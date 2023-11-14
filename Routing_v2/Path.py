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

from __future__ import annotations
from typing import TYPE_CHECKING

from Routing_v2.Primitives import GridNode, GridEdge, MetalWire, Via

if TYPE_CHECKING:
    from PDK.PDK import PDK, ViaLayer
    from Routing_v2.Primitives import Conductor

from itertools import count
import networkx as nx
import copy

import numpy as np
from PDK.PDK import MetalLayer

class Path:
    """Class to store a routing path.
    """
    #setup a counter to provide a unique id for each path.
    counter = count()
    def __init__(self, nodes : list[GridNode], pdk : PDK) -> None:
        """Class to store a path formed by GridNodes.
            Path = nodes[0]<->nodes[1]<->nodes[2]<->....
        Args:
            nodes (list[GridNode]): List of GridNodes forming the path.
            pdk (PDK): PDK which is used for the path. 
        """
        self._nodes = nodes
        self._id = Path.counter.__next__()
        self._pdk = copy.deepcopy(pdk)

        #setup the graph of the path
        self._graph = nx.Graph()
        self._setup_graph()

        #setup the primitives of the path
        self._primitives_graph = nx.Graph()
        self._setup_primitives()

    def _setup_graph(self):
        """Setup a graph for the path.
        """
        if len(self._nodes)>1:
            edges = []
            for i in range(1,len(self._nodes)):
                node1 = self._nodes[i-1]
                node2 = self._nodes[i]
                edges.append((node1, node2))
            
            self._graph.add_edges_from(edges)
        else:
            assert len(self._nodes)>0
            self._graph.add_node(self._nodes[0])

    def _setup_primitives(self):
        """Setup the primitives of the path.
        """
        if len(self._nodes)>1:
            #get a list of neighboring nodes and their direction
            #nodes = [[node1, node2, direction(node1, node2)],...]
            nodes = [[self._nodes[0], self._nodes[1], GridNode.get_direction_between(self._nodes[0], self._nodes[1])]]
            for i in range(2, len(self._nodes)):
                last_path = nodes[-1]
                last_direction = last_path[2]
                last_node = last_path[1]
                act_node = self._nodes[i]
                act_dir = GridNode.get_direction_between(act_node, last_node)

                if act_dir == last_direction and act_dir != 'VIA':
                    #if the actual direction is the same as the last
                    #change the last node of the actual "subpath" to the actual node
                    last_path[1] = act_node
                else:
                    #direction changed -> add the path to the nodes
                    nodes.append([last_node, act_node, act_dir])
            
            #setup the primitives
            primitives = []
            for node, i in zip(nodes, range(len(nodes))):
                if node[2]=='VIA': #if the node is a via

                    via = Via(GridEdge(node[0], node[1]))
                    #check if the via is on top of another via
                    if i>1:
                        if nodes[i-1][2]=='VIA':
                            bottom_plate = via.bottom_plate
                            bottom_plate_area = bottom_plate.area
                            bottom_plate_layer = bottom_plate.layer
                            assert type(bottom_plate_layer)==MetalLayer
                            
                            #if the area is to small, change the width of the bottom plate
                            if bottom_plate.area < bottom_plate_layer.minArea:
                                new_width = np.ceil(np.sqrt(bottom_plate_layer.minArea)/2.)*2
                                bottom_plate.set_width(new_width)

                    primitives.append(via)
                else:
                    wire = MetalWire(GridEdge(node[0], node[1]), width=self.pdk.get_layer(str(node[0].layer)).width)
                    if i>1 and i+1<len(nodes):
                        via = None
                        if nodes[i-1][2]=='VIA': #VIA where placed before the wire
                            via = primitives[-1]
                        elif nodes[i+1][2]=='VIA': #VIA where placed after wire
                            via = Via(GridEdge(nodes[i+1][0], nodes[i+1][1]))
                        
                        if not (via is None): #if there is a neighboring via, check the length
                            common_layer = wire.layer
                            common_plate = 'BOTTOM' if via.bottom_plate.layer == common_layer else 'TOP'
                            via_layer : ViaLayer
                            via_layer = via.layer
                            enclosure = via_layer.minEnclosure_bottom if common_plate=='BOTTOM' else via_layer.minEnclosure_top

                            minL = via_layer.width/2 + enclosure + common_layer.minSpace + wire.width/2

                            if wire.length<minL:
                                #print(f"Updating width for wire {wire}.")
                                wire.set_width(via_layer.width + 2*enclosure)
                                wire_width = self.pdk.get_layer(str(node[0].layer)).width
                                wire.set_left_offset(wire_width/2)
                                wire.set_right_offset(wire_width/2)

                    primitives.append(wire)

            assert len(primitives)>0, "There must be at least one primitive!"
            
            edges = []
            for i in range(1, len(primitives)):
                edges.append((primitives[i-1], primitives[i]))
            
            if len(primitives)>1:
                self._primitives_graph.add_edges_from(edges)
            else:
                self._primitives_graph.add_node(primitives[0])

    def get_path_lines(self) -> tuple[list,list]:
        """Get lines which build up the path.

        Returns:
            tuple[list,list]: (Horizontal lines (y-coordinates), Vertical lines (x-coordinates))
        """
        lines_H = []
        lines_V = []
        for primitive in self.primitives:
            if type(primitive)==MetalWire:
                if primitive.direction == 'H':
                    lines_H.append(primitive.edge.node1.coordinate[1])
                elif primitive.direction == 'V':
                    lines_V.append(primitive.edge.node1.coordinate[0])
                else:
                    pass
        return (list(set(lines_H)), list(set(lines_V)))
    @property
    def nodes(self) -> list[GridNode]:
        """Get the nodes of the path.

        Returns:
            list[GridNode]: List of path nodes.
        """
        return self._nodes

    @property
    def graph(self) -> nx.Graph:
        """Get the graph of the path.

        Returns:
            nx.Graph: Graph describing the path.
        """
        return self._graph
    
    @property
    def pdk(self) -> PDK:
        """Get the PDK of the path.

        Returns:
            PDK: PDK
        """
        return self._pdk
    
    @property
    def length(self) -> float:
        """Get the length of the path.

        Returns:
            float: Length of the path
        """
        l = 0
        for i in range(1, len(self._nodes)):
            l += GridNode.get_distance_between(self._nodes[i-1], self._nodes[i])
        
        return l
    
    @property
    def primitives(self) -> list[Conductor]:
        """Get the primitives of the path.

        Returns:
            list[Conductor]: List of conductors.
        """
        return list(self._primitives_graph.nodes)

    def get_wire_length(self) -> float:
        """Get the wire-length of the path.

        Returns:
            float: Wire-length of the path
        """
        l = 0
        for i in range(1, len(self._nodes)):
            node1 = self._nodes[i-1]
            node2 = self._nodes[i]
            if node1.layer==node2.layer:
                l += GridNode.get_distance_between(node1, node2)
        
        return l

    def get_number_of_vias(self) -> int:
        """Get the number of vias of the path.

        Returns:
            int: _description_
        """
        v = 0
        for i in range(1, len(self._nodes)):
            node1 = self._nodes[i-1]
            node2 = self._nodes[i]
            if node1.layer!=node2.layer:
                v += 1
        
        return v
    
    def plot(self, ax):
        """Plot the path on axis <ax>.

        Args:
            ax (axis): Axis on which the path shall be plotted.
        """
        for primitive in self._primitives_graph.nodes:
            primitive.plot(ax)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"

    def __hash__(self) -> int:
        return self._id
    
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Path) and self._id == __value._id
    
    @staticmethod
    def are_connected(path1 : Path, path2: Path) -> bool:
        """Check if two paths are connected.

        Args:
            path1 (Path): First path.
            path2 (Path): Second path.

        Returns:
            bool: True, if the paths are connected, otherwise False.
        """
        #setup sets from the nodes
        nodes1 = set(path1.nodes)
        nodes2 = set(path2.nodes)

        #check if there are any intersections
        intersection = nodes1.intersection(nodes2)

        #if there are intersections -> the paths are connected
        if len(intersection)>0:
            return True
        else:
            return False

    @staticmethod
    def get_intersections(path1 : Path, path2 : Path) -> list[GridNode]:
        """Get the intersecting nodes of path1 and path2.

        Args:
            path1 (Path): First path.
            path2 (Path): Second path.

        Returns:
            list[GridNode]: List of intersecting path nodes.
        """
        nodes1 = set(path1.nodes)
        nodes2 = set(path2.nodes)

        intersection = nodes1.intersection(nodes2)
        return list(intersection)
    
    @staticmethod
    def get_minimum_distance_between(path1 : Path, path2 : Path) -> float:
        """Get the minimum L1 distance between grid nodes of path1 and path2.

        Args:
            path1 (Path): First path
            path2 (Path): Second path

        Returns:
            float: Min. distance.
        """
        nodes1 = sorted(path1.nodes, key = lambda node: tuple(node))
        nodes2 = sorted(path2.nodes, key = lambda node: tuple(node))
        min_dist = float('inf')
        #iterate over all nodes, and store the minimum distance.
        for node1 in nodes1:
            for node2 in nodes2:
                dist = GridNode.get_distance_between(node1, node2)
                if dist<min_dist:
                    min_dist = dist
        
        return min_dist


