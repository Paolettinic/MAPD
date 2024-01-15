from typing import Union, List
from .task import Task


class TaskAgentVertex:
    def __init__(self, vertex_id: int, data: Union[int, Task]):
        self.vertex_id: int = vertex_id
        self.data = data

    def __hash__(self):
        return self.vertex_id

    def __eq__(self, other):
        return isinstance(other, TaskAgentVertex) and other.data == self.data

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Vertex[{self.vertex_id=},{self.data=}]"


class TaskAgentEdge:
    def __init__(self, v1: TaskAgentVertex, v2: TaskAgentVertex, weight: float = 0):
        self.v1 = v1
        self.v2 = v2
        self.weight = weight

    def get_components(self):
        return self.v1, self.v2, self.weight

    def __hash__(self):
        return hash(f"{self.v1.vertex_id},{self.v2.vertex_id},{self.weight}")

    def __eq__(self, other):
        return (
                isinstance(other, TaskAgentEdge) and
                self.v1 == other.v1 and
                self.v2 == other.v2 and
                self.weight == other.weight
        )


class TaskAgentGraph:
    def __init__(self):
        self.vertices: List[TaskAgentVertex] = []
        self.edges: List[TaskAgentEdge] = []

    def add_vertex(self, vertex: TaskAgentVertex):
        self.vertices.append(vertex)

    def add_edge(self, edge: TaskAgentEdge):
        if edge.v1 in self.vertices and edge.v2 in self.vertices:
            self.edges.append(edge)
        else:
            raise RuntimeError("In order to add an edge, its vertices must first be added to the graph")

    def get_distance_matrix(self):
        #empty_matrix = [[0 for _ in self.vertices] for _ in self.vertices]
        import numpy as np
        distance_matrix = np.zeros((len(self.vertices),len(self.vertices)))

        for edge in self.edges:
            v1, v2, weight = edge.get_components()
            distance_matrix[v1.vertex_id][v2.vertex_id] = weight
        #print(distance_matrix)
        return distance_matrix

    # def __getitem__(self, item):
    #     if item in self.vertices:
    #         return self.vertices[item]
    #     else:
    #         raise IndexError("The specified node is not present in the graph")
