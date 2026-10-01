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


class _C1V1State(GeometryState):
    """Read-only validation adapter for explicit migration of historical C1."""
    schema = "geomind.c1.geometry.v1"
    algorithm = "budgeted-active-queue.v1"


class _BudgetExhausted(Exception):
    pass


class IncrementalGeometry(GeometryState):
    schema = "geomind.c1.geometry.v2"
    algorithm = "budgeted-active-queue.v2"

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
        if not isinstance(schema, str):
            raise ValueError("Saved geometry schema must be a string")
        loader = {cls.schema: cls, _C1V1State.schema: _C1V1State, GeometryState.schema: GeometryState}.get(schema)
        if loader is None:
            raise ValueError("Unknown saved geometry version")
        loaded = loader.load(encoded)
        state = cls(loaded.settings)
        payload = json.loads(loaded.export())
        payload.pop("checksum")
        payload.pop("frozen")
        payload.update(schema=cls.schema, algorithm=cls.algorithm)
        state._snapshot = payload
        state._index = {node: i for i, node in enumerate(payload["nodes"])}
        return state if schema == cls.schema else cls.load(state.export())

    @classmethod
    def load(cls, encoded):
        state = super().load(encoded)
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            try:
                nodes, index, edges, source, target, offsets, weights, degree, components, anchors = _prepare(state.observation())
                coordinates = np.array(state._snapshot["coordinates"])
                residual, force, gradient = _gradient(coordinates, source, target, offsets, weights, anchors)
                alpha = state.settings.step_factor / max(1.0, float(degree.max()))
                if alpha * float(np.linalg.norm(gradient, axis=1).max()) >= state.settings.update_tolerance:
                    raise ValueError("Persisted coordinates violate C1 update tolerance")
            except (ValueError, OverflowError, FloatingPointError) as exc:
                raise ValueError(f"Invalid C1 geometry artifact: {exc}") from exc
        return state

    def observation(self):
        if self._snapshot is None:
            raise RuntimeError("No saved geometry")
        return Observation(tuple(self._snapshot["nodes"]), tuple(Constraint(e["source"], e["target"], tuple(e["offset"]), e["weight"], e["relation_id"]) for e in self._snapshot["edges"]), tuple((name, tuple(vector)) for name, vector in self._snapshot["relations"]))

    def update(self, observation, manifest_hash, edge_visit_budget=100000):
        """Accept a complete, additive public observation as one atomic update.

        Existing constraints and relation definitions survive unchanged. A
        spanning tree of added inter-frame edges places new singleton nodes
        and merges old component frames without disturbing internal answers.
        All initialization reads, local reads and certificates share the cap.
        Full preparation, translations, queue and persistence are also timed.
        """
        if self._frozen:
            raise RuntimeError("Frozen geometry cannot update; fork the saved state explicitly")
        started = perf_counter()
        before = self.export() if self._snapshot is not None else None
        trace = {"status": "INVALID_STATE", "reason": None, "edge_visit_budget": edge_visit_budget if type(edge_visit_budget) is int else None,
                 "dynamic_edge_visits": 0, "warm_start_edge_visits": 0, "local_edge_visits": 0, "certificate_edge_visits": 0,
                 "node_pops": 0, "node_updates": 0, "queue_pushes": 0, "queue_peak": 0,
                 "queue_rounds": 0, "certificate_passes": 0, "fallbacks": 0,
                 "budget_exhaustion_required_visits": None,
                 "committed_before": digest(json.loads(before)) if before else None}
        touched = set()
        dynamics_started = None
        dynamics_finished = None
        numeric_arrays = []

        def spend(count, category):
            if trace["dynamic_edge_visits"] + count > edge_visit_budget:
                trace["budget_exhaustion_required_visits"] = count
                raise _BudgetExhausted()
            trace["dynamic_edge_visits"] += count
            trace[category] += count

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
            added_counts = new_counts - old_counts
            added = list(added_counts.elements())
            added_nodes = set(observation.nodes) - set(old.nodes)
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                nodes, index, edges, source, target, offsets, weights, degree, components, anchors = _prepare(observation)
                coordinates = np.zeros((len(nodes), 2), dtype=np.float64)
                for node in old.nodes:
                    coordinates[index[node]] = self._snapshot["coordinates"][self._index[node]]
                adjacency = [[] for _ in nodes]
                for k, (i, j) in enumerate(zip(source, target)):
                    adjacency[i].append((k, j, -1))
                    adjacency[j].append((k, i, 1))
                anchor_set = set(anchors)
                alpha = self.settings.step_factor / max(1.0, float(degree.max()))
                local_scale = np.where(degree > 0, degree, 1.0)
                # Each old component is a rigid frame; each new node starts as
                # a singleton frame. Only added constraints place these frames.
                frames = np.empty(len(nodes), dtype=np.int64)
                for node in old.nodes:
                    frames[index[node]] = self._snapshot["components"][self._index[node]]
                frame_count = len(self._snapshot["anchors"])
                for node in sorted(added_nodes):
                    frames[index[node]] = frame_count
                    frame_count += 1
                frame_adjacency = [[] for _ in range(frame_count)]
                shifts = np.zeros((frame_count, 2))
                added_indices = []
                remaining = added_counts.copy()
                for k, edge in enumerate(edges):
                    if remaining[edge]:
                        added_indices.append(k)
                        remaining[edge] -= 1
                numeric_arrays = [source, target, offsets, weights, degree, coordinates, local_scale, frames, shifts]
                trace["preprocessing_seconds"] = perf_counter() - started
                trace["preprocessing_work"] = {"input_edge_records": len(old.edges) + len(edges), "component_neighbor_visits": 2 * len(edges), "adjacency_edge_records": len(edges), "degree_endpoint_accumulations": 2 * len(edges), "coordinate_records_copied": len(old.nodes), "frame_node_visits": len(nodes), "added_index_edge_records": len(edges), "sort_items": len(edges) + len(nodes), "sort_comparisons": "not instrumented; included in preprocessing time"}
                trace["alpha"] = alpha
                trace["added_nodes"] = len(added_nodes)
                trace["added_edges"] = len(added)
                dynamics_started = perf_counter()
                warm_started = perf_counter()
                for k in added_indices:
                    spend(1, "warm_start_edge_visits")
                    touched.add(k)
                    a, b = int(frames[source[k]]), int(frames[target[k]])
                    if a == b:
                        continue
                    offset = offsets[k] - (coordinates[target[k]] - coordinates[source[k]])
                    frame_adjacency[a].append((k, b, offset))
                    frame_adjacency[b].append((k, a, -offset))
                visited = set()
                for root in range(frame_count):
                    if root in visited:
                        continue
                    visited.add(root)
                    pending = [root]
                    while pending:
                        frame = pending.pop()
                        for k, neighbor, offset in frame_adjacency[frame]:
                            spend(1, "warm_start_edge_visits")
                            touched.add(k)
                            if neighbor not in visited:
                                shifts[neighbor] = shifts[frame] + offset
                                visited.add(neighbor)
                                pending.append(neighbor)
                coordinates += shifts[frames]
                # Re-gauge merged components; all internal differences survive.
                origins = [coordinates[anchor].copy() for anchor in anchors]
                for i, component in enumerate(components):
                    coordinates[i] -= origins[component]
                trace["warm_start_seconds"] = perf_counter() - warm_started
                trace["warm_start_node_translations"] = len(nodes)
                trace["gauge_node_visits"] = len(nodes)
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
                stable = 0
                while True:
                    while current:
                        node = heapq.heappop(current)
                        current_members.remove(node)
                        trace["node_pops"] += 1
                        incident = adjacency[node]
                        force = np.zeros(2)
                        for k, neighbor, sign in incident:
                            spend(1, "local_edge_visits")
                            touched.add(k)
                            residual = coordinates[target[k]] - coordinates[source[k]] - offsets[k]
                            force += sign * weights[k] * residual
                        magnitude = float(np.linalg.norm(force))
                        if not np.isfinite(magnitude):
                            raise ValueError("Nonfinite local force norm")
                        if max(magnitude, magnitude / local_scale[node]) < self.settings.gradient_tolerance and alpha * magnitude < self.settings.update_tolerance:
                            continue
                        coordinates[node] -= alpha * force
                        trace["node_updates"] += 1
                        # A moved node and residual-bearing neighbors become active.
                        push(node, next_round=True)
                        for k, neighbor, sign in incident:
                            spend(1, "local_edge_visits")
                            touched.add(k)
                            residual = coordinates[target[k]] - coordinates[source[k]] - offsets[k]
                            residual_norm = float(np.linalg.norm(residual))
                            if not np.isfinite(residual_norm):
                                raise ValueError("Nonfinite local residual norm")
                            if residual_norm > self.settings.gradient_tolerance:
                                push(neighbor, next_round=True)
                    if next_nodes:
                        trace["queue_rounds"] += 1
                        for node in sorted(next_nodes):
                            push(node)
                        next_nodes.clear()
                        continue
                    # Global proof is explicitly charged; never infer convergence
                    # merely because the queue is empty.
                    spend(len(edges), "certificate_edge_visits")
                    touched.update(range(len(edges)))
                    residual, edge_force, gradient = _gradient(coordinates, source, target, offsets, weights, anchors)
                    trace["certificate_passes"] += 1
                    norm = np.linalg.norm(gradient, axis=1)
                    if not np.isfinite(norm).all():
                        raise ValueError("Nonfinite convergence norm")
                    bad = np.flatnonzero((norm >= self.settings.gradient_tolerance) | (norm / local_scale >= self.settings.gradient_tolerance) | (alpha * norm >= self.settings.update_tolerance))
                    if len(bad):
                        stable = 0
                        for node in bad:
                            push(int(node))
                    else:
                        stable += 1
                        if stable >= self.settings.stable_sweeps:
                            trace["gradient_max"] = float(norm.max())
                            trace["normalized_gradient_max"] = float((norm / local_scale).max())
                            trace["update_max"] = float(alpha * norm.max())
                            trace["energy"] = float(0.5 * np.sum(weights[:, None] * residual ** 2))
                            trace["residual_max"] = float(np.linalg.norm(residual, axis=1).max()) if edges else 0.0
                            break
                numeric_arrays.extend((residual, edge_force, gradient))
                dynamics_finished = perf_counter()
                commit_started = perf_counter()
                proposal = {"schema": self.schema, "algorithm": self.algorithm, "settings": asdict(self.settings),
                            "training_manifest_hash": manifest_hash, "nodes": list(nodes), "edges": [asdict(e) for e in edges],
                            "relations": observation.relations, "components": components, "anchors": anchors,
                            "coordinates": coordinates.tolist()}
                canonical(proposal)
                self._snapshot, self._index = proposal, index
                trace.update(status="PASS", reason=None)
                trace["commit_seconds"] = perf_counter() - commit_started
        except _BudgetExhausted:
            trace.update(status="NOT_CONVERGED", reason="Dynamic edge-visit budget exhausted")
        except (ValueError, TypeError, AttributeError, OverflowError, FloatingPointError) as exc:
            trace.update(status="INVALID_STATE", reason=str(exc))
        self._last_failure = trace["status"]
        trace.setdefault("preprocessing_seconds", perf_counter() - started)
        trace["dynamics_seconds"] = (dynamics_finished or perf_counter()) - dynamics_started if dynamics_started is not None else 0.0
        trace["touched_edges"] = len(touched)
        trace["numeric_workspace_bytes"] = sum(a.nbytes for a in numeric_arrays)
        persistence_started = perf_counter()
        after = self.export() if self._snapshot is not None else None
        trace["committed_after"] = digest(json.loads(after)) if after else None
        trace["snapshot_retained"] = after == before if trace["status"] != "PASS" else None
        trace["persistence_seconds"] = perf_counter() - persistence_started
        trace["total_update_seconds"] = perf_counter() - started
        return trace
