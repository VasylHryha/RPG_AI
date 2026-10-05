"""Thin ctypes access to ABI v1. Run build.py before loading; never auto-build.

    with World('remember', 12, namespace='dev') as episode:
        with Policy('remember', 12, kind='reference') as policy:
            while not episode.observe().done:
                episode.step(policy.action(episode.observe()))
            print(episode.score().as_dict())

Angles are radians. magnitude estimates distance for perceive, and supplies
normalized speed for motion tasks. choose/focus_fire also require choice=id.
Invalid actions raise InvalidAction; the native counter still records rejection.
"""
import ctypes as C
from enum import IntEnum
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
TASKS = ("perceive", "move", "remember", "choose", "chase", "pursuit", "focus_fire",
         "remember_static")
NAMESPACES = ("dev", "validation", "judging")


class Status(IntEnum):
    OK = 0
    BAD_ARGUMENT = 1
    JUDGING_DENIED = 2
    BAD_ACTION = 3
    EPISODE_DONE = 4


class WorldError(ValueError):
    def __init__(self, status):
        self.status = Status(status)
        super().__init__(self.status.name)


class InvalidAction(WorldError):
    pass


def _check(status):
    if status:
        raise (InvalidAction if status == Status.BAD_ACTION else WorldError)(status)


class Values(C.Structure):
    def as_dict(self):
        return {name: getattr(self, name) for name, *_ in self._fields_}


class Enemy(Values):
    _fields_ = [(name, C.c_int32) for name in ("id", "visible")] + [
        (name, C.c_double) for name in ("dx", "dy", "angle", "distance", "vx", "vy", "hp")]


class Observation(Values):
    _fields_ = [(name, C.c_int32) for name in
                ("task", "step", "horizon", "done", "enemy_count", "mode")] + [
        (name, C.c_double) for name in
        ("dt", "half_size", "agent_x", "agent_y", "target_angle", "target_distance",
         "desired_range", "occluder_xmin", "occluder_xmax", "occluder_ymin", "occluder_ymax")
    ] + [("enemies", Enemy * 8)]

    def as_dict(self):
        result = super().as_dict()
        result["enemies"] = [e.as_dict() for e in self.enemies[:self.enemy_count]]
        return result


class Action(Values):
    _fields_ = [("angle", C.c_double), ("magnitude", C.c_double), ("choice", C.c_int32)]

    def __init__(self, angle=0.0, magnitude=0.0, choice=-1):
        if isinstance(choice, bool) or not isinstance(choice, int) or not -(2**31) <= choice < 2**31:
            raise ValueError("choice must be an int32, without truncation")
        super().__init__(angle, magnitude, choice)


class Score(Values):
    _fields_ = [(name, C.c_int32) for name in ("steps", "hidden_steps", "invalid_actions", "done")] + [
        (name, C.c_double) for name in
        ("angular_error", "distance_error", "goal_error", "settle_seconds",
         "correct_choice_rate", "damage_per_second", "in_range_rate")]


class Evaluation(Values):
    _fields_ = [("episodes", C.c_int32), ("mean", Score)]

    def as_dict(self):
        return {"episodes": self.episodes, "mean": self.mean.as_dict()}


def _index(value, names):
    if isinstance(value, str):
        if value not in names:
            raise ValueError(f"expected one of {names}")
        return names.index(value)
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < len(names):
        raise ValueError(f"invalid index for {names}")
    return value


