"""Independent controls: BFS compilation, dense anchored LS, direct edge lookup.

No candidate internals are used. Dense matrices belong only to this reference.
"""

from collections import deque
from time import perf_counter

import numpy as np

from .geometry import Answer


class CompiledCoordinates:
    def __init__(self, observation):
        started = perf_counter()
        observation.validate()
        neighbors = {node: [] for node in observation.nodes}
        for edge in observation.edges:
            d = np.array(edge.offset)
            neighbors[edge.source].append((edge.target, d))
            neighbors[edge.target].append((edge.source, -d))
        self.coordinates, self.components = {}, {}
        self.edge_visits = 0
        for root in sorted(observation.nodes):
            if root in self.coordinates:
                continue
            self.coordinates[root] = np.zeros(2)
            self.components[root] = root
            queue = deque([root])
            while queue:
                node = queue.popleft()
                for target, offset in neighbors[node]:
                    self.edge_visits += 1
                    if target not in self.coordinates:
                        self.coordinates[target] = self.coordinates[node] + offset
                        self.components[target] = root
                        queue.append(target)
        self.residual_max = max((float(np.linalg.norm(self.coordinates[e.target] - self.coordinates[e.source] - e.offset)) for e in observation.edges), default=0.0)
        self.build_seconds = perf_counter() - started

    def query(self, source, target):
        if source not in self.coordinates or target not in self.coordinates:
            return Answer("UNKNOWN")
        if self.components[source] != self.components[target]:
            return Answer("UNIDENTIFIABLE")
        return Answer("OK", tuple(self.coordinates[target] - self.coordinates[source]))


class LeastSquares:
    def __init__(self, observation):
        started = perf_counter()
        # Reference discovers connectivity using union-find, independently of C0.
        observation.validate()
        nodes = sorted(observation.nodes)
        index = {node: i for i, node in enumerate(nodes)}
        parent = list(range(len(nodes)))

        def find(i):
            while parent[i] != i:
                i = parent[i]
            return i

        for edge in observation.edges:
            a, b = find(index[edge.source]), find(index[edge.target])
            parent[max(a, b)] = min(a, b)
        labels = [find(i) for i in range(len(nodes))]
        anchors = set(labels)
        free = [i for i in range(len(nodes)) if i not in anchors]
        matrix = np.zeros((len(observation.edges), len(nodes)))
        rhs = np.zeros((len(observation.edges), 2))
        for row, edge in enumerate(observation.edges):
            scale = np.sqrt(edge.weight)
            matrix[row, index[edge.source]] = -scale
            matrix[row, index[edge.target]] = scale
            rhs[row] = scale * np.array(edge.offset)
        coordinates = np.zeros((len(nodes), 2))
        if free:
            coordinates[free] = np.linalg.lstsq(matrix[:, free], rhs, rcond=None)[0]
        self.coordinates = dict(zip(nodes, coordinates))
        self.components = dict(zip(nodes, labels))
        residual = matrix @ coordinates - rhs
        self.energy = float(0.5 * np.sum(residual ** 2))
        self.matrix_bytes = matrix.nbytes + rhs.nbytes
        self.build_seconds = perf_counter() - started

    def query(self, source, target):
        if source not in self.coordinates or target not in self.coordinates:
            return Answer("UNKNOWN")
        if self.components[source] != self.components[target]:
            return Answer("UNIDENTIFIABLE")
        return Answer("OK", tuple(self.coordinates[target] - self.coordinates[source]))


class DirectEdges:
    def __init__(self, observation):
        started = perf_counter()
        observation.validate()
        self.nodes = set(observation.nodes)
        self.offsets = {}
        for edge in observation.edges:
            self.offsets.setdefault((edge.source, edge.target), edge.offset)
            self.offsets.setdefault((edge.target, edge.source), tuple(-v for v in edge.offset))
        self.build_seconds = perf_counter() - started

    def query(self, source, target):
        if source not in self.nodes or target not in self.nodes:
            return Answer("UNKNOWN")
        if source == target:
            return Answer("OK", (0.0, 0.0))
        value = self.offsets.get((source, target))
        return Answer("OK", value) if value is not None else Answer("UNKNOWN")
