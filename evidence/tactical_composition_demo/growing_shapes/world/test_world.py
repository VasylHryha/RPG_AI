"""Engine contracts only: no learning, growth, recorded panel or judging access."""
import math
from concurrent.futures import ThreadPoolExecutor
import json
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest
from world import (Action, InvalidAction, Library, Observation, Policy,
                   Status, TASKS, World, WorldError)


@pytest.fixture(scope="module")
def library():
    return Library()


def rollout(library, task, seed, kind="reference", namespace="dev"):
    observations = []
    with World(task, seed, namespace, library=library) as w, Policy(
            task, seed, kind, namespace, library=library) as p:
        while not w.observe().done:
            o = w.observe()
            observations.append(o.as_dict())
            w.step(p.action(o))
        return observations, w.score().as_dict()


@pytest.mark.parametrize("task", TASKS)
@pytest.mark.parametrize("kind", ("reference", "random"))
def test_determinism_interleaved_and_parallel(library, task, kind):
    expected = rollout(library, task, 317, kind)
    # A different intervening task cannot perturb any random stream or memory.
    rollout(library, "remember", 91, "random")
    assert rollout(library, task, 317, kind) == expected
    with ThreadPoolExecutor(max_workers=2) as pool:
        runs = list(pool.map(lambda _: rollout(library, task, 317, kind), range(2)))
    assert runs == [expected, expected]


@pytest.mark.parametrize("task", TASKS)
def test_generator_statistics(library, task):
    observations = []
    for seed in range(512):
        with World(task, seed, library=library) as w:
            observations.append(w.observe())
    assert all(o.dt == 0.1 and o.horizon == 160 and o.half_size == 10 for o in observations)
    assert all(o.step == 0 and not o.done for o in observations)
    if task == "move":
        keeps = [o for o in observations if o.mode == 1]
        assert 0.4 < len(keeps) / 512 < 0.6
        inside = [o for o in keeps if o.target_distance < o.desired_range]
        assert 0.35 < len(inside) / len(keeps) < 0.65
        assert all(1.5 <= o.desired_range <= 3.5 for o in keeps)
        assert all(4 <= o.target_distance <= 8 for o in observations if o.mode == 0)
        assert abs(sum(math.cos(o.target_angle) for o in observations) / 512) < 0.12
        assert abs(sum(math.sin(o.target_angle) for o in observations) / 512) < 0.12
        return
    if task == "pursuit":
        assert all(o.enemy_count == 1 and o.enemies[0].visible for o in observations)
        assert all(0.55 <= o.enemies[0].vx <= 0.85 and o.enemies[0].vy == 0 for o in observations)
        return
    if task == "remember":
        assert all(o.enemy_count == 1 for o in observations)
    else:
        assert set(o.enemy_count for o in observations) == set(range(3, 9))
        assert 5.2 < sum(o.enemy_count for o in observations) / 512 < 5.8
    enemies = [e for o in observations for e in o.enemies[:o.enemy_count]]
    assert all(e.visible and -10 <= o.agent_x + e.dx <= 10 and -10 <= o.agent_y + e.dy <= 10
               for o in observations for e in o.enemies[:o.enemy_count])
    assert abs(sum(math.cos(e.angle) for e in enemies) / len(enemies)) < 0.12
    assert abs(sum(math.sin(e.angle) for e in enemies) / len(enemies)) < 0.12
    assert all(10 <= e.hp <= 100 for e in enemies)
    if task in ("perceive", "remember", "chase"):
        assert all(0.25 <= math.hypot(e.vx, e.vy) <= 0.65 + 1e-14 for e in enemies)
    else:
        assert all(e.vx == e.vy == 0 for e in enemies)
    if task == "choose":
        inside_fraction = sum(any(e.distance <= o.desired_range for e in o.enemies[:o.enemy_count])
                              for o in observations) / 512
        assert 0.4 < inside_fraction < 0.6


@pytest.mark.parametrize("task", TASKS)
@pytest.mark.parametrize("namespace", ("dev", "validation"))
def test_reference_margin(library, task, namespace):
    # Reuse the measured rollouts instead of rerunning this comparison.
    scores = json.loads((Path(__file__).parent / "WORLD_CHECKS.json").read_text())["scores"][namespace][task]
    ref = SimpleNamespace(**scores["reference"]["mean"])
    rnd = SimpleNamespace(**scores["random"]["mean"])
    assert ref.done and rnd.done and ref.steps == rnd.steps == 160
    assert ref.invalid_actions == rnd.invalid_actions == 0
    if task == "perceive":
        assert ref.angular_error < 1e-10 and rnd.angular_error > 1.4
        assert ref.distance_error < 1e-10 and rnd.distance_error > 8
    elif task == "remember":
        assert ref.hidden_steps == rnd.hidden_steps == 120
        assert ref.angular_error < 1e-10 and rnd.angular_error > 1.4
    elif task == "choose":
        assert ref.correct_choice_rate == 1 and rnd.correct_choice_rate < 0.3
    elif task == "focus_fire":
        assert ref.damage_per_second > 0.75
        assert ref.damage_per_second > rnd.damage_per_second + 0.6
    else:
        assert ref.goal_error < rnd.goal_error * 0.25
        assert ref.in_range_rate > rnd.in_range_rate + 0.5
        if task == "move":
            assert ref.settle_seconds < 2.5 and rnd.settle_seconds > 12


