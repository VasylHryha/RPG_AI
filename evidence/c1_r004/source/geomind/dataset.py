"""Evaluator-owned worlds. Only World.observation may reach the candidate."""

from dataclasses import dataclass

import numpy as np

from .geometry import Constraint, Observation

GENERATOR_VERSION = "c0-worlds.v2"


@dataclass(frozen=True)
class World:
    observation: Observation
    truth: dict
    queries: tuple
    hidden_edges: tuple
    cross_component_queries: tuple


def generate(seed, arm, node_count=32, query_count=64):
    if arm not in ("lattice", "continuous", "disconnected", "inconsistent", "noisy"):
        raise ValueError("Unknown arm")
    if type(seed) is not int or seed < 0 or type(node_count) is not int or node_count < 16 or type(query_count) is not int or query_count < 1:
        raise ValueError("Nonnegative seed, at least 16 nodes and positive query count required")
    rng = np.random.default_rng(seed)
    ids = [f"u{v:04d}" for v in rng.permutation(node_count)]
    original_ids = list(ids)
    groups = [list(range(node_count))] if arm != "disconnected" else [list(range(node_count // 2)), list(range(node_count // 2, node_count))]
    positions = np.zeros((node_count, 2))
    tree, redundant, pairs = [], [], set()

    def make_edge(i, j):
        return Constraint(ids[i], ids[j], tuple(positions[j] - positions[i]))

    for group in groups:
        # Tree built before redundant constraints: hiding the latter cannot lose identifiability.
        positions[group[0]] = rng.integers(-10, 11, 2)
        for k, j in enumerate(group[1:], 1):
            i = group[int(rng.integers(0, k))]
            offset = rng.normal(size=2) if arm in ("continuous", "noisy") else np.array(((1, 0), (-1, 0), (0, 1), (0, -1)))[rng.integers(4)]
            positions[j] = positions[i] + offset
            tree.append(make_edge(i, j))
            pairs.add(tuple(sorted((i, j))))
        options = [(i, j) for i in group for j in group if i < j and (i, j) not in pairs]
        rng.shuffle(options)
        for i, j in options[:len(group)]:
            redundant.append(make_edge(i, j))
    rng.shuffle(redundant)
    hidden = tuple(redundant[:8])
    exposed = list(tree) + redundant[8:]
    if arm == "inconsistent":
        edge = exposed[-1]
        exposed[-1] = Constraint(edge.source, edge.target, (edge.offset[0] + 0.7, edge.offset[1] - 0.4))
    elif arm == "noisy":
        exposed = [Constraint(e.source, e.target, tuple(np.asarray(e.offset) + rng.normal(0, 0.05, 2))) for e in exposed]
    vectors = sorted({e.offset for e in exposed})
    vector_names = {vector: f"r{i:04d}" for i, vector in enumerate(vectors)}
    catalog = tuple((vector_names[v], v) for v in vectors)
    exposed = [Constraint(e.source, e.target, e.offset, e.weight, vector_names[e.offset]) for e in exposed]
    supplied = {frozenset((e.source, e.target)) for e in exposed}
    possible = [(ids[i], ids[j]) for group in groups for i in group for j in group if i < j and frozenset((ids[i], ids[j])) not in supplied]
    rng.shuffle(possible)
    hidden_pairs = [tuple(sorted((e.source, e.target))) for e in hidden]
    remaining = [tuple(sorted(pair)) for pair in possible if tuple(sorted(pair)) not in hidden_pairs]
    if query_count < len(hidden_pairs) or query_count > len(hidden_pairs) + len(remaining):
        raise ValueError("Query budget must cover all hidden edges and fit available indirect pairs")
    queries = tuple(hidden_pairs + remaining[:query_count - len(hidden_pairs)])
    cross = tuple((ids[i], ids[j]) for i in groups[0][:4] for j in groups[1][:4]) if arm == "disconnected" else ()
    rng.shuffle(ids)  # Observation order unrelated to traversal order or coordinates.
    return World(Observation(tuple(ids), tuple(exposed), catalog), dict(zip(original_ids, map(tuple, positions))), queries, hidden, cross)
