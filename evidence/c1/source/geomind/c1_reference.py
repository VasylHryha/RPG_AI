"""Independent sparse anchored least-squares control using conjugate gradients.

No candidate preparation/dynamics imports. Dense LS validates this reference
at small sizes; full reference work and nonconvergence are reported.
"""

from time import perf_counter

import numpy as np

from .geometry import Answer


class SparseLeastSquares:
    def __init__(self, observation, tolerance=1e-11, max_iterations=20000):
        started = perf_counter()
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
        self.edge_visits = len(rows)

        def multiply(vector):
            full = np.zeros(len(names))
            full[free] = vector
            drops = weight * (full[right] - full[left])
            result = np.bincount(right, weights=drops, minlength=len(names)) - np.bincount(left, weights=drops, minlength=len(names))
            self.edge_visits += len(rows)
            return result[free]

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
            while len(residual) and float(np.max(np.abs(residual))) >= tolerance and iteration < max_iterations:
                image = multiply(direction)
                denominator = float(direction @ image)
                if denominator <= 0 or not np.isfinite(denominator):
                    self.status = "NOT_CONVERGED"
                    break
                step = product / denominator
                x += step * direction
                residual -= step * image
                iteration += 1
                if float(np.max(np.abs(residual))) < tolerance:
                    # Check actual residual; recurrence drift cannot certify a solve.
                    residual = rhs[free, axis] - multiply(x)
                    if float(np.max(np.abs(residual))) < tolerance:
                        break
                    z = residual / diagonal[free]
                    product = float(residual @ z)
                    direction = z.copy()
                    continue
                z = residual / diagonal[free]
                new_product = float(residual @ z)
                direction = z + (new_product / product) * direction
                product = new_product
            if len(residual) and float(np.max(np.abs(rhs[free, axis] - multiply(x)))) >= tolerance:
                self.status = "NOT_CONVERGED"
            coordinates[free, axis] = x
            self.iterations.append(iteration)
        self.coordinates = dict(zip(names, coordinates))
        self.components = dict(zip(names, labels))
        error = coordinates[right] - coordinates[left] - offsets
        self.energy = float(0.5 * np.sum(weight[:, None] * error ** 2))
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
