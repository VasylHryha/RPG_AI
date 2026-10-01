"""C1 additive transactions over incrementally maintained geometry (R004).

Same residual energy and C0 step rule; stable-ID asynchronous node relaxation
is the declared queue rule. The candidate keeps its committed geometry as
in-memory incremental structures and accepts additive deltas. One operation
cap charges every in-memory transaction step: delta input, degree upkeep,
frame placement and translation, anchor choice, incident-edge reads and the
local convergence certificate. An optional, separately capped full solve is a
distinct fallback arm. Export/load are separate, global, timed persistence
operations validated by the accepted C0 rules. Every failed transaction is
undone from a journal. No reference solver or hidden truth is imported.

Local certificate soundness: a loaded state is fully certified by the C0
validator. A transaction changes a node's force only through added incident
edges, its own movement or a neighbor's movement, and changes which nodes are
fixed only through anchor reassignment. Rigid frame translations preserve
every old residual, and alpha can only shrink as weighted degree grows. The
certificate therefore checks exactly the endpoints of added edges, new nodes,
freed anchors, moved nodes and neighbors of moved nodes.
"""

import heapq
import json
import math
from bisect import insort
from collections import Counter
from dataclasses import asdict
from time import perf_counter

import numpy as np

from .geometry import Answer, Constraint, GeometryState, Observation, Settings, _gradient, _prepare, canonical, digest, finite_number, valid_hash

# Certified forces stay below tolerance by this factor, so summation-order
# differences from the C0 validator cannot make a commit fail on reload.
CERTIFICATE_MARGIN = 1 - 1e-6
# The fallback solve aims well inside the certificate before it is checked.
FALLBACK_TARGET = 0.25


class _C1V1State(GeometryState):
    """Read-only validation adapters for explicit migration of earlier C1."""
    schema = "geomind.c1.geometry.v1"
    algorithm = "budgeted-active-queue.v1"


class _C1V2State(GeometryState):
    schema = "geomind.c1.geometry.v2"
    algorithm = "budgeted-active-queue.v2"


class _C1V3State(GeometryState):
    schema = "geomind.c1.geometry.v3"
    algorithm = "budgeted-active-queue.v3"


class _C1V4Snapshot(GeometryState):
    """Accepted C0 validation rules applied to the current C1 snapshot."""
    schema = "geomind.c1.geometry.v4"
    algorithm = "incremental-active-queue.v4"


class _BudgetExhausted(Exception):
    pass


class _FallbackExhausted(Exception):
    pass


def _edge_key(edge):
    # Identical to the canonical C0 edge order in geometry._prepare.
    return (edge.source, edge.target, edge.offset, edge.weight, edge.relation_id or "")


TRACE_COUNTERS = ("input_records", "degree_reads", "frame_edge_reads", "translation_writes", "anchor_reads",
                  "local_edge_reads", "certificate_reads")


class _Transaction:
    """Operation meter plus undo journal for one atomic apply."""

    def __init__(self, state, trace, budget, fallback_budget):
        self.state, self.trace = state, trace
        self.budget, self.fallback_budget = budget, fallback_budget
        self.journal = []
        self.coordinates = {}
        self.components = {}

    def spend(self, count, category):
        if self.trace["charged_operations"] + count > self.budget:
            self.trace["budget_exhaustion_required"] = count
            raise _BudgetExhausted()
        self.trace["charged_operations"] += count
        self.trace[category] += count

    def spend_fallback(self, count):
        if self.trace["fallback_operations"] + count > self.fallback_budget:
            self.trace["fallback_exhaustion_required"] = count
            raise _FallbackExhausted()
        self.trace["fallback_operations"] += count

    def move(self, node, x, y):
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError("Nonfinite coordinates")
        state = self.state
        if node not in self.coordinates:
            self.coordinates[node] = (state._x[node], state._y[node])
        state._x[node], state._y[node] = x, y

    def relabel(self, node, component):
        state = self.state
        if node not in self.components:
            self.components[node] = state._comp[node]
        state._comp[node] = component

    def rollback(self):
        state = self.state
        for node, (x, y) in self.coordinates.items():
            state._x[node], state._y[node] = x, y
        for node, component in self.components.items():
            state._comp[node] = component
        for undo in reversed(self.journal):
            undo()
        self.trace["journal_entries_undone"] = len(self.journal) + len(self.coordinates) + len(self.components)


