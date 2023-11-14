# ========================================================================
#
# SPDX-FileCopyrightText: 2023 Jakob Ratschenberger
# Johannes Kepler University, Institute for Integrated Circuits
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-License-Identifier: Apache-2.0
# ========================================================================

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
    
