"""C1 additive transactions from certified saved geometry.

Same residual energy as C0; stable-ID, asynchronous node relaxation is the
declared queue execution rule. No reference solver or hidden truth is imported.
"""

from collections import Counter
from dataclasses import asdict
import heapq
import json
from time import perf_counter

import numpy as np

from .geometry import Constraint, GeometryState, Observation, _gradient, _prepare, canonical, digest, valid_hash


class IncrementalGeometry(GeometryState):
    schema = "geomind.c1.geometry.v1"
    algorithm = "budgeted-active-queue.v1"

    def learn(self, *args, **kwargs):
        raise RuntimeError("C1 begins from a saved C0/C1 state; use from_saved then update")

    @classmethod
    def from_saved(cls, encoded):
        """Explicit mutable fork; never thaws or mutates the saved original."""
        try:
            record = json.loads(encoded)
            if not isinstance(record, dict):
                raise ValueError("Saved geometry must be an object")
            schema = record.get("schema")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid saved geometry: {exc}") from exc
        loaded = cls.load(encoded) if schema == cls.schema else GeometryState.load(encoded)
        state = cls(loaded.settings)
        payload = json.loads(loaded.export())
        payload.pop("checksum")
        payload.pop("frozen")
        payload.update(schema=cls.schema, algorithm=cls.algorithm)
        state._snapshot = payload
        state._index = {node: i for i, node in enumerate(payload["nodes"])}
        return state

    def observation(self):
        if self._snapshot is None:
            raise RuntimeError("No saved geometry")
        return Observation(tuple(self._snapshot["nodes"]), tuple(Constraint(e["source"], e["target"], tuple(e["offset"]), e["weight"], e["relation_id"]) for e in self._snapshot["edges"]), tuple((name, tuple(vector)) for name, vector in self._snapshot["relations"]))

    def update(self, observation, manifest_hash, edge_visit_budget=100000):
        """Accept a complete, additive public observation as one atomic update.

Existing constraints and relation definitions must survive unchanged. Costs
include full input preparation; the dynamic cap covers incident-edge reads
and global certificates. There is no automatic full-solve fallback.
"""
        if self._frozen:
            raise RuntimeError("Frozen geometry cannot update; fork the saved state explicitly")
        started = perf_counter()
        before = self.export() if self._snapshot is not None else None
        trace = {"status": "INVALID_STATE", "reason": None, "edge_visit_budget": edge_visit_budget if type(edge_visit_budget) is int else None,
                 "dynamic_edge_visits": 0, "local_edge_visits": 0, "certificate_edge_visits": 0,
                 "node_pops": 0, "node_updates": 0, "queue_pushes": 0, "queue_peak": 0,
                 "queue_rounds": 0, "certificate_passes": 0, "fallbacks": 0,
                 "committed_before": digest(json.loads(before)) if before else None}
        touched = set()
        try:
            if self._snapshot is None or not isinstance(observation, Observation) or not valid_hash(manifest_hash):
                raise ValueError("Saved state, typed observation and manifest identity required")
            if type(edge_visit_budget) is not int or edge_visit_budget < 0:
                raise ValueError("Nonnegative integer edge budget required")
            old = self.observation()
            observation.validate()
            if not set(old.nodes).issubset(observation.nodes):
                raise ValueError("C1 permits additive nodes only")
            old_counts = Counter(old.edges)
            new_counts = Counter(observation.edges)
            if old_counts - new_counts:
                raise ValueError("C1 permits additive constraints only")
            old_relations, new_relations = dict(old.relations), dict(observation.relations)
            if any(new_relations.get(name) != vector for name, vector in old_relations.items()):
                raise ValueError("Existing relation definitions must remain unchanged")
            added = list((new_counts - old_counts).elements())
            added_nodes = set(observation.nodes) - set(old.nodes)
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                nodes, index, edges, source, target, offsets, weights, degree, components, anchors = _prepare(observation)
                coordinates = np.zeros((len(nodes), 2), dtype=np.float64)
                for node in old.nodes:
                    coordinates[index[node]] = self._snapshot["coordinates"][self._index[node]]
                # Re-gauge whole components; relative answers survive frame changes.
                origins = [coordinates[anchor].copy() for anchor in anchors]
                for i, component in enumerate(components):
                    coordinates[i] -= origins[component]
                adjacency = [[] for _ in nodes]
                for k, (i, j) in enumerate(zip(source, target)):
                    adjacency[i].append((k, j, -1))
                    adjacency[j].append((k, i, 1))
                anchor_set = set(anchors)
                alpha = self.settings.step_factor / max(1.0, float(degree.max()))
                local_scale = np.where(degree > 0, degree, 1.0)
                dirty = {index[e.source] for e in added} | {index[e.target] for e in added} | {index[n] for n in added_nodes}
                # If an old anchor becomes free after merging, certify it too.
                dirty |= {index[old.nodes[a]] for a in self._snapshot["anchors"] if index[old.nodes[a]] not in anchor_set}
                current, next_nodes = [], set()
                current_members = set()

                def push(node, next_round=False):
                    if node in anchor_set:
                        return
                    if next_round:
                        if node not in next_nodes:
                            next_nodes.add(node)
                            trace["queue_pushes"] += 1
                    elif node not in current_members:
                        heapq.heappush(current, node)
                        current_members.add(node)
                        trace["queue_pushes"] += 1
                    trace["queue_peak"] = max(trace["queue_peak"], len(current_members) + len(next_nodes))

                for node in sorted(dirty):
                    push(node)
                trace["preprocessing_seconds"] = perf_counter() - started
                trace["preprocessing_work"] = {"input_edge_records": len(old.edges) + len(edges), "component_neighbor_visits": 2 * len(edges), "adjacency_edge_records": len(edges), "degree_endpoint_accumulations": 2 * len(edges), "coordinate_records_copied": len(old.nodes), "gauge_node_visits": len(nodes), "sort_items": len(edges) + len(nodes)}
                trace["alpha"] = alpha
                trace["added_nodes"] = len(added_nodes)
                trace["added_edges"] = len(added)
                dynamics_started = perf_counter()
                stable = 0
                exhausted = False
                while True:
                    while current:
                        node = heapq.heappop(current)
                        current_members.remove(node)
                        trace["node_pops"] += 1
                        incident = adjacency[node]
                        required = 2 * len(incident)
                        if trace["dynamic_edge_visits"] + required > edge_visit_budget:
                            exhausted = True
                            break
                        force = np.zeros(2)
                        for k, neighbor, sign in incident:
                            residual = coordinates[target[k]] - coordinates[source[k]] - offsets[k]
                            force += sign * weights[k] * residual
                            touched.add(k)
                        trace["local_edge_visits"] += len(incident)
                        trace["dynamic_edge_visits"] += len(incident)
                        magnitude = float(np.linalg.norm(force))
                        if max(magnitude, magnitude / local_scale[node]) < self.settings.gradient_tolerance:
                            continue
                        coordinates[node] -= alpha * force
                        trace["node_updates"] += 1
                        # A moved node and residual-bearing neighbors become active.
                        push(node, next_round=True)
                        for k, neighbor, sign in incident:
                            residual = coordinates[target[k]] - coordinates[source[k]] - offsets[k]
                            if float(np.linalg.norm(residual)) > self.settings.gradient_tolerance:
                                push(neighbor, next_round=True)
                        trace["local_edge_visits"] += len(incident)
                        trace["dynamic_edge_visits"] += len(incident)
                    if exhausted:
                        break
                    if next_nodes:
                        trace["queue_rounds"] += 1
                        for node in sorted(next_nodes):
                            push(node)
                        next_nodes.clear()
                        continue
                    # Global proof is explicitly charged; never infer convergence
                    # merely because the queue is empty.
                    if trace["dynamic_edge_visits"] + len(edges) > edge_visit_budget:
                        exhausted = True
                        break
                    residual, edge_force, gradient = _gradient(coordinates, source, target, offsets, weights, anchors)
                    trace["certificate_edge_visits"] += len(edges)
                    trace["dynamic_edge_visits"] += len(edges)
                    trace["certificate_passes"] += 1
                    touched.update(range(len(edges)))
                    norm = np.linalg.norm(gradient, axis=1)
                    bad = np.flatnonzero((norm >= self.settings.gradient_tolerance) | (norm / local_scale >= self.settings.gradient_tolerance))
                    if len(bad):
                        stable = 0
                        for node in bad:
                            push(int(node))
                    else:
                        stable += 1
                        if stable >= self.settings.stable_sweeps:
                            trace["gradient_max"] = float(norm.max())
                            trace["normalized_gradient_max"] = float((norm / local_scale).max())
                            trace["energy"] = float(0.5 * np.sum(weights[:, None] * residual ** 2))
                            trace["residual_max"] = float(np.linalg.norm(residual, axis=1).max()) if edges else 0.0
                            break
                trace["dynamics_seconds"] = perf_counter() - dynamics_started
                trace["touched_edges"] = len(touched)
                trace["numeric_workspace_bytes"] = sum(a.nbytes for a in (source, target, offsets, weights, degree, coordinates, local_scale))
                if exhausted:
                    trace.update(status="NOT_CONVERGED", reason="Dynamic edge-visit budget exhausted")
                else:
                    proposal = {"schema": self.schema, "algorithm": self.algorithm, "settings": asdict(self.settings),
                                "training_manifest_hash": manifest_hash, "nodes": list(nodes), "edges": [asdict(e) for e in edges],
                                "relations": observation.relations, "components": components, "anchors": anchors,
                                "coordinates": coordinates.tolist()}
                    canonical(proposal)
                    self._snapshot, self._index = proposal, index
                    trace.update(status="PASS", reason=None)
        except (ValueError, TypeError, AttributeError, OverflowError, FloatingPointError) as exc:
            trace.update(status="INVALID_STATE", reason=str(exc))
        self._last_failure = trace["status"]
        trace["total_update_seconds"] = perf_counter() - started
        trace["committed_after"] = digest(json.loads(self.export())) if self._snapshot is not None else None
        trace["snapshot_retained"] = self.export() == before if trace["status"] != "PASS" else None
        return trace