class IncrementalGeometry:
    schema = _C1V4Snapshot.schema
    algorithm = _C1V4Snapshot.algorithm

    def __init__(self, settings=Settings()):
        settings.validate()
        self._settings = settings
        self._frozen = False
        self._ready = False
        self._last_failure = "INVALID_STATE"
        self._last_certified = frozenset()

    @property
    def settings(self):
        return self._settings

    def learn(self, *args, **kwargs):
        raise RuntimeError("C1 begins from a saved C0/C1 state; use from_saved then apply/update")

    # ------------------------------------------------------------------ load
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
        loader = {cls.schema: _C1V4Snapshot, _C1V3State.schema: _C1V3State, _C1V2State.schema: _C1V2State,
                  _C1V1State.schema: _C1V1State, GeometryState.schema: GeometryState}.get(schema)
        if loader is None:
            raise ValueError("Unknown saved geometry version")
        return cls._from_validated(loader.load(encoded), frozen=False)

    @classmethod
    def load(cls, encoded):
        validated = _C1V4Snapshot.load(encoded)
        return cls._from_validated(validated, frozen=validated._frozen)

    @classmethod
    def _from_validated(cls, validated, frozen):
        """Build incremental structures from a fully C0-validated snapshot."""
        payload = validated._snapshot
        try:
            state = cls(validated.settings)
            state._names = list(payload["nodes"])
            state._id = {name: i for i, name in enumerate(state._names)}
            state._x = [float(row[0]) for row in payload["coordinates"]]
            state._y = [float(row[1]) for row in payload["coordinates"]]
            state._comp = list(payload["components"])
            state._members = {}
            for i, component in enumerate(state._comp):
                state._members.setdefault(component, []).append(i)
            state._anchor = dict(enumerate(payload["anchors"]))
            state._next_comp = len(payload["anchors"])
            count = len(state._names)
            state._adj = [[] for _ in range(count)]
            state._src_w = [[] for _ in range(count)]
            state._tgt_w = [[] for _ in range(count)]
            state._es, state._et, state._edx, state._edy, state._ew, state._edges = [], [], [], [], [], []
            for record in payload["edges"]:
                edge = Constraint(record["source"], record["target"], tuple(record["offset"]), record["weight"], record["relation_id"])
                s, t, _ = state._append_edge(edge)
                item = (_edge_key(edge), float(edge.weight))
                state._src_w[s].append(item)  # canonical order keeps degree lists sorted
                state._tgt_w[t].append(item)
            state._deg = [state._degree(i) for i in range(count)]
            state._maxdeg = max(state._deg, default=0.0)
            state._relations = [(name, tuple(vector)) for name, vector in payload["relations"]]
            state._relation_map = dict(state._relations)
            state._manifest_hash = payload["training_manifest_hash"]
            state._frozen = frozen
            observation = Observation(tuple(state._names), tuple(state._edges), tuple(state._relations))
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                nodes, index, edges, source, target, offsets, weights, degree, components, anchors = _prepare(observation)
                # Incremental degree upkeep must reproduce the C0 anchor rule bit for bit.
                if any(a != float(b) for a, b in zip(state._deg, degree)):
                    raise ValueError("Incremental degree bookkeeping differs from C0 preparation")
                coordinates = np.array(payload["coordinates"], dtype=np.float64).reshape(-1, 2)
                residual, force, gradient = _gradient(coordinates, source, target, offsets, weights, anchors)
                alpha = state.settings.step_factor / max(1.0, float(degree.max()))
                if alpha * float(np.linalg.norm(gradient, axis=1).max()) >= state.settings.update_tolerance:
                    raise ValueError("Persisted coordinates violate C1 update tolerance")
            state._ready = True
            return state
        except (ValueError, TypeError, KeyError, IndexError, OverflowError, FloatingPointError) as exc:
            raise ValueError(f"Invalid C1 geometry artifact: {exc}") from exc

    # ---------------------------------------------------------- structures
    def _degree(self, node):
        # Same sequential summation as np.bincount(source) + np.bincount(target).
        outgoing = 0.0
        for _, weight in self._src_w[node]:
            outgoing += weight
        incoming = 0.0
        for _, weight in self._tgt_w[node]:
            incoming += weight
        return outgoing + incoming

    def _append_edge(self, edge):
        s, t = self._id[edge.source], self._id[edge.target]
        k = len(self._es)
        self._es.append(s)
        self._et.append(t)
        self._edx.append(float(edge.offset[0]))
        self._edy.append(float(edge.offset[1]))
        self._ew.append(float(edge.weight))
        self._edges.append(edge)
        self._adj[s].append(k)
        self._adj[t].append(k)
        return s, t, k

    def _is_anchor(self, node):
        return self._anchor[self._comp[node]] == node

    def _better_anchor(self, a, b):
        # C0 rule: maximum weighted degree, then smallest node ID.
        return self._deg[a] > self._deg[b] or (self._deg[a] == self._deg[b] and self._names[a] < self._names[b])

    def _force(self, node):
        fx = fy = 0.0
        x, y = self._x, self._y
        for k in self._adj[node]:
            s, t, w = self._es[k], self._et[k], self._ew[k]
            rx = x[t] - x[s] - self._edx[k]
            ry = y[t] - y[s] - self._edy[k]
            if not math.isfinite(rx * rx + ry * ry):
                raise ValueError("Nonfinite residual energy")
            if s == node:
                fx -= w * rx
                fy -= w * ry
            else:
                fx += w * rx
                fy += w * ry
        magnitude = math.hypot(fx, fy)
        if not math.isfinite(magnitude):
            raise ValueError("Nonfinite local force norm")
        return fx, fy, magnitude

    # --------------------------------------------------------------- reads
    def query(self, source, target):
        if not self._ready:
            return Answer(self._last_failure)
        if not isinstance(source, str) or not isinstance(target, str):
            return Answer("INVALID_STATE")
        if source not in self._id or target not in self._id:
            return Answer("UNKNOWN")
        i, j = self._id[source], self._id[target]
        if self._comp[i] != self._comp[j]:
            return Answer("UNIDENTIFIABLE")
        anchor = self._anchor[self._comp[i]]
        # Same arithmetic as exporting anchor-relative coordinates then subtracting.
        dx = (self._x[j] - self._x[anchor]) - (self._x[i] - self._x[anchor])
        dy = (self._y[j] - self._y[anchor]) - (self._y[i] - self._y[anchor])
        return Answer("OK", (dx, dy)) if math.isfinite(dx) and math.isfinite(dy) else Answer("INVALID_STATE")

    def observation(self):
        if not self._ready:
            raise RuntimeError("No saved geometry")
        return Observation(tuple(sorted(self._names)), tuple(sorted(self._edges, key=_edge_key)), tuple(self._relations))

    def freeze(self):
        if not self._ready:
            raise RuntimeError("No committed geometry")
        self._frozen = True

    def export(self):
        """Global persistence: canonical C0-format snapshot, anchors at zero."""
        if not self._ready:
            raise RuntimeError("No committed geometry")
        order = sorted(range(len(self._names)), key=self._names.__getitem__)
        rank = {node: r for r, node in enumerate(order)}
        labels, anchors = {}, []
        for node in order:
            component = self._comp[node]
            if component not in labels:
                labels[component] = len(anchors)
                anchors.append(rank[self._anchor[component]])
        coordinates = []
        for node in order:
            anchor = self._anchor[self._comp[node]]
            coordinates.append([self._x[node] - self._x[anchor], self._y[node] - self._y[anchor]])
        payload = {"schema": self.schema, "algorithm": self.algorithm, "settings": asdict(self.settings),
                   "training_manifest_hash": self._manifest_hash, "nodes": [self._names[n] for n in order],
                   "edges": [asdict(e) for e in sorted(self._edges, key=_edge_key)], "relations": [list(r) for r in self._relations],
                   "components": [labels[self._comp[n]] for n in order], "anchors": anchors, "coordinates": coordinates,
                   "frozen": self._frozen}
        return canonical(dict(payload, checksum=digest(payload)))

    # ------------------------------------------------------------- updates
    def _new_trace(self, budget, fallback_budget):
        trace = {"status": "INVALID_STATE", "reason": None, "arm": "queue+fallback" if fallback_budget else "queue",
                 "edge_visit_budget": budget if type(budget) is int else None,
                 "fallback_budget": fallback_budget if type(fallback_budget) is int else None,
                 "charged_operations": 0, "fallback_operations": 0,
                 "budget_exhaustion_required": None, "fallback_exhaustion_required": None,
                 "node_pops": 0, "node_updates": 0, "queue_pushes": 0, "queue_peak": 0, "queue_rounds": 0,
                 "certificate_passes": 0, "certificate_nodes": 0, "forced_steps": 0,
                 "fallbacks": 0, "fallback_restarts": 0, "fallback_cg_iterations": 0, "queue_exhausted": False,
                 "added_nodes": 0, "added_edges": 0, "added_relations": 0, "translated_nodes": 0,
                 "moved_nodes": 0, "touched_edges": 0, "journal_entries_undone": 0}
        trace.update({name: 0 for name in TRACE_COUNTERS})
        return trace

    def update(self, observation, manifest_hash, edge_visit_budget=100000, fallback_budget=0):
        """Compatibility path: a complete additive observation, diffed in O(V+E).

        The full input and the diff are charged as input records, so this path
        is global by construction; `apply` takes the delta directly.
        """
        if self._frozen:
            raise RuntimeError("Frozen geometry cannot update; fork the saved state explicitly")
        try:
            if not self._ready or not isinstance(observation, Observation):
                raise ValueError("Saved state and typed observation required")
            observation.validate()
            old_nodes = set(self._names)
            if not old_nodes.issubset(observation.nodes):
                raise ValueError("C1 permits additive nodes only")
            old_counts, new_counts = Counter(self._edges), Counter(observation.edges)
            if old_counts - new_counts:
                raise ValueError("C1 permits additive constraints only")
            new_relations = dict(observation.relations)
            if any(new_relations.get(name) != vector for name, vector in self._relations):
                raise ValueError("Existing relation definitions must remain unchanged")
        except (ValueError, TypeError, AttributeError) as exc:
            trace = self._new_trace(edge_visit_budget, fallback_budget)
            trace["reason"] = str(exc)
            return trace
        added_nodes = tuple(sorted(set(observation.nodes) - old_nodes))
        added_edges = tuple((new_counts - old_counts).elements())
        added_relations = tuple(r for r in observation.relations if r[0] not in self._relation_map)
        records = len(observation.nodes) + len(observation.edges) + len(observation.relations) + len(self._names) + len(self._edges)
        return self.apply(added_nodes, added_edges, added_relations, manifest_hash, edge_visit_budget, fallback_budget, input_records=records)

    def _validate_delta(self, added_nodes, added_edges, added_relations):
        if not all(isinstance(c, tuple) for c in (added_nodes, added_edges, added_relations)):
            raise ValueError("Delta containers must be immutable tuples")
        if any(not isinstance(n, str) or not n or n in self._id for n in added_nodes) or len(set(added_nodes)) != len(added_nodes):
            raise ValueError("Added nodes must be new, nonempty and unique string IDs")
        catalog = dict(self._relation_map)
        for entry in added_relations:
            if not isinstance(entry, tuple) or len(entry) != 2:
                raise ValueError("Invalid relation manifest entry")
            name, vector = entry
            if not isinstance(name, str) or not name or name in catalog or not isinstance(vector, tuple) or len(vector) != 2 or not all(finite_number(v) for v in vector):
                raise ValueError("Invalid or redefined relation")
            catalog[name] = vector
        if catalog and not self._relation_map and self._edges:
            raise ValueError("Existing constraints lack the relation IDs a new manifest would require")
        known = set(added_nodes)
        for edge in added_edges:
            if not isinstance(edge, Constraint) or not isinstance(edge.source, str) or not isinstance(edge.target, str):
                raise ValueError("Invalid constraint record")
            if edge.source == edge.target or not all(n in self._id or n in known for n in (edge.source, edge.target)):
                raise ValueError("Dangling or self constraint")
            if not isinstance(edge.offset, tuple) or len(edge.offset) != 2 or not all(finite_number(v) for v in edge.offset):
                raise ValueError("Finite immutable 2D offsets required")
            if not finite_number(edge.weight) or edge.weight <= 0:
                raise ValueError("Positive finite weights required")
            if edge.relation_id is not None and (not isinstance(edge.relation_id, str) or catalog.get(edge.relation_id) != edge.offset):
                raise ValueError("Relation ID/vector mismatch")
            if catalog and edge.relation_id is None:
                raise ValueError("All manifest-backed constraints require relation IDs")

    def apply(self, added_nodes, added_edges, added_relations, manifest_hash, edge_visit_budget=100000, fallback_budget=0, input_records=0):
        """Atomically apply one additive delta; refusals undo every change."""
        if self._frozen:
            raise RuntimeError("Frozen geometry cannot update; fork the saved state explicitly")
        started = perf_counter()
        trace = self._new_trace(edge_visit_budget, fallback_budget)
        tx = None
        try:
            if not self._ready or not valid_hash(manifest_hash):
                raise ValueError("Saved state and manifest identity required")
            for value in (edge_visit_budget, fallback_budget, input_records):
                if type(value) is not int or value < 0:
                    raise ValueError("Nonnegative integer budgets required")
            tx = _Transaction(self, trace, edge_visit_budget, fallback_budget)
            tx.spend(input_records + len(added_nodes) + len(added_edges) + len(added_relations), "input_records")
            self._validate_delta(added_nodes, added_edges, added_relations)
            trace.update(added_nodes=len(added_nodes), added_edges=len(added_edges), added_relations=len(added_relations))
            trace["validation_seconds"] = perf_counter() - started
            self._apply_structure(tx, added_nodes, added_edges, added_relations)
            trace["structure_seconds"] = perf_counter() - started - trace["validation_seconds"]
            dynamics_started = perf_counter()
            try:
                self._relax(tx)
            except _BudgetExhausted:
                if not fallback_budget:
                    raise
                trace["queue_exhausted"] = True
                fallback_started = perf_counter()
                self._fallback(tx)
                trace["fallback_seconds"] = perf_counter() - fallback_started
            trace["dynamics_seconds"] = perf_counter() - dynamics_started
            self._manifest_hash = manifest_hash
            trace.update(status="PASS", reason=None)
        except _BudgetExhausted:
            self._undo(tx, trace, "NOT_CONVERGED", "Dynamic operation budget exhausted")
        except _FallbackExhausted:
            self._undo(tx, trace, "NOT_CONVERGED", "Fallback operation budget exhausted")
        except (ValueError, TypeError, AttributeError, KeyError, IndexError, OverflowError, FloatingPointError, ZeroDivisionError) as exc:
            self._undo(tx, trace, "INVALID_STATE", str(exc))
        except BaseException:
            self._undo(tx, trace, "INVALID_STATE", "interrupted")
            raise
        self._last_failure = trace["status"]
        if trace["status"] == "PASS":
            trace["moved_nodes"] = len(tx.coordinates)
            # Names of every node the committing certificate covered (for audits).
            self._last_certified = frozenset(self._names[i] for i in tx.certified)
        trace["total_seconds"] = perf_counter() - started
        return trace

    def _undo(self, tx, trace, status, reason):
        rollback_started = perf_counter()
        if tx is not None:
            tx.rollback()
        trace.update(status=status, reason=reason, rollback_seconds=perf_counter() - rollback_started)

    def _apply_structure(self, tx, added_nodes, added_edges, added_relations):
        trace = tx.trace
        for entry in added_relations:
            self._relations.append(entry)
            self._relation_map[entry[0]] = entry[1]
            tx.journal.append(lambda name=entry[0]: (self._relations.pop(), self._relation_map.pop(name)))
        for name in added_nodes:
            i, component = len(self._names), self._next_comp
            self._names.append(name)
            self._id[name] = i
            for column, value in ((self._x, 0.0), (self._y, 0.0), (self._comp, component), (self._adj, []), (self._src_w, []), (self._tgt_w, []), (self._deg, 0.0)):
                column.append(value)
            self._members[component] = [i]
            self._anchor[component] = i
            self._next_comp += 1
            tx.journal.append(lambda name=name, component=component: self._pop_node(name, component))
        new_ids = [self._id[name] for name in added_nodes]
        # Frames: every pre-existing component and every new singleton.
        previous_anchors = {}
        for edge in added_edges:
            for name in (edge.source, edge.target):
                component = self._comp[self._id[name]]
                previous_anchors.setdefault(component, self._anchor[component])
        for i in new_ids:
            previous_anchors.setdefault(self._comp[i], i)
        added_ids, endpoints = [], set()
        for edge in added_edges:
            s, t = self._id[edge.source], self._id[edge.target]
            tx.spend(len(self._src_w[s]) + len(self._tgt_w[s]) + len(self._src_w[t]) + len(self._tgt_w[t]) + 2, "degree_reads")
            old = (self._deg[s], self._deg[t], self._maxdeg)
            item = (_edge_key(edge), float(edge.weight))
            s, t, k = self._append_edge(edge)
            # Journal before the fallible steps so a partial insert is still undone.
            tx.journal.append(lambda s=s, t=t, item=item, old=old: self._pop_edge(s, t, item, old))
            insort(self._src_w[s], item)
            insort(self._tgt_w[t], item)
            self._deg[s], self._deg[t] = self._degree(s), self._degree(t)
            self._maxdeg = max(self._maxdeg, self._deg[s], self._deg[t])
            added_ids.append(k)
            endpoints.update((s, t))
        # Spanning tree of added inter-frame edges; the largest frame stays put.
        links = {}
        for k in added_ids:
            tx.spend(1, "frame_edge_reads")
            s, t = self._es[k], self._et[k]
            a, b = self._comp[s], self._comp[t]
            if a == b:
                continue
            dx = self._edx[k] - (self._x[t] - self._x[s])
            dy = self._edy[k] - (self._y[t] - self._y[s])
            links.setdefault(a, []).append((b, dx, dy))
            links.setdefault(b, []).append((a, -dx, -dy))
        merged_into = {}
        seen = set()
        for start in sorted(links, key=lambda c: self._names[self._anchor[c]]):
            if start in seen:
                continue
            group, stack = [start], [start]
            seen.add(start)
            while stack:
                frame = stack.pop()
                for other, _, _ in links[frame]:
                    tx.spend(1, "frame_edge_reads")
                    if other not in seen:
                        seen.add(other)
                        group.append(other)
                        stack.append(other)
            root = min(group, key=lambda c: (-len(self._members[c]), self._names[self._anchor[c]]))
            shifts, stack = {root: (0.0, 0.0)}, [root]
            while stack:
                frame = stack.pop()
                for other, dx, dy in links[frame]:
                    tx.spend(1, "frame_edge_reads")
                    if other not in shifts:
                        shifts[other] = (shifts[frame][0] + dx, shifts[frame][1] + dy)
                        stack.append(other)
            for frame in sorted(group, key=lambda c: self._names[self._anchor[c]]):
                if frame == root:
                    continue
                sx, sy = shifts[frame]
                members = self._members[frame]
                tx.spend(len(members), "translation_writes")
                for i in members:
                    tx.move(i, self._x[i] + sx, self._y[i] + sy)
                    tx.relabel(i, root)
                trace["translated_nodes"] += len(members)
                size, anchor = len(self._members[root]), self._anchor[frame]
                self._members[root].extend(members)
                del self._members[frame]
                del self._anchor[frame]
                tx.journal.append(lambda root=root, frame=frame, size=size, members=members, anchor=anchor: self._unmerge(root, frame, size, members, anchor))
                merged_into[frame] = root
        # Anchors: only previous anchors, added-edge endpoints and new nodes can win.
        candidates = {}
        for component, anchor in previous_anchors.items():
            candidates.setdefault(merged_into.get(component, component), set()).add(anchor)
        for i in endpoints | set(new_ids):
            candidates.setdefault(self._comp[i], set()).add(i)
        for component in sorted(candidates, key=lambda c: self._names[self._anchor[c]]):
            options = sorted(candidates[component] | {self._anchor[component]}, key=self._names.__getitem__)
            tx.spend(len(options), "anchor_reads")
            best = options[0]
            for option in options[1:]:
                if self._better_anchor(option, best):
                    best = option
            if best != self._anchor[component]:
                old = self._anchor[component]
                self._anchor[component] = best
                tx.journal.append(lambda component=component, old=old: self._anchor.__setitem__(component, old))
        freed = {a for a in previous_anchors.values() if not self._is_anchor(a)}
        tx.dirty = endpoints | set(new_ids) | freed
        tx.added_ids = added_ids

    def _pop_node(self, name, component):
        for column in (self._names, self._x, self._y, self._comp, self._adj, self._src_w, self._tgt_w, self._deg):
            column.pop()
        del self._id[name]
        del self._members[component]
        del self._anchor[component]
        self._next_comp -= 1

    def _pop_edge(self, s, t, item, old):
        for column in (self._es, self._et, self._edx, self._edy, self._ew, self._edges):
            column.pop()
        self._adj[t].pop()
        self._adj[s].pop()
        for column in (self._src_w[s], self._tgt_w[t]):
            if item in column:
                column.remove(item)
        self._deg[s], self._deg[t], self._maxdeg = old

    def _unmerge(self, root, frame, size, members, anchor):
        del self._members[root][size:]
        self._members[frame] = members
        self._anchor[frame] = anchor

    def _relax(self, tx):
        trace, settings = tx.trace, self.settings
        alpha = settings.step_factor / max(1.0, self._maxdeg)
        trace["alpha"] = alpha
        gtol, utol = settings.gradient_tolerance, settings.update_tolerance
        certify = set(tx.dirty)
        touched = set(tx.added_ids)
        current, members, next_nodes, forced = [], set(), set(), set()

        def push(node, next_round=False):
            if self._is_anchor(node):
                return
            if next_round:
                if node not in next_nodes:
                    next_nodes.add(node)
                    trace["queue_pushes"] += 1
            elif node not in members:
                heapq.heappush(current, (self._names[node], node))
                members.add(node)
                trace["queue_pushes"] += 1
            trace["queue_peak"] = max(trace["queue_peak"], len(members) + len(next_nodes))

        for node in sorted(tx.dirty, key=self._names.__getitem__):
            push(node)
        try:
            while True:
                while current:
                    _, node = heapq.heappop(current)
                    members.discard(node)
                    trace["node_pops"] += 1
                    incident = self._adj[node]
                    tx.spend(len(incident), "local_edge_reads")
                    touched.update(incident)
                    fx, fy, magnitude = self._force(node)
                    scale = self._deg[node] if self._deg[node] > 0 else 1.0
                    quiet = max(magnitude, magnitude / scale) < gtol and alpha * magnitude < utol
                    if node in forced:
                        # The certificate flagged this node; never skip it on a
                        # summation-order difference.
                        forced.discard(node)
                        trace["forced_steps"] += 1
                    elif quiet:
                        continue
                    tx.move(node, self._x[node] - alpha * fx, self._y[node] - alpha * fy)
                    trace["node_updates"] += 1
                    certify.add(node)
                    push(node, next_round=True)
                    tx.spend(len(incident), "local_edge_reads")
                    for k in incident:
                        s, t = self._es[k], self._et[k]
                        other = t if s == node else s
                        certify.add(other)
                        norm = math.hypot(self._x[t] - self._x[s] - self._edx[k], self._y[t] - self._y[s] - self._edy[k])
                        if not math.isfinite(norm):
                            raise ValueError("Nonfinite local residual norm")
                        if norm > gtol:
                            push(other, next_round=True)
                if next_nodes:
                    trace["queue_rounds"] += 1
                    for node in sorted(next_nodes, key=self._names.__getitem__):
                        push(node)
                    next_nodes.clear()
                    continue
                bad = self._certify(certify, alpha, lambda count: tx.spend(count, "certificate_reads"), trace, touched)
                if not bad:
                    break
                for node in bad:
                    forced.add(node)
                    push(node)
        finally:
            trace["touched_edges"] = len(touched)
            trace["moved_nodes"] = len(tx.coordinates)
            tx.certified = certify

    def _certify(self, nodes, alpha, charge, trace, touched=None):
        """Explicit convergence proof over every node whose force may have changed."""
        settings = self.settings
        gtol, utol = settings.gradient_tolerance * CERTIFICATE_MARGIN, settings.update_tolerance * CERTIFICATE_MARGIN
        checked = sorted((n for n in nodes if not self._is_anchor(n)), key=self._names.__getitem__)
        trace["certificate_passes"] += 1
        trace["certificate_nodes"] += len(checked)
        bad, worst, worst_normalized = [], 0.0, 0.0
        for node in checked:
            charge(len(self._adj[node]))
            if touched is not None:
                touched.update(self._adj[node])
            _, _, magnitude = self._force(node)
            scale = self._deg[node] if self._deg[node] > 0 else 1.0
            if magnitude >= gtol or magnitude / scale >= gtol or alpha * magnitude >= utol:
                bad.append(node)
            worst, worst_normalized = max(worst, magnitude), max(worst_normalized, magnitude / scale)
        if not bad:
            trace.update(gradient_max=worst, normalized_gradient_max=worst_normalized, update_max=alpha * worst)
        return bad

    def _fallback(self, tx):
        """Distinct arm: metered Jacobi-preconditioned CG on affected components."""
        trace, settings = tx.trace, self.settings
        trace["fallbacks"] = 1
        alpha = settings.step_factor / max(1.0, self._maxdeg)
        affected = set(getattr(tx, "certified", set())) | set(tx.dirty)
        components = sorted({self._comp[i] for i in affected}, key=lambda c: self._names[self._anchor[c]])
        gtol = settings.gradient_tolerance * CERTIFICATE_MARGIN * FALLBACK_TARGET
        utol = settings.update_tolerance * CERTIFICATE_MARGIN * FALLBACK_TARGET
        everyone = set()
        for component in components:
            nodes = sorted(self._members[component], key=self._names.__getitem__)
            everyone.update(nodes)
            tx.spend_fallback(len(nodes) + sum(len(self._adj[i]) for i in nodes))
            local = {node: r for r, node in enumerate(nodes)}
            edges = [k for i in nodes for k in self._adj[i] if self._es[k] == i]
            if not edges:
                continue
            src = np.array([local[self._es[k]] for k in edges], dtype=np.int64)
            tgt = np.array([local[self._et[k]] for k in edges], dtype=np.int64)
            offsets = np.array([(self._edx[k], self._edy[k]) for k in edges], dtype=np.float64)
            weights = np.array([self._ew[k] for k in edges], dtype=np.float64)
            scale = np.array([self._deg[i] if self._deg[i] > 0 else 1.0 for i in nodes])
            anchor, size = local[self._anchor[component]], len(nodes)
            X = np.array([(self._x[i], self._y[i]) for i in nodes], dtype=np.float64)
            trace["fallback_workspace_bytes"] = trace.get("fallback_workspace_bytes", 0) + sum(a.nbytes for a in (src, tgt, offsets, weights, scale, X))

            def laplacian(V, subtract=None):
                tx.spend_fallback(len(edges))
                drops = V[tgt] - V[src] if subtract is None else V[tgt] - V[src] - subtract
                drops = weights[:, None] * drops
                out = np.stack([np.bincount(tgt, drops[:, a], size) - np.bincount(src, drops[:, a], size) for a in (0, 1)], axis=1)
                out[anchor] = 0.0
                return out

            def settled(G):
                norm = np.hypot(G[:, 0], G[:, 1])
                return bool(np.all(norm < gtol) and np.all(norm / scale < gtol) and alpha * float(norm.max()) < utol)

            with np.errstate(over="raise", invalid="raise", divide="raise"):
                G = laplacian(X, offsets)
                while not settled(G):
                    trace["fallback_restarts"] += 1
                    R = -G
                    Z = R / scale[:, None]
                    Z[anchor] = 0.0
                    P, rz = Z.copy(), np.sum(R * Z, axis=0)
                    for _ in range(4 * size + 16):
                        AP = laplacian(P)
                        curvature = np.sum(P * AP, axis=0)
                        step = np.divide(rz, curvature, out=np.zeros(2), where=curvature > 0)
                        X = X + step * P
                        R = R - step * AP
                        trace["fallback_cg_iterations"] += 1
                        if settled(R):
                            break
                        Z = R / scale[:, None]
                        Z[anchor] = 0.0
                        updated = np.sum(R * Z, axis=0)
                        P = Z + np.divide(updated, rz, out=np.zeros(2), where=rz > 0) * P
                        rz = updated
                    G = laplacian(X, offsets)  # true gradient; recurrence drift cannot certify
            tx.spend_fallback(size)
            for i, (x, y) in zip(nodes, X.tolist()):
                if i != self._anchor[component]:
                    tx.move(i, x, y)
        bad = self._certify(everyone, alpha, tx.spend_fallback, trace)
        if bad:
            raise _FallbackExhausted()
        tx.certified = set(tx.certified) | everyone
