"""Transactional C0 state. Exposed constraints only; no evaluator dependency."""

from dataclasses import asdict, dataclass
import hashlib
import json
import numbers
import re
from time import perf_counter
from typing import Optional, Tuple

import numpy as np


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def finite_number(value):
    return isinstance(value, numbers.Real) and not isinstance(value, (bool, np.bool_)) and np.isfinite(value)


def valid_hash(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


@dataclass(frozen=True)
class Constraint:
    source: str
    target: str
    offset: Tuple[float, float]
    weight: float = 1.0
    relation_id: Optional[str] = None


@dataclass(frozen=True)
class Observation:
    nodes: Tuple[str, ...]
    edges: Tuple[Constraint, ...]
    # Public per-world relation manifest: opaque ID -> exact numeric vector.
    relations: tuple = ()

    def validate(self):
        if not isinstance(self.nodes, tuple) or not isinstance(self.edges, tuple) or not isinstance(self.relations, tuple):
            raise ValueError("Observation containers must be immutable tuples")
        if not self.nodes or any(not isinstance(n, str) or not n for n in self.nodes) or len(set(self.nodes)) != len(self.nodes):
            raise ValueError("Nonempty unique string node IDs required")
        catalog = {}
        for entry in self.relations:
            if not isinstance(entry, tuple) or len(entry) != 2:
                raise ValueError("Invalid relation manifest entry")
            name, vector = entry
            if not isinstance(name, str) or not name or name in catalog or not isinstance(vector, tuple) or len(vector) != 2 or not all(finite_number(v) for v in vector):
                raise ValueError("Invalid relation manifest")
            catalog[name] = vector
        known = set(self.nodes)
        for edge in self.edges:
            if not isinstance(edge, Constraint) or not isinstance(edge.source, str) or not isinstance(edge.target, str):
                raise ValueError("Invalid constraint record")
            if edge.source not in known or edge.target not in known or edge.source == edge.target:
                raise ValueError("Dangling or self constraint")
            if not isinstance(edge.offset, tuple) or len(edge.offset) != 2 or not all(finite_number(v) for v in edge.offset):
                raise ValueError("Finite immutable 2D offsets required")
            if not finite_number(edge.weight) or edge.weight <= 0:
                raise ValueError("Positive finite weights required")
            if edge.relation_id is not None and (not isinstance(edge.relation_id, str) or catalog.get(edge.relation_id) != edge.offset):
                raise ValueError("Relation ID/vector mismatch")
            if catalog and edge.relation_id is None:
                raise ValueError("All manifest-backed constraints require relation IDs")


@dataclass(frozen=True)
class Settings:
    step_factor: float = 0.25
    max_sweeps: int = 10000
    gradient_tolerance: float = 1e-8
    update_tolerance: float = 1e-8
    stable_sweeps: int = 10

    def validate(self):
        if not finite_number(self.step_factor) or not 0 < self.step_factor <= 0.25:
            raise ValueError("Invalid step factor")
        if any(type(v) is not int or v < 1 for v in (self.max_sweeps, self.stable_sweeps)):
            raise ValueError("Positive integer sweep budgets required")
        if any(not finite_number(v) or v <= 0 for v in (self.gradient_tolerance, self.update_tolerance)):
            raise ValueError("Invalid stopping tolerance")


@dataclass(frozen=True)
class Answer:
    status: str
    displacement: Optional[Tuple[float, float]] = None


def _prepare(observation):
    observation.validate()
    nodes = tuple(sorted(observation.nodes))
    index = {node: i for i, node in enumerate(nodes)}
    edges = tuple(sorted(observation.edges, key=lambda e: (e.source, e.target, e.offset, e.weight, e.relation_id or "")))
    n = len(nodes)
    source = np.array([index[e.source] for e in edges], dtype=np.int64)
    target = np.array([index[e.target] for e in edges], dtype=np.int64)
    offsets = np.array([e.offset for e in edges], dtype=np.float64).reshape(-1, 2)
    weights = np.array([e.weight for e in edges], dtype=np.float64)
    degree = np.bincount(source, weights=weights, minlength=n) + np.bincount(target, weights=weights, minlength=n)
    if not np.isfinite(degree).all():
        raise ValueError("Weighted degree overflow")
    adjacency = [[] for _ in nodes]
    for i, j in zip(source, target):
        adjacency[i].append(j)
        adjacency[j].append(i)
    components = [-1] * n
    anchors = []
    for root in range(n):
        if components[root] != -1:
            continue
        component = len(anchors)
        anchor = root
        components[root] = component
        stack = [root]
        while stack:
            node = stack.pop()
            if (degree[node], -node) > (degree[anchor], -anchor):
                anchor = node
            for neighbor in adjacency[node]:
                if components[neighbor] == -1:
                    components[neighbor] = component
                    stack.append(neighbor)
        anchors.append(int(anchor))
    return nodes, index, edges, source, target, offsets, weights, degree, components, anchors


def _gradient(coordinates, source, target, offsets, weights, anchors):
    residual = coordinates[target] - coordinates[source] - offsets
    force = weights[:, None] * residual
    gradient = np.column_stack([
        np.bincount(target, weights=force[:, axis], minlength=len(coordinates))
        - np.bincount(source, weights=force[:, axis], minlength=len(coordinates))
        for axis in range(2)
    ])
    gradient[anchors] = 0
    return residual, force, gradient


class GeometryState:
    schema = "geomind.c0.geometry.v2"
    algorithm = "synchronous-local-relaxation.v2"

    def __init__(self, settings=Settings()):
        settings.validate()
        self._settings = settings
        self._snapshot = None
        self._index = {}
        self._frozen = False
        self._last_failure = "INVALID_STATE"

    @property
    def settings(self):
        return self._settings

    def learn(self, observation, training_manifest_hash):
        if self._frozen:
            raise RuntimeError("Frozen geometry cannot learn")
        started = perf_counter()
        trace = {"status": "INVALID_STATE", "sweeps": 0, "energy": None, "residual_max": None, "gradient_max": None, "update_max": None, "fallbacks": 0}
        try:
            if not isinstance(observation, Observation) or not valid_hash(training_manifest_hash):
                raise ValueError("Typed observation and SHA256 manifest identity required")
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                nodes, index, edges, source, target, offsets, weights, degree, components, anchors = _prepare(observation)
                alpha = self.settings.step_factor / max(1.0, float(degree.max()))
                coordinates = np.zeros((len(nodes), 2), dtype=np.float64)
                local_scale = np.where(degree > 0, degree, 1.0)
                trace["preprocessing_seconds"] = perf_counter() - started
                trace["preprocessing_work"] = {
                    "validation_edge_records": len(edges), "array_edge_records": 4 * len(edges),
                    "adjacency_edge_records": len(edges), "component_neighbor_visits": 2 * len(edges),
                    "degree_endpoint_accumulations": 2 * len(edges), "anchor_node_visits": len(nodes),
                    "sort_items": len(edges) + len(nodes), "sort_comparisons": "not instrumented; included in preprocessing time",
                }
                stable = 0
                dynamics_started = perf_counter()
                for sweep in range(1, self.settings.max_sweeps + 1):
                    residual, edge_force, gradient = _gradient(coordinates, source, target, offsets, weights, anchors)
                    delta = -alpha * gradient
                    gradient_max = float(np.linalg.norm(gradient, axis=1).max())
                    normalized_gradient_max = float(np.linalg.norm(gradient / local_scale[:, None], axis=1).max())
                    update_max = float(np.linalg.norm(delta, axis=1).max())
                    coordinates += delta
                    if not np.isfinite(coordinates).all():
                        raise ValueError("Nonfinite dynamics")
                    trace["sweeps"] = sweep
                    stable = stable + 1 if gradient_max < self.settings.gradient_tolerance and normalized_gradient_max < self.settings.gradient_tolerance and update_max < self.settings.update_tolerance else 0
                    if stable >= self.settings.stable_sweeps:
                        break
                residual, edge_force, committed_gradient = _gradient(coordinates, source, target, offsets, weights, anchors)
                energy = float(0.5 * np.sum(weights[:, None] * residual ** 2))
                residual_max = float(np.linalg.norm(residual, axis=1).max()) if edges else 0.0
                committed_gradient_max = float(np.linalg.norm(committed_gradient, axis=1).max())
                committed_normalized_gradient_max = float(np.linalg.norm(committed_gradient / local_scale[:, None], axis=1).max())
                converged = stable >= self.settings.stable_sweeps and max(committed_gradient_max, committed_normalized_gradient_max) < self.settings.gradient_tolerance
                trace.update({
                    "status": "PASS" if converged else "NOT_CONVERGED", "gradient_max": committed_gradient_max,
                    "update_max": update_max, "energy": energy, "residual_max": residual_max, "alpha": alpha,
                    "normalized_gradient_max": committed_normalized_gradient_max,
                    "dynamics_seconds": perf_counter() - dynamics_started,
                    "dynamics_work": {"residual_edge_records": (sweep + 1) * len(edges), "force_edge_records": (sweep + 1) * len(edges), "gradient_endpoint_accumulations": 4 * (sweep + 1) * len(edges), "node_updates": sweep * len(nodes), "global_convergence_scans": 4 * sweep + 2},
                    "edge_visits": (sweep + 1) * len(edges),
                    "numeric_workspace_bytes": sum(a.nbytes for a in (source, target, offsets, weights, degree, local_scale, coordinates, residual, edge_force, gradient, delta, committed_gradient)),
                })
                if converged:
                    proposal = {
                        "schema": self.schema, "algorithm": self.algorithm, "settings": asdict(self.settings),
                        "training_manifest_hash": training_manifest_hash, "nodes": list(nodes),
                        "edges": [asdict(e) for e in edges], "relations": observation.relations,
                        "components": components, "anchors": anchors, "coordinates": coordinates.tolist(),
                    }
                    canonical(proposal)
                    self._snapshot, self._index = proposal, index
        except (ValueError, TypeError, AttributeError, OverflowError, FloatingPointError) as exc:
            trace.update(status="INVALID_STATE", reason=str(exc))
        trace["total_learn_seconds"] = perf_counter() - started
        self._last_failure = trace["status"]
        return trace

    def freeze(self):
        if self._snapshot is None:
            raise RuntimeError("No committed geometry")
        self._frozen = True

    def query(self, source, target):
        if self._snapshot is None:
            return Answer(self._last_failure)
        if not isinstance(source, str) or not isinstance(target, str):
            return Answer("INVALID_STATE")
        if source not in self._index or target not in self._index:
            return Answer("UNKNOWN")
        i, j = self._index[source], self._index[target]
        if self._snapshot["components"][i] != self._snapshot["components"][j]:
            return Answer("UNIDENTIFIABLE")
        a, b = self._snapshot["coordinates"][i], self._snapshot["coordinates"][j]
        displacement = (b[0] - a[0], b[1] - a[1])
        return Answer("OK", displacement) if all(np.isfinite(v) for v in displacement) else Answer("INVALID_STATE")

    def export(self):
        if self._snapshot is None:
            raise RuntimeError("No committed geometry")
        payload = dict(self._snapshot, frozen=self._frozen)
        return canonical(dict(payload, checksum=digest(payload)))

    @classmethod
    def load(cls, encoded):
        """Checksums detect accidental changes; semantic checks establish valid state."""
        try:
            payload = json.loads(encoded, object_pairs_hook=_unique_object)
            expected = {"checksum", "schema", "algorithm", "settings", "training_manifest_hash", "nodes", "edges", "relations", "components", "anchors", "coordinates", "frozen"}
            if not isinstance(payload, dict) or set(payload) != expected:
                raise ValueError("Incompatible geometry fields")
            checksum = payload.pop("checksum")
            if not valid_hash(checksum) or digest(payload) != checksum or payload["schema"] != cls.schema or payload["algorithm"] != cls.algorithm:
                raise ValueError("Incompatible or corrupted geometry")
            if not valid_hash(payload["training_manifest_hash"]) or type(payload["frozen"]) is not bool:
                raise ValueError("Invalid manifest identity or lifecycle")
            state = cls(Settings(**payload["settings"]))
            if any(not isinstance(payload[k], list) for k in ("nodes", "edges", "relations", "components", "anchors", "coordinates")):
                raise ValueError("Invalid serialized containers")
            edges = []
            for e in payload["edges"]:
                if not isinstance(e, dict) or set(e) != {"source", "target", "offset", "weight", "relation_id"} or not isinstance(e["offset"], list):
                    raise ValueError("Invalid serialized edge")
                edges.append(Constraint(e["source"], e["target"], tuple(e["offset"]), e["weight"], e["relation_id"]))
            relations = tuple((entry[0], tuple(entry[1])) for entry in payload["relations"] if isinstance(entry, list) and len(entry) == 2 and isinstance(entry[1], list))
            if len(relations) != len(payload["relations"]):
                raise ValueError("Invalid serialized relations")
            observation = Observation(tuple(payload["nodes"]), tuple(edges), relations)
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                nodes, index, sorted_edges, source, target, offsets, weights, degree, components, anchors = _prepare(observation)
                if list(nodes) != payload["nodes"] or tuple(edges) != sorted_edges:
                    raise ValueError("Noncanonical state ordering")
                for name, actual in (("components", components), ("anchors", anchors)):
                    if any(type(v) is not int for v in payload[name]) or payload[name] != actual:
                        raise ValueError("Invalid connectivity or gauge")
                if any(not isinstance(row, list) or len(row) != 2 or not all(finite_number(v) for v in row) for row in payload["coordinates"]):
                    raise ValueError("Invalid coordinate records")
                coordinates = np.array(payload["coordinates"], dtype=np.float64)
                if coordinates.shape != (len(nodes), 2) or np.any(coordinates[anchors] != 0):
                    raise ValueError("Invalid coordinates or gauge")
                residual, force, gradient = _gradient(coordinates, source, target, offsets, weights, anchors)
                if float(np.linalg.norm(gradient, axis=1).max()) >= state.settings.gradient_tolerance:
                    raise ValueError("Persisted coordinates are not an equilibrium")
                local_scale = np.where(degree > 0, degree, 1.0)
                if float(np.linalg.norm(gradient / local_scale[:, None], axis=1).max()) >= state.settings.gradient_tolerance:
                    raise ValueError("Persisted normalized force is not an equilibrium")
                energy = float(0.5 * np.sum(weights[:, None] * residual ** 2))
                if not np.isfinite(energy):
                    raise ValueError("Invalid residual energy")
            state._frozen = payload.pop("frozen")
            state._snapshot, state._index = payload, index
            return state
        except (ValueError, TypeError, KeyError, AttributeError, IndexError, OverflowError, FloatingPointError) as exc:
            raise ValueError(f"Invalid geometry artifact: {exc}") from exc