@pytest.mark.parametrize("task", TASKS)
def test_invalid_actions_are_counted_not_repaired(library, task):
    choice = 0 if task in ("choose", "focus_fire") else -1
    limit = math.sqrt(800) if task == "perceive" else 1
    bad = [Action(float("nan"), 0, choice), Action(float("inf"), 0, choice),
           Action(math.pi + 0.01, 0, choice), Action(-math.pi - 0.01, 0, choice),
           Action(0, -0.01, choice), Action(0, limit + 0.01, choice),
           Action(0, float("nan"), choice), Action(0, float("inf"), choice),
           Action(0, 0, 200), Action(0, 0, -2),
           Action(0, 0, -1 if choice == 0 else 0)]
    with World(task, 12, library=library) as w:
        before = w.observe().as_dict()
        before_score = w.score().as_dict()
        for count, action in enumerate(bad, 1):
            with pytest.raises(InvalidAction) as error:
                w.step(action)
            assert error.value.status == Status.BAD_ACTION
            assert w.observe().as_dict() == before
            score = w.score().as_dict()
            assert score.pop("invalid_actions") == count
            assert score == {k: v for k, v in before_score.items() if k != "invalid_actions"}
        # Same physics boundary action remains valid, never counted as a fix.
        w.step(Action(math.pi, limit, choice))
        assert w.score().steps == 1 and w.score().invalid_actions == len(bad)
    with pytest.raises(RuntimeError, match="closed"):
        w.observe()
    w.close()  # idempotent


@pytest.mark.parametrize("task", TASKS)
def test_namespace_and_task_separation(library, task):
    with World(task, 23, "dev", library=library) as a, World(task, 23, "validation", library=library) as b:
        assert a.seed_tag != b.seed_tag
        assert a.observe().as_dict() != b.observe().as_dict()
    for constructor in (World, Policy):
        with pytest.raises(WorldError) as error:
            constructor(task, 23, namespace="judging", library=library)
        assert error.value.status == Status.JUDGING_DENIED
    with pytest.raises(WorldError) as error:
        library.evaluate(task, 23, 1, namespace="judging")
    assert error.value.status == Status.JUDGING_DENIED
    with World(task, 23, library=library) as a, World(task, 24, library=library) as b:
        assert a.seed_tag != b.seed_tag


def test_seed_identity_is_task_specific(library):
    tags = []
    for task in TASKS:
        with World(task, 7, library=library) as w:
            tags.append(w.seed_tag)
    assert len(set(tags)) == len(TASKS)


@pytest.mark.parametrize("seed", (-1, 2**64, 1.2, True))
def test_python_rejects_truncation(library, seed):
    with pytest.raises(ValueError):
        World("move", seed, library=library)


@pytest.mark.parametrize("choice", (2**31, -2**31 - 1, 1.2, True))
def test_choice_rejects_truncation(choice):
    with pytest.raises(ValueError):
        Action(choice=choice)


def test_other_validation_and_done(library):
    for task in ("unknown", -1, 7, 2**32, True):
        with pytest.raises(ValueError):
            World(task, 0, library=library)
    with pytest.raises(ValueError):
        World("move", 0, "unknown", library=library)
    with pytest.raises(ValueError):
        World("move", 0, allow_judging=1, library=library)
    with pytest.raises(ValueError):
        library.evaluate("move", 0, 2**32)
    assert library.api.gs_observe(None, None) == Status.BAD_ARGUMENT
    assert library.api.gs_step(None, None) == Status.BAD_ARGUMENT
    with World("move", 0, library=library) as w:
        for _ in range(160):
            w.step(Action())
        assert w.observe().done
        with pytest.raises(WorldError) as error:
            w.step(Action())
        assert error.value.status == Status.EPISODE_DONE
        assert w.score().steps == 160 and w.score().invalid_actions == 0