def _seed(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < 2**64:
        raise ValueError("seed must be uint64, without truncation")
    return value


def _flags(allow_judging):
    if not isinstance(allow_judging, bool):
        raise ValueError("allow_judging must be an explicit bool")
    return int(allow_judging)


class Library:
    """Share the immutable library binding; each World/Policy owns its own state."""
    def __init__(self):
        build_dir = ROOT / "_build"
        manifest = json.loads((build_dir / "build.json").read_text())
        for name, expected in manifest["source_sha256"].items():
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
                raise RuntimeError(f"stale native build: {name}; run build.py")
        filename = "libgs_world.dylib" if sys.platform == "darwin" else "libgs_world.so"
        if hashlib.sha256((build_dir / filename).read_bytes()).hexdigest() != manifest["binary_sha256"][filename]:
            raise RuntimeError("native binary identity mismatch; run build.py")
        self.api = C.CDLL(str(build_dir / filename))
        specs = {
            "gs_abi_version": (C.c_int32, []),
            "gs_struct_size": (C.c_uint32, [C.c_int32]),
            "gs_create": (C.c_int32, [C.c_int32, C.c_int32, C.c_uint64, C.c_uint32, C.POINTER(C.c_void_p)]),
            "gs_destroy": (None, [C.c_void_p]),
            "gs_observe": (C.c_int32, [C.c_void_p, C.POINTER(Observation)]),
            "gs_step": (C.c_int32, [C.c_void_p, C.POINTER(Action)]),
            "gs_score": (C.c_int32, [C.c_void_p, C.POINTER(Score)]),
            "gs_seed_tag": (C.c_int32, [C.c_void_p, C.POINTER(C.c_uint64)]),
            "gs_policy_create": (C.c_int32, [C.c_int32, C.c_int32, C.c_uint64, C.c_int32, C.c_uint32,
                                             C.POINTER(C.c_void_p)]),
            "gs_policy_destroy": (None, [C.c_void_p]),
            "gs_policy_action": (C.c_int32, [C.c_void_p, C.POINTER(Observation), C.POINTER(Action)]),
            "gs_evaluate": (C.c_int32, [C.c_int32, C.c_int32, C.c_uint64, C.c_int32, C.c_int32,
                                      C.c_uint32, C.POINTER(Evaluation)]),
        }
        for name, (result, arguments) in specs.items():
            function = getattr(self.api, name)
            function.restype, function.argtypes = result, arguments
        if self.api.gs_abi_version() != 1:
            raise RuntimeError("unsupported world ABI")
        for i, struct in enumerate((Observation, Action, Score, Evaluation, Enemy)):
            if self.api.gs_struct_size(i) != C.sizeof(struct):
                raise RuntimeError(f"ABI layout mismatch: {struct.__name__}")

    def evaluate(self, task, first_seed, episodes, kind="reference", namespace="dev", *, allow_judging=False):
        if isinstance(episodes, bool) or not isinstance(episodes, int) or not 1 <= episodes <= 1_000_000:
            raise ValueError("episodes must be in [1,1000000]")
        result = Evaluation()
        _check(self.api.gs_evaluate(_index(task, TASKS), _index(namespace, NAMESPACES),
                                   _seed(first_seed), episodes, _index(kind, ("reference", "random")),
                                   _flags(allow_judging), C.byref(result)))
        return result


class _Handle:
    def _open(self):
        if not self._handle:
            raise RuntimeError("closed handle")

    def close(self):
        if getattr(self, "_handle", None):
            getattr(self.library.api, self._destroy)(self._handle)
            self._handle = C.c_void_p()

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()


class World(_Handle):
    _destroy = "gs_destroy"

    def __init__(self, task, seed, namespace="dev", *, allow_judging=False, library=None):
        self.library = library if library is not None else Library()
        self._handle = C.c_void_p()
        _check(self.library.api.gs_create(_index(task, TASKS), _index(namespace, NAMESPACES),
                                         _seed(seed), _flags(allow_judging), C.byref(self._handle)))

    def observe(self):
        self._open()
        result = Observation()
        _check(self.library.api.gs_observe(self._handle, C.byref(result)))
        return result

    def step(self, action):
        self._open()
        if not isinstance(action, Action):
            raise TypeError("step requires an Action")
        _check(self.library.api.gs_step(self._handle, C.byref(action)))

    def score(self):
        self._open()
        result = Score()
        _check(self.library.api.gs_score(self._handle, C.byref(result)))
        return result

    @property
    def seed_tag(self):
        self._open()
        result = C.c_uint64()
        _check(self.library.api.gs_seed_tag(self._handle, C.byref(result)))
        return result.value


class Policy(_Handle):
    _destroy = "gs_policy_destroy"

    def __init__(self, task, seed, kind="reference", namespace="dev", *, allow_judging=False, library=None):
        self.library = library if library is not None else Library()
        self._handle = C.c_void_p()
        _check(self.library.api.gs_policy_create(_index(task, TASKS), _index(namespace, NAMESPACES),
                                                _seed(seed), _index(kind, ("reference", "random")),
                                                _flags(allow_judging), C.byref(self._handle)))

    def action(self, observation):
        self._open()
        if not isinstance(observation, Observation):
            raise TypeError("policy requires an Observation")
        result = Action()
        _check(self.library.api.gs_policy_action(self._handle, C.byref(observation), C.byref(result)))
        return result
