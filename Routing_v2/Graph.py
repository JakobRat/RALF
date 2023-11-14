
import typing

class Graph:
    def __init__(self) -> None:
        self._adjacency = {}

    def add_node(self, node):
        if isinstance(node, typing.Hashable):
            if not (node in self._adjacency):
                self._adjacency[node] = []
        else:
            raise ValueError("A node must be hashable!")
    
    def add_edge(self, node1, node2):
        if isinstance(node1, typing.Hashable) and isinstance(node2, typing.Hashable):
            self.add_node(node1)
            self.add_node(node2)
            if not (node2 in self._adjacency[node1]):
                self._adjacency[node1].append(node2)
            
            if not (node1 in self._adjacency[node2]):
                self._adjacency[node2].append(node1)
    
    @property
    def adjacency(self) -> dict:
        return self._adjacency
    
    def get_neighbors(self, node) -> list:
        try:
            return self._adjacency[node]
        except:
            raise ValueError(f"Node {node} not in graph!")
    
    @property
    def nodes(self) -> list:
        return list(self._adjacency.keys())
    