@pytest.mark.parametrize("task", ("remember", "pursuit"))
def test_hidden_redaction_and_causal_memory(library, task):
    # Change ALL hidden value slots in a copied observation. The reference must
    # ignore them, using its own earlier observations and elapsed time only.
    with World(task, 55, library=library) as w, Policy(task, 55, library=library) as p, Policy(
            task, 55, library=library) as q:
        hidden = 0
        for _ in range(160):
            o = w.observe()
            poisoned = Observation.from_buffer_copy(o)
            for i in range(o.enemy_count):
                if not o.enemies[i].visible:
                    hidden += 1
                    e = o.enemies[i]
                    assert all(getattr(e, field) == 0 for field in
                               ("dx", "dy", "angle", "distance", "vx", "vy", "hp"))
                    for field in ("dx", "dy", "angle", "distance", "vx", "vy", "hp"):
                        setattr(poisoned.enemies[i], field, 123456.0)
            a, b = p.action(o), q.action(poisoned)
            assert a.as_dict() == b.as_dict()
            w.step(a)
        assert hidden > 30
        if task == "remember":
            assert hidden == 120


def test_manual_perception_score_and_clamping_physics(library):
    with World("perceive", 3, library=library) as w:
        o = w.observe()
        target = min(o.enemies[:o.enemy_count], key=lambda e: (e.distance, e.id))
        a = Action(math.remainder(target.angle + 0.5, 2 * math.pi), target.distance + 1)
        w.step(a)
        score = w.score()
        assert score.angular_error == pytest.approx(0.5)
        assert score.distance_error == pytest.approx(1)
        assert w.observe().agent_x == o.agent_x and w.observe().agent_y == o.agent_y
    with World("move", 3, library=library) as w:
        for _ in range(160):
            w.step(Action(0, 1))
        assert w.observe().agent_x == 10
        assert w.score().invalid_actions == 0


def test_choose_score_from_independent_observation_rule(library):
    for seed in range(32):
        with World("choose", seed, library=library) as w:
            o = w.observe()
            enemies = list(o.enemies[:o.enemy_count])
            candidates = [e for e in enemies if e.distance <= o.desired_range]
            winner = min(candidates, key=lambda e: (e.hp, e.id)) if candidates else min(
                enemies, key=lambda e: (e.distance, e.id))
            for e in enemies:
                w.step(Action(choice=e.id))
            assert w.score().correct_choice_rate == pytest.approx(1 / o.enemy_count)
            # A fresh episode verifies this exact predicted winner scores 1.
        with World("choose", seed, library=library) as w:
            w.step(Action(choice=winner.id))
            assert w.score().correct_choice_rate == 1


def test_move_goal_and_settle_from_public_trajectory(library):
    with World("move", 99, library=library) as w, Policy("move", 99, library=library) as p:
        errors = []
        for _ in range(160):
            w.step(p.action(w.observe()))
            o = w.observe()
            errors.append(abs(o.target_distance - o.desired_range))
        score = w.score()
        assert score.goal_error == pytest.approx(sum(errors) / 160)
        starts = [i for i in range(151) if all(e <= 0.25 for e in errors[i:i+10])]
        assert starts
        assert score.settle_seconds == pytest.approx((starts[0] + 1) * 0.1)


def test_focus_damage_requires_selected_target_range(library):
    with World("focus_fire", 2, library=library) as w, Policy("focus_fire", 2, library=library) as p:
        initial_hp = sum(e.hp for e in w.observe().enemies[:w.observe().enemy_count])
        for _ in range(160):
            o = w.observe()
            a = p.action(o)
            w.step(a)
            after = w.observe()
            for i in range(o.enemy_count):
                drop = o.enemies[i].hp - after.enemies[i].hp
                if i == a.choice and after.enemies[i].distance <= after.desired_range:
                    assert drop == pytest.approx(0.1)
                else:
                    assert drop == 0
        final_hp = sum(e.hp for e in after.enemies[:after.enemy_count])
        assert w.score().damage_per_second == pytest.approx((initial_hp-final_hp)/16)


def test_native_batch_equals_python_loop(library):
    for task in TASKS:
        score = rollout(library, task, 7)[1]
        assert library.evaluate(task, 7, 1).mean.as_dict() == score


def test_scores_and_speed_receipt():
    # Emitted once by verify_world.py before pytest; pytest does not replay it.
    receipt = json.loads((Path(__file__).parent / "WORLD_CHECKS.json").read_text())
    assert receipt["status"] in ("PENDING_TESTS", "PASS")
    assert receipt["scope"] == "engine verification only; no judging, growth or learning"
    for name, expected in receipt["source_sha256"].items():
        assert hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest() == expected
    assert receipt["benchmark"]["optimized"]
    assert all(m["episodes_per_second"] >= 2000 for m in receipt["benchmark"]["native"].values())
