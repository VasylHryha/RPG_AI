"""Independent sparse anchored least-squares control using conjugate gradients.

No candidate preparation/dynamics imports. Dense LS validates this reference
at small sizes; full reference work and nonconvergence are reported.
"""

from time import perf_counter

import numpy as np

from .geometry import Answer, finite_number


class SparseLeastSquares:
    def __init__(self, observation, tolerance=1e-11, max_iterations=20000):
        started = perf_counter()
        if not finite_number(tolerance) or tolerance <= 0 or type(max_iterations) is not int or max_iterations < 1:
            raise ValueError("Positive finite tolerance and integer reference budget required")
        observation.validate()
        names = sorted(observation.nodes)
        lookup = {name: i for i, name in enumerate(names)}
        parent = list(range(len(names)))

        def root(node):
            while parent[node] != node:
                parent[node] = parent[parent[node]]
                node = parent[node]
            return node

        rows = [(lookup[e.source], lookup[e.target], e.weight, e.offset) for e in observation.edges]
        for left, right, weight, offset in rows:
            a, b = root(left), root(right)
            parent[max(a, b)] = min(a, b)
        labels = [root(i) for i in range(len(names))]
        anchor_set = set(labels)
        free = np.array([i for i in range(len(names)) if i not in anchor_set], dtype=np.int64)
        left = np.array([r[0] for r in rows], dtype=np.int64)
        right = np.array([r[1] for r in rows], dtype=np.int64)
        weight = np.array([r[2] for r in rows], dtype=np.float64)
        offsets = np.array([r[3] for r in rows], dtype=np.float64).reshape(-1, 2)
        rhs = np.zeros((len(names), 2))
        for i, j, w, d in rows:
            rhs[i] -= w * np.asarray(d)
            rhs[j] += w * np.asarray(d)
        diagonal = np.bincount(left, weights=weight, minlength=len(names)) + np.bincount(right, weights=weight, minlength=len(names))
        if not np.isfinite(rhs).all() or not np.isfinite(diagonal).all():
            raise ValueError("Reference weighted arithmetic overflow")
        self.edge_visits = len(rows)

        def multiply(vector):
            full = np.zeros(len(names))
            full[free] = vector
            drops = weight * (full[right] - full[left])
            result = np.bincount(right, weights=drops, minlength=len(names)) - np.bincount(left, weights=drops, minlength=len(names))
            self.edge_visits += len(rows)
            if not np.isfinite(result).all():
                raise ValueError("Nonfinite reference matrix product")
            return result[free]

        def converged(residual):
            return not len(residual) or (np.isfinite(residual).all() and float(np.max(np.abs(residual))) < tolerance and float(np.max(np.abs(residual) / diagonal[free])) < tolerance)

        coordinates = np.zeros((len(names), 2))
        self.iterations = []
        self.status = "PASS"
        for axis in range(2):
            x = np.zeros(len(free))
            residual = rhs[free, axis].copy()
            z = residual / diagonal[free]
            direction = z.copy()
            product = float(residual @ z)
            iteration = 0
            while not converged(residual) and iteration < max_iterations:
                image = multiply(direction)
                denominator = float(direction @ image)
                if denominator <= 0 or not np.isfinite(denominator):
                    self.status = "NOT_CONVERGED"
                    break
                step = product / denominator
                x += step * direction
                residual -= step * image
                iteration += 1
                if converged(residual):
                    # Check actual residual; recurrence drift cannot certify a solve.
                    residual = rhs[free, axis] - multiply(x)
                    if converged(residual):
                        break
                    z = residual / diagonal[free]
                    product = float(residual @ z)
                    direction = z.copy()
                    continue
                z = residual / diagonal[free]
                new_product = float(residual @ z)
                direction = z + (new_product / product) * direction
                product = new_product
            if not converged(rhs[free, axis] - multiply(x)):
                self.status = "NOT_CONVERGED"
            coordinates[free, axis] = x
            self.iterations.append(iteration)
        self.coordinates = dict(zip(names, coordinates))
        self.components = dict(zip(names, labels))
        error = coordinates[right] - coordinates[left] - offsets
        self.energy = float(0.5 * np.sum(weight[:, None] * error ** 2))
        if not finite_number(self.energy):
            raise ValueError("Nonfinite reference residual energy")
        self.numeric_workspace_bytes = sum(a.nbytes for a in (left, right, weight, offsets, rhs, diagonal, coordinates))
        self.build_seconds = perf_counter() - started

    def query(self, source, target):
        if self.status != "PASS":
            return Answer("NOT_CONVERGED")
        if source not in self.coordinates or target not in self.coordinates:
            return Answer("UNKNOWN")
        if self.components[source] != self.components[target]:
            return Answer("UNIDENTIFIABLE")
        return Answer("OK", tuple(self.coordinates[target] - self.coordinates[source]))


