"""Evaluator-owned C1 panel and explicitly compiled public initialization."""

from dataclasses import asdict, dataclass, replace
import json
from time import perf_counter

import numpy as np

from .geometry import Constraint, GeometryState, Observation, Settings, _prepare, canonical, digest
from .references import CompiledCoordinates

GENERATOR = "c1-jittered-grid-interventions.v3"
KINDS = ("consistent_edge", "inconsistent_edge", "new_node", "bridge")


@dataclass(frozen=True)
class Case:
    base: Observation
    updated: Observation
    queries: tuple
    retention_queries: tuple
    affected_queries: tuple
    truth: dict


def _with_relations(base, edges):
    catalog = dict(base.relations)
    by_vector = {vector: name for name, vector in base.relations}
    result = list(base.edges)
    for edge in edges:
        if edge.offset not in by_vector:
            name = f"r{len(catalog):06d}"
            while name in catalog:
                name += "x"
            by_vector[edge.offset] = name
            catalog[name] = edge.offset
        result.append(replace(edge, relation_id=by_vector[edge.offset]))
    return tuple(result), tuple(sorted(catalog.items()))


def generate_case(node_count, kind, seed):
    """Seed-varied worlds: R002 seeds only relabeled one fixed geometry.

    Each seed draws grid widths, continuous position jitter, consistent chord
    cycles, intervention endpoints and the contradiction vector. Component
    roles stay fixed: the third component is never touched.
    """
    if type(node_count) is not int or node_count < 16 or node_count % 4 or kind not in KINDS or type(seed) is not int or seed < 0:
        raise ValueError("C1 case requires a size divisible by four, valid kind and nonnegative seed")
    rng = np.random.default_rng(seed)
    names = [f"u{v:06d}" for v in rng.permutation(node_count)]
    sizes = (node_count // 2, node_count // 4, node_count // 4)
    groups, positions, raw_edges = [], {}, []
    cursor = 0
    for group_id, size in enumerate(sizes):
        group = names[cursor:cursor + size]
        cursor += size
        groups.append(group)
        root = np.sqrt(size)
        width = int(rng.integers(max(2, int(root / 2)), max(3, int(2 * root)) + 1))
        for i, node in enumerate(group):
            jitter = np.round(rng.uniform(-0.25, 0.25, 2), 6)
            positions[node] = (float(i % width + 10 * group_id * root + jitter[0]), float(i // width + jitter[1]))
        for i, node in enumerate(group):
            if i % width:
                raw_edges.append(Constraint(group[i - 1], node, tuple(np.asarray(positions[node]) - positions[group[i - 1]])))
            if i >= width:
                raw_edges.append(Constraint(group[i - width], node, tuple(np.asarray(positions[node]) - positions[group[i - width]])))
        # Consistent chords add base cycles without contradicting saved geometry.
        for _ in range(size // 8):
            x, y = (str(v) for v in rng.choice(group, 2, replace=False))
            raw_edges.append(Constraint(x, y, tuple(np.asarray(positions[y]) - positions[x])))
    empty = Observation(tuple(sorted(names)), ())
    edges, relations = _with_relations(empty, raw_edges)
    base = Observation(tuple(sorted(names)), edges, relations)
    a, b = (str(v) for v in rng.choice(groups[0], 2, replace=False))
    vector = tuple(np.asarray(positions[b]) - positions[a])
    nodes = base.nodes
    if kind == "consistent_edge":
        added = Constraint(a, b, vector)
    elif kind == "inconsistent_edge":
        angle = rng.uniform(0, 2 * np.pi)
        error = rng.uniform(0.2, 1.0) * np.array([np.cos(angle), np.sin(angle)])
        added = Constraint(a, b, tuple(np.asarray(vector) + error))
    elif kind == "new_node":
        b = "new-unit"
        nodes = tuple(sorted(nodes + (b,)))
        offset = tuple(np.round(rng.uniform(-1, 1, 2), 6))
        positions[b] = tuple(np.asarray(positions[a]) + offset)
        added = Constraint(a, b, offset)
    else:
        b = str(rng.choice(groups[1]))
        added = Constraint(a, b, tuple(np.asarray(positions[b]) - positions[a]))
    edges, relations = _with_relations(base, (added,))
    updated = Observation(nodes, edges, relations)
    queries = {(a, b)}
    for group in groups:
        for _ in range(20):
            x, y = rng.choice(group, 2, replace=False)
            queries.add((str(x), str(y)))
    if kind == "bridge":
        for _ in range(20):
            queries.add((str(rng.choice(groups[0])), str(rng.choice(groups[1]))))
    if kind == "new_node":
        queries.update((str(rng.choice(groups[0])), b) for _ in range(10))
    # These pairs must remain unidentifiable after every intervention.
    for _ in range(10):
        queries.add((str(rng.choice(groups[0])), str(rng.choice(groups[2]))))
    # Third component is truly disconnected from every intervention.
    retention = tuple((groups[2][0], node) for node in groups[2][1:])
    affected = tuple((groups[0][0], node) for node in groups[0][-min(8, len(groups[0]) - 1):])
    return Case(base, updated, tuple(sorted(queries)), retention, affected, positions)


def save_initial_state(observation, manifest_hash, settings=Settings()):
    """Shared exact initializer derived only from public offsets, fully charged."""
    started = perf_counter()
    reference = CompiledCoordinates(observation)
    if reference.residual_max > 1e-10:
        raise ValueError("Compiled initialization requires consistent constraints")
    nodes, index, edges, source, target, offsets, weights, degree, components, anchors = _prepare(observation)
    coordinates = np.array([reference.coordinates[node] for node in nodes])
    origins = [coordinates[a].copy() for a in anchors]
    for i, component in enumerate(components):
        coordinates[i] -= origins[component]
    payload = {"schema": GeometryState.schema, "algorithm": GeometryState.algorithm,
               "settings": asdict(settings), "training_manifest_hash": manifest_hash,
               "nodes": list(nodes), "edges": [asdict(e) for e in edges], "relations": observation.relations,
               "components": components, "anchors": anchors, "coordinates": coordinates.tolist(), "frozen": True}
    encoded = canonical(dict(payload, checksum=digest(payload)))
    loaded = GeometryState.load(encoded)
    if loaded.export() != encoded:
        raise ValueError("Saved initialization did not round-trip")
    return encoded, {"source": "compiled public constraints; shared exact warm state, not candidate learning",
                     "compile_seconds": reference.build_seconds, "compile_edge_visits": reference.edge_visits,
                     "certify_serialize_seconds": perf_counter() - started - reference.build_seconds,
                     "total_seconds": perf_counter() - started, "serialized_bytes": len(encoded.encode())}