class StraightPath(Path):
    def __init__(self, nodes: list[GridNode], pdk : PDK) -> None:
        """Class to store a Straight-Path. 
        A straight path is a path, where all nodes form a straight line on the same layer.

        Args:
            nodes (list[GridNode]): List of nodes.
        """
        assert StraightPath(nodes=nodes), "Nodes do not form a straight path!"
        if len(nodes)>1:
            nodes = [nodes[0], nodes[-1]]
        
        super().__init__(nodes=nodes, pdk=pdk)
        self._grid_edge = GridEdge(nodes[0], nodes[1])

    @staticmethod
    def is_straight_path(nodes : list[GridNode]) -> bool:
        """Check if the nodes form a straight path.

        Args:
            nodes (list[GridNode]): List of nodes forming a path.

        Returns:
            bool: True if the straight, otherwise False
        """

        x_aligned = True
        y_aligned = True

        for i in range(1,len(nodes)):
            node1 = nodes[i-1]
            node2 = nodes[i]

            x_aligned = x_aligned and node1.coordinate[0]==node2.coordinate[0] and node1.layer == node2.layer
            y_aligned = y_aligned and node1.coordinate[1]==node2.coordinate[1] and node1.layer == node2.layer
        
        return x_aligned or y_aligned
            
class ViaPath(Path):
    def __init__(self, nodes: list[GridNode], pdk : PDK) -> None:
        assert len(nodes)==2, "Only two nodes can form a Via!"
        assert not (pdk.get_via_layer(nodes[0].layer, nodes[1].layer) is None), "Nodes are not at neighboring layers!"
        assert nodes[0].coordinate == nodes[1].coordinate
        super().__init__(nodes)

        self._grid_edge = GridEdge(nodes[0], nodes[1])

    