class IncrementalCompiled:
    """Strongest simple incremental baseline for consistent additive updates (R4 section 6).

    Compiled coordinates per component (its own BFS), union-by-size translation
    on bridges, O(1) placement of new nodes and an O(1) consistency check for an
    edge inside a component. Compiled coordinates cannot represent a
    contradiction, so such an update refuses with NOT_CONVERGED; a least-squares
    solve is the comparison for that kind. Imports nothing from the candidate.
    """

    def __init__(self, observation, tolerance=1e-9):
        observation.validate()
        self.tolerance = tolerance
        self.coordinates, self.component, self.members = {}, {}, {}
        neighbors = {node: [] for node in observation.nodes}
        for e in observation.edges:
            neighbors[e.source].append((e.target, float(e.offset[0]), float(e.offset[1])))
            neighbors[e.target].append((e.source, -float(e.offset[0]), -float(e.offset[1])))
        for root in sorted(observation.nodes):
            if root in self.coordinates:
                continue
            self.coordinates[root] = (0.0, 0.0)
            self.component[root] = root
            self.members[root] = [root]
            pending = [root]
            while pending:
                node = pending.pop()
                x, y = self.coordinates[node]
                for other, dx, dy in neighbors[node]:
                    if other not in self.coordinates:
                        self.coordinates[other] = (x + dx, y + dy)
                        self.component[other] = root
                        self.members[root].append(other)
                        pending.append(other)
        for e in observation.edges:
            if self._residual(e) > tolerance:
                raise ValueError("Incremental compiled baseline requires consistent saved constraints")

    def _residual(self, e):
        (xs, ys), (xt, yt) = self.coordinates[e.source], self.coordinates[e.target]
        return float(np.hypot(xt - xs - e.offset[0], yt - ys - e.offset[1]))

    def apply(self, added_nodes, added_edges):
        """Atomic additive update; returns (status, operations)."""
        undo, operations = [], len(added_nodes) + len(added_edges)
        for node in added_nodes:
            self.coordinates[node] = (0.0, 0.0)
            self.component[node] = node
            self.members[node] = [node]
            undo.append(lambda node=node: (self.coordinates.pop(node), self.component.pop(node), self.members.pop(node)))
        for e in added_edges:
            a, b = self.component[e.source], self.component[e.target]
            if a == b:
                if self._residual(e) > self.tolerance:
                    for step in reversed(undo):
                        step()
                    return "NOT_CONVERGED", operations
                continue
            (xs, ys), (xt, yt) = self.coordinates[e.source], self.coordinates[e.target]
            # Move the smaller component so that x_target - x_source = offset.
            if len(self.members[a]) <= len(self.members[b]):
                moving, keep, sx, sy = a, b, xt - xs - e.offset[0], yt - ys - e.offset[1]
            else:
                moving, keep, sx, sy = b, a, e.offset[0] - (xt - xs), e.offset[1] - (yt - ys)
            moved = self.members[moving]
            operations += len(moved)
            old = [(node, self.coordinates[node]) for node in moved]
            for node in moved:
                x, y = self.coordinates[node]
                self.coordinates[node] = (x + sx, y + sy)
                self.component[node] = keep
            size = len(self.members[keep])
            self.members[keep].extend(moved)
            del self.members[moving]

            def restore(old=old, moving=moving, keep=keep, size=size, moved=moved):
                for node, value in old:
                    self.coordinates[node] = value
                    self.component[node] = moving
                del self.members[keep][size:]
                self.members[moving] = moved
            undo.append(restore)
        return "PASS", operations

    def query(self, source, target):
        if source not in self.coordinates or target not in self.coordinates:
            return Answer("UNKNOWN")
        if self.component[source] != self.component[target]:
            return Answer("UNIDENTIFIABLE")
        (xs, ys), (xt, yt) = self.coordinates[source], self.coordinates[target]
        return Answer("OK", (xt - xs, yt - ys))
