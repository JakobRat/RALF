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
if TYPE_CHECKING:
    from Routing_v2.Grid import Grid
    from Routing_v2.Obstacles import Obstacles
    from PDK.PDK import PDK
    from SchematicCapture.Net import Net
    from Magic.MagicTerminal import MagicTerminal
    from Magic.MagicDie import MagicDiePin
    from Routing_v2.Route import Route

import heapq
from Routing_v2.Path import Path as RoutingPath
from Routing_v2.Obstacles import global_obstacles
from Routing_v2.Grid import global_grid
from Routing_v2.Primitives import *
from Routing_v2.Geometrics import Rectangle
import networkx as nx

DEBUG = True
USE_ASTAR_MULTI = False
import time

class Router:
    def __init__(self, path1 : RoutingPath, path2 : RoutingPath, route : Route) -> None:
        """Connect two paths (<path1>, <path2>).

        Args:
            path1 (RoutingPath): First path.
            path2 (RoutingPath): Second path.
            route (Route): Route for which a path shall be routed.
        """
        self._path1 = path1
        self._path2 = path2

        #get the vias of path1 and path2
        self._via_edges_1 = [tuple(via.edge) for via in list(filter(lambda p : type(p)==Via, path1.primitives))]
        self._via_edges_2 = [tuple(via.edge) for via in list(filter(lambda p : type(p)==Via, path2.primitives))]
        
        self._nodes = []
        self._nodes.extend(path1.nodes)
        self._nodes.extend(path2.nodes)
        self._x = set([node.coordinate[0] for node in self._nodes])
        self._y = set([node.coordinate[1] for node in self._nodes])
        
        self._route = route
        self._pdk = route._pdk
        self._net = route._net
        
        #setup the number of trials
        # ToDo: Generalize!
        self._n_trials = 5
        
        self._trial_nodes = set()

        self._route_lines_H = []
        self._route_lines_V = []
    
    def add_route_lines(self, lines_H : list, lines_V : list):
        """Add lines, which shall be in the routing-grid.

        Args:
            lines_H (list): List of horizontal grid lines (y-coordinates)
            lines_V (list): List of vertical grid lines (x-coordinates)
            
        """
        self._route_lines_H.extend(lines_H)
        self._route_lines_V.extend(lines_V)

    def route(self) -> RoutingPath | None:
        """Get a path from path1 to path2.

        Returns:
            RoutingPath | None: Path from path1 to path2, or None if no path has been found.
        """
        
        #try to find a path for n_trials.
        for n in range(self._n_trials):
            
            #get the nodes of the paths
            path1_nodes = list(filter(lambda n : n.layer != 'li', self._path1.nodes))
            path2_nodes = list(filter(lambda n : n.layer != 'li', self._path2.nodes))
            
            #setup a heap with distances between the nodes
            distances = []
            for node1 in path1_nodes:
                for node2 in path2_nodes:
                    dist = GridNode.get_distance_between(node1, node2)
                    heapq.heappush(distances, (dist, (node1, node2)))
            path = None

            if not USE_ASTAR_MULTI:
                #try each node pair until a path were found, starting by the 
                # nodes which are minimum spaced
                while path is None and len(distances)>0:
                    dist, next_nodes = heapq.heappop(distances)
                    if DEBUG:
                        print(f"Finding path for nodes {next_nodes[0]}-{next_nodes[1]} for net {self._net}.")

                    
                    start = GridNode(*next_nodes[0])
                    goal = GridNode(*next_nodes[1])
                    
                    #calculate the area which were spanned by the nodes
                    area = (min(start.coordinate[0], goal.coordinate[0]),
                            min(start.coordinate[1], goal.coordinate[1]),
                            max(start.coordinate[0], goal.coordinate[0]),
                            max(start.coordinate[1], goal.coordinate[1]))
                    

                    if self._route.get_route_planner() is None:
                        # if the route has no global route
                        # -> setup the grid, such that only obstacles in the 
                        #    area spannend by the nodes are considered
                        global_obstacles.setup_obstacle_grid_for_area(area, pdk=self._pdk, net=self._net)
                    else:
                        # Route has a global routing
                        # -> setup the grid, such that only the obstacles 
                        #    in the GCells are considered.
                        global_obstacles.setup_obstacle_grid_for_route_planner(plan=self._route.get_route_planner(), pdk=self._pdk, net=self._net)
                    
                    #add grid-lines for the start and goal node
                    global_grid.setup_grid_for_path(next_nodes[0], next_nodes[1])
                    
                    if self._route_lines_V or self._route_lines_H:
                        #if there are extra grid-lines, add them
                        global_grid.add_grid_lines(self._route_lines_V, self._route_lines_H)   

                    #find a path using the astar algorithm
                    path = self.astar(start, goal)
                    
                    if path is None:
                        print(f"No path found, trying next.")

            else:
                
                #setup the obstacles
                global_obstacles.setup_obstacle_rtree_for_net(self._net)

                #setup the grid
                global_obstacles.setup_obstacle_grid_for_pdk(self._pdk)

                lines_x = []
                lines_y = []
                for node in path1_nodes:
                    lines_x.append(node.coordinate[0])
                    lines_y.append(node.coordinate[1])

                for node in path2_nodes:
                    lines_x.append(node.coordinate[0])
                    lines_y.append(node.coordinate[1])

                global_grid.add_grid_lines(lines_x, lines_y)

                #find a path
                path = self.astar_multi(path1_nodes, path2_nodes)
                
            if path:
                # if a path were found -> break
                break
            else:
                if DEBUG:
                    print(f"No route found, trying {n}th run!")

        if path:
            # if a path were found -> return a RoutingPath
            path = RoutingPath(nodes = path, pdk = self._pdk)
        else:
            path = None
        
        return path
    
    def get_feasible_neighbors(self, node : GridNode) -> list[GridNode]:
        """Get all feasible neighbors of node <node>.

        Args:
            node (GridNode): GridNode for which the feasible neighbors should be found.
            
        Returns:
            list[GridNode] : List of all feasible grid nodes.
        """
        #get all grid-neighbors of the node
        neighbors = global_grid.get_neighbors(node)
        
        #filter 'li' nodes -> there is no 'li' routing! 
        #  ToDo generalize for other PDKs 
        neighbors = list(filter(lambda n: n.layer != 'li', neighbors)) #don't use li!
        

        assert len(neighbors)>0, f"Node {node}, has no neighbors!"

        #get the last via and bend
        last_via = self.last_via(node)
        last_bend = self.last_bend(node)

        feasible_neighbors = []

        #check each neighbor for feasibility.
        for neighbor in neighbors:
            
            cost_mult = 1 
            #if the node isn't in the global route -> increase the cost
            if not (self._route.get_route_planner() is None):
                if not self._route.get_route_planner().node_is_in_plan_area(neighbor):
                    cost_mult = 100

            #if the neighbor forms a Wire
            if neighbor.layer == node.layer:
                layer : MetalLayer

                #check if the min. dist to a bend is given
                if not (last_via is None):
                    if not self._valid_via_bend_space(last_via, (node, neighbor)):
                        continue
                
                #check if the wire intersects with an obstacle
                layer = self._pdk.metal_layers[str(node.layer)]
                
                #obstacles are stored unexpanded -> 
                # expand the wire by the minimum space 
                offset = layer.width/2 #+layer.minSpace
                
                #calc the boundary of the wire
                bound_3d = (min(neighbor.coordinate[0], node.coordinate[0])-offset,
                            min(neighbor.coordinate[1], node.coordinate[1])-offset,
                            hash(layer),
                            max(neighbor.coordinate[0], node.coordinate[0])+offset,
                            max(neighbor.coordinate[1], node.coordinate[1])+offset,
                            hash(layer))
                
                #check if the wire intersects with an obstacle
                if not global_obstacles.intersects_with_area(bound_3d):

                    #calculate the cost of the wire
                    # add the resistance of the wire to the cost
                    # -> wires with less resistance shall be preferred
                    cost = neighbor.layer.resistivity * GridNode.get_distance_between(node, neighbor)/layer.width
                    
                    # add the wire width to the cost
                    # -> wires which need less resources shall be preferred
                    cost += layer.width
                    
                    # check if the wire will form a bend
                    if node.parent:
                        if GridNode.get_direction_between(node, neighbor) != GridNode.get_direction_between(node, node.parent):
                            
                            # if the wire forms a bend, increase the cost tremendously
                            # -> a path shall be as straight as possible
                            cost *= 10
                    
                    if neighbor in self._trial_nodes:
                            # if the node were already used by a previous path-finding 
                            # increase the cost tremendously
                            # -> avoid a node that is likely to result in no path being found
                            cost *= 100

                    

                    neighbor.set_cost(cost*cost_mult)
                    feasible_neighbors.append(neighbor)
                
            else: #via

                layer1 : MetalLayer
                layer1 = self._pdk.metal_layers[str(node.layer)]
                layer2 : MetalLayer
                layer2 = self._pdk.metal_layers[str(neighbor.layer)]
                via_layer : ViaLayer
                via_layer = self._pdk.get_via_layer(layer1, layer2)

                if node.layer < neighbor.layer:
                    bottom_node = node
                    top_node = neighbor
                elif node.layer > neighbor.layer:
                    bottom_node = neighbor
                    top_node = node
                else:
                    raise ValueError(f"Trying to assign a VIA for nodes on same layer! ({node},{neighbor})")
                
                #check if the via - via space is valid
                if not (last_via is None):
                    if not self._valid_via_via_space((bottom_node, top_node), last_via):
                        continue
                
                #check if the via is valid spaced to the vias of the first path.
                valid_via_to_path = True
                for via_edge in self._via_edges_1:
                    if not self._valid_via_via_space((bottom_node, top_node), via_edge):
                            valid_via_to_path = False
                            break
                
                if not valid_via_to_path:
                    continue
                
                #check if the via is valid spaced to the vias of the second path.
                for via_edge in self._via_edges_2:
                    if not self._valid_via_via_space((bottom_node, top_node), via_edge):
                            valid_via_to_path = False
                            break
                
                if not valid_via_to_path:
                    continue
                
                #check if the distance to the last bend is valid
                if not (last_bend is None):
                    if not self._valid_via_bend_space((bottom_node, top_node), (last_bend[1], last_bend[2])):
                        continue
                
                #check if the via don't intersects with a obstacle
                #setup the areas of the via for obstacle checking
                offset_bottom = via_layer.width/2+via_layer.minEnclosure_bottom #+via_layer.bottom_layer.minSpace
                via_width_bottom = (via_layer.width+2*via_layer.minEnclosure_bottom)
                
                offset_top = via_layer.width/2+via_layer.minEnclosure_top #+via_layer.top_layer.minSpace
                via_width_top = (via_layer.width+2*via_layer.minEnclosure_top)
                
                bound_3d_bottom = (bottom_node.coordinate[0]-offset_bottom,
                                  bottom_node.coordinate[1]-offset_bottom,
                                  hash(bottom_node.layer),
                                  bottom_node.coordinate[0]+offset_bottom,
                                  bottom_node.coordinate[1]+offset_bottom,
                                  hash(bottom_node.layer))
                
                bound_3d_top = (top_node.coordinate[0]-offset_top,
                                  top_node.coordinate[1]-offset_top,
                                  hash(top_node.layer),
                                  top_node.coordinate[0]+offset_top,
                                  top_node.coordinate[1]+offset_top,
                                  hash(top_node.layer))
                
                                
                #check if the bottom plate intersects
                if not global_obstacles.intersects_with_area(bound_3d_bottom):
                    #check if the top plate intersects
                    if not global_obstacles.intersects_with_area(bound_3d_top):
                        
                        #calculate the cost of the via
                        # -> make vias at higher layers more costly 
                        # -> prefer routing on lower layers
                        # ToDo: Generalize for other PDKs!
                        cost_dict =  {'li' : 100, 'm1' : 100, 'm2' : 100, 'm3' : 200, 'm4' : 200, 'm5' : 200}
                        cost = cost_dict[str(neighbor.layer)]
                        
                        # add the width of the bottom and top plate to the cost
                        # -> prefer vias which use less resources
                        cost += via_width_bottom + via_width_top
                        
                        if neighbor in self._trial_nodes:
                            # if the node were already used by a previous path-finding 
                            # increase the cost tremendously
                            # -> avoid a node that is likely to result in no path being found
                            cost *= 100
                        
                        
                        neighbor.set_cost(cost*cost_mult)
                        feasible_neighbors.append(neighbor)

        
        #if len(feasible_neighbors)==0:
        #    print(f"No feassible neighbor for node {node} found!")

        return feasible_neighbors
    
    def _get_primitives(self, edge : GridEdge, pdk : PDK) -> Conductor:
        """Get a primitive (Via or Wire) which is defined by the GridEdge <edge>.

        Args:
            edge (GridEdge): Edges of the primitive.
            pdk (PDK): PDK of the primitive.

        Returns:
            Conductor: Primitive.
        """
        if edge.node1.layer == edge.node2.layer:
            return MetalWire(edge, width=pdk.get_layer(str(edge.node1.layer)).width)
        else:
            via_layer : ViaLayer
            via_layer = pdk.get_via_layer(edge.node1.layer, edge.node2.layer)
            return Via(edge, via_layer.width)
    
    def _valid_via_via_space(self, via1_nodes : tuple[GridNode, GridNode], via2_nodes : tuple[GridNode, GridNode]) -> bool:
        """Check if two vias are valid spaced.

        Args:
            via1_nodes (tuple[GridNode, GridNode]): Nodes forming via1.
            via2_nodes (tuple[GridNode, GridNode]): Nodes forming via2.

        Returns:
            bool: True, if they are such spaced that no spacing error occurs, otherwise False.
        """
        #sort the nodes according their layers
        via1_nodes = sorted(via1_nodes, key=lambda node : node.layer)
        via2_nodes = sorted(via2_nodes, key=lambda node : node.layer)
        via1_layer = self._pdk.get_via_layer(via1_nodes[0].layer, via1_nodes[1].layer)
        via2_layer = self._pdk.get_via_layer(via2_nodes[0].layer, via2_nodes[1].layer)
        
        #get the common layers
        common_layers = []
        for node1 in via1_nodes:
            for node2 in via2_nodes:
                if node1.layer==node2.layer:
                    common_layers.append((node1.layer, node1, node2))
        
        #check if the distances are valid
        for layer, node1, node2 in common_layers:
            pdk_layer = self._pdk.get_layer(str(layer))
            w1 = via1_layer.width
            w2 = via2_layer.width
            e1 = via1_layer.minEnclosure_bottom if layer==via1_layer.bottom_layer else via1_layer.minEnclosure_top
            e2 = via2_layer.minEnclosure_bottom if layer==via2_layer.bottom_layer else via2_layer.minEnclosure_top
            space = pdk_layer.minSpace
            
            #minimum space between, two not touching vias
            dmin = w1/2+e1+space+e2+w2/2
            
            #max space between two touching vias.
            if via1_layer == via2_layer:
                dmin_without_space = w1/2+w2/2
            else:
                dmin_without_space = w1/2+e1+e2+w2/2
            
            dx = abs(node1.coordinate[0]-node2.coordinate[0])
            dy = abs(node1.coordinate[1]-node2.coordinate[1])
            
            #stacked vias -> no spacing error
            if dx==0 and dy==0:
                return True
            
            #if the two vias are touching -> check if there is no spacing error on another layer
            if dx<=dmin_without_space and dy<=dmin_without_space:
                continue
            
            #if the vias don't touch and the min. distance is violate -> spacing error occured.
            if dx<dmin and dy<dmin:
                return False
        
        return True

    def _valid_via_bend_space(self, via_nodes : tuple[GridNode, GridNode], bend_nodes : tuple[GridNode, GridNode]) -> bool:
        """Check if the via has enough space to a bend.

        Args:
            via_nodes (tuple[GridNode, GridNode]): Nodes forming a via.
            bend_nodes (tuple[GridNode, GridNode]): Nodes of a bend, which form the parallel wire to the via. 

        Returns:
            bool: True, if valid, else False.
        """
        
        #sort the nodes according their layers
        via_nodes = sorted(via_nodes, key=lambda node : node.layer)
        via_layer = self._pdk.get_via_layer(via_nodes[0].layer, via_nodes[1].layer)
        
        assert bend_nodes[0].layer == bend_nodes[1].layer
        assert (bend_nodes[0].coordinate[0]==bend_nodes[1].coordinate[0] or
                bend_nodes[0].coordinate[1]==bend_nodes[1].coordinate[1])
        
        #get the layer of the bend
        bend_layer = self._pdk.get_layer(str(bend_nodes[0].layer))

        #get the coordinate of the via
        via_coordinate = via_nodes[0].coordinate

        #get the distances between the via and the bend nodes
        dx0 = abs(bend_nodes[0].coordinate[0]-via_coordinate[0])
        dy0 = abs(bend_nodes[0].coordinate[1]-via_coordinate[1])
        dx1 = abs(bend_nodes[1].coordinate[0]-via_coordinate[0])
        dy1 = abs(bend_nodes[1].coordinate[1]-via_coordinate[1])
        
        #if the bend nodes are aligned with the via, 
        # no min-space drc error can occor 
        if (dx0==0 and dx1==0) or (dy0==0 and dy1==0):
            return True
        
        #get the common layers
        common_layers = []
        for node1 in via_nodes:
            if node1.layer==bend_layer:
                common_layers.append((node1.layer, node1))
        
        #check if the distances are valid
        for layer, node1 in common_layers:
            pdk_layer = self._pdk.get_layer(str(layer))
            w1 = via_layer.width
            w2 = bend_layer.width
            e1 = via_layer.minEnclosure_bottom if layer==via_layer.bottom_layer else via_layer.minEnclosure_top
            space = pdk_layer.minSpace

            #setup the area of the bend
            bend_area = (min(bend_nodes[0].coordinate[0]-w2/2, bend_nodes[1].coordinate[0]-w2/2),
                         min(bend_nodes[0].coordinate[1]-w2/2, bend_nodes[1].coordinate[1]-w2/2),
                         max(bend_nodes[0].coordinate[0]+w2/2, bend_nodes[1].coordinate[0]+w2/2),
                         max(bend_nodes[0].coordinate[1]+w2/2, bend_nodes[1].coordinate[1]+w2/2))
            
            #setup the area of the via, with space
            via_area_with_space = (node1.coordinate[0]-w1/2-e1-space,
                                   node1.coordinate[1]-w1/2-e1-space,
                                   node1.coordinate[0]+w1/2+e1+space,
                                   node1.coordinate[1]+w1/2+e1+space)
            
            #setup the area of the via, without space
            via_area_without_space = (node1.coordinate[0]-w1/2-e1,
                                   node1.coordinate[1]-w1/2-e1,
                                   node1.coordinate[0]+w1/2+e1,
                                   node1.coordinate[1]+w1/2+e1)
            
            #setup rectangles
            bend_rect = Rectangle(*bend_area)
            via_rect_without_space = Rectangle(*via_area_without_space)

            #if the bend overlaps with the via, check next 
            if Rectangle.overlap(bend_rect, via_rect_without_space):
                continue
            
            via_rect_with_space = Rectangle(*via_area_with_space) 
            
            #if the bend overlaps with the via + space, -> min space is violated
            if Rectangle.overlap(bend_rect, via_rect_with_space):
                return False
        
        return True

    def heuristic(self, node : GridNode, goal : GridNode):
        pos1 = node.coordinate
        pos2 = goal.coordinate
        layer1 = hash(node.layer)
        layer2 = hash(goal.layer)
        return (abs(pos1[0]-pos2[0])+abs(pos1[1]-pos2[1])+abs(layer1-layer2))

    def heuristic_multi(self, node : GridNode, goals : list[GridNode]):
        dists = [self.heuristic(node, goal) for goal in goals]
        return min(dists)
    
    def astar_multi(self, starts : list[GridNode], goals : list[GridNode]):

        open_list = []
        closed_list = set()

        for start in starts:
            start._g = 0
            heapq.heappush(open_list, (self.heuristic_multi(start, goals), start))
        
        while open_list:
            current_cost, current_node = heapq.heappop(open_list)

            if current_node in goals:
                #goal reached, reconstruct path
                path = []
                while current_node:
                    path.append(current_node)
                    current_node = current_node.parent
                
                return path[::-1]
            
            closed_list.add(current_node)

            for neighbor in self.get_feasible_neighbors(current_node):
                if neighbor in closed_list:
                    continue

                tentative_score = current_node.g + neighbor.cost

                if tentative_score<neighbor.g or neighbor.g == 0 or (neighbor not in open_list):
                    neighbor.set_parent(current_node)
                    neighbor.set_g(tentative_score)
                    
                    if neighbor not in open_list:
                        heapq.heappush(open_list, (neighbor.g+self.heuristic_multi(neighbor, goals), neighbor))
                    else:
                        i = open_list.index(neighbor)
                        old_value = open_list.pop(i)
                        heapq.heapify(open_list)
                        heapq.heappush(open_list, (neighbor.g+self.heuristic_multi(neighbor, goals), neighbor))

        self._trial_nodes.update(closed_list)
        return None
    
    def astar(self, start : GridNode, goal : GridNode):

        open_list = []
        closed_list = set()

        start._g = 0
        heapq.heappush(open_list, (self.heuristic(start, goal), start))
        
        while open_list:
            current_cost, current_node = heapq.heappop(open_list)

            if current_node == goal:
                #goal reached, reconstruct path
                path = []
                while current_node:
                    path.append(current_node)
                    current_node = current_node.parent
                
                return path[::-1]
            
            closed_list.add(current_node)

            for neighbor in self.get_feasible_neighbors(current_node):
                if neighbor in closed_list:
                    continue

                tentative_score = current_node.g + neighbor.cost

                if tentative_score<neighbor.g or neighbor.g == 0 or (neighbor not in open_list):
                    neighbor.set_parent(current_node)
                    neighbor.set_g(tentative_score)
                    
                    if neighbor not in open_list:
                        heapq.heappush(open_list, (neighbor.g+self.heuristic(neighbor, goal), neighbor))
                    else:
                        i = open_list.index(neighbor)
                        old_value = open_list.pop(i)
                        heapq.heapify(open_list)
                        heapq.heappush(open_list, (neighbor.g+self.heuristic(neighbor, goal), neighbor))

        self._trial_nodes.update(closed_list)
        return None
    
    def last_via(self, node : GridNode) -> tuple[GridNode, GridNode]|None:
        """Get the last via on the path defined by the parents of <node>.

        Args:
            node (GridNode): Last grid node.

        Returns:
            tuple[GridNode, GridNode]|None: If there is a via, the nodes forming a via are returned, else None.
        """
        current_node = node
        while current_node:
            if current_node.parent:
                if (current_node.parent.coordinate == current_node.coordinate and 
                    abs(hash(current_node.layer)-hash(current_node.parent.layer))==1):
                    return (current_node, current_node.parent)
            current_node = current_node.parent
        return None
    
    def last_bend(self, node : GridNode) -> tuple[GridNode, GridNode, GridNode]|None:
        """Get the last bend on the path, defined py the parents of <node>.

        Args:
            node (GridNode): Grid node.

        Returns:
            tuple[GridNode, GridNode, GridNode]|None: Nodes which form a bend, if there is a bend, otherwise None.
        """
        current_node = node
        while current_node:
            if current_node.parent:
                parent = current_node.parent
                if parent.parent:
                    dir1 = GridNode.get_direction_between(current_node, parent)
                    dir2 = GridNode.get_direction_between(parent, parent.parent)
                    if dir1 != dir2 and dir1!='VIA' and dir2!='VIA':
                        return (current_node, parent, parent.parent)
                    
            current_node = current_node.parent
        return None
    
class TerminalRouter:
    def __init__(self, terminal : MagicTerminal, route : Route) -> None:
        """Connect the pins of a MagicTerminal.

        Args:
            terminal (MagicTerminal): MagicTerminal for which the pins, shall be connected.
            route (Route): Route to which the MagicTerminal belongs.
        """
        self._terminal = terminal
        self._route = route
        self._pdk = route._pdk
        self._net = route._net

        #store the pins, sorted by their coordinate
        self._pins = sorted(terminal.pins, key=lambda pin: pin.coordinate)

    def route(self) -> list[RoutingPath]:
        """Route the terminal.

        Returns:
            list[RoutingPath]: List of paths connecting the terminal pins.
        """
        if DEBUG:
            print(f"Routing terminal {self._terminal}.")

        paths = []

        if len(self._pins)>1:
            
            li_paths = []

            routing_nodes = []

            #connect pins at li to m1, and determine routing nodes
            # ToDo: Generalize for other PDKs.
            for pin in self._pins:
                node1 = None
                if pin.layer == 'li': #add a path to li if the pin is at li
                    node_li = GridNode(*pin.get_coordinate_on_grid(), pin.layer)
                    node1 = GridNode(*pin.get_coordinate_on_grid(), self._pdk.get_layer('m1'))
                    li_paths.append(RoutingPath([node1, node_li], self._pdk))

                if node1 is None:
                    node1 = GridNode(*pin.get_coordinate_on_grid(), pin.layer)
                
                routing_nodes.append(node1)
            
            #connect the pins
            for i in range(len(routing_nodes)-1):
                node1 = routing_nodes[i]
                node2 = routing_nodes[i+1]

                #find a path from node1 to node2
                path1 = RoutingPath([node1], self._pdk) 
                path2 = RoutingPath([node2], self._pdk)
                paths.append(path1)
                paths.append(path2)
            
            paths = StrategyRouter(paths, route=self._route).route()

            paths.extend(li_paths) #add the paths
        
        elif len(self._pins)==1: #there is only one pin
            pin = self._pins[0]
            if pin.layer == 'li': #add a path to li if the node is at li
                node_li = GridNode(*pin.get_coordinate_on_grid(), pin.layer)
                node1 = GridNode(*pin.get_coordinate_on_grid(), self._pdk.get_layer('m1'))
                paths.append(RoutingPath([node1, node_li], self._pdk))
            else: #add a path to the pin
                node = GridNode(*pin.get_coordinate_on_grid(), pin.layer)
                paths.append(RoutingPath([node], self._pdk))      

        else:
            pass
        

        return paths
    
    def route2(self) -> list[RoutingPath]:
        """Route the terminal.

        Returns:
            list[RoutingPath]: List of paths connecting the terminal pins.
        """
        if DEBUG:
            print(f"Routing terminal {self._terminal}.")

        paths = []

        if len(self._pins)>1:
            
            li_paths = []

            routing_nodes = []

            #connect pins at li to m1, and determine routing nodes
            # ToDo: Generalize for other PDKs.
            for pin in self._pins:
                node1 = None
                if pin.layer == 'li': #add a path to li if the pin is at li
                    node_li = GridNode(*pin.get_coordinate_on_grid(), pin.layer)
                    node1 = GridNode(*pin.get_coordinate_on_grid(), self._pdk.get_layer('m1'))
                    li_paths.append(RoutingPath([node1, node_li], self._pdk))

                if node1 is None:
                    node1 = GridNode(*pin.get_coordinate_on_grid(), pin.layer)
                
                routing_nodes.append(node1)
            
            #connect the pins
            for i in range(len(routing_nodes)-1):
                node1 = routing_nodes[i]
                node2 = routing_nodes[i+1]

                #find a path from node1 to node2
                path = Router(RoutingPath([node1], self._pdk), RoutingPath([node2], self._pdk), route=self._route).route()
                paths.append(path)
            
            paths.extend(li_paths) #add the paths
        
        elif len(self._pins)==1: #there is only one pin
            pin = self._pins[0]
            if pin.layer == 'li': #add a path to li if the node is at li
                node_li = GridNode(*pin.get_coordinate_on_grid(), pin.layer)
                node1 = GridNode(*pin.get_coordinate_on_grid(), self._pdk.get_layer('m1'))
                paths.append(RoutingPath([node1, node_li], self._pdk))
            else: #add a path to the pin
                node = GridNode(*pin.get_coordinate_on_grid(), pin.layer)
                paths.append(RoutingPath([node], self._pdk))      

        else:
            pass
        
        return paths


class StrategyRouter:
    def __init__(self, paths : list[RoutingPath], route : Route) -> None:
        """Router to connect the paths given in <path>, following the strategy, that 
            unconnected paths with minimum spacing are connected until all paths are connected.

        Args:
            paths (list[RoutingPath]): List of paths, which shall be connected.
            route (Route): Route to which the paths belong.
        """
        self._paths = paths
        self._route = route
        self._pdk = route._pdk
        self._net = route._net

        self._path_lines_H = set()
        self._path_lines_V = set()

        self._graph = nx.Graph()
        self._setup_graph()

    def _setup_graph(self):
        """Setup a connection graph, to track allready connected paths.
        """
        
        #add the paths to the graph
        self._graph.add_nodes_from(self._paths)

        #find allready connected paths
        connected_paths = []
        for i in range(len(self._paths)-1):
            for j in range(1,len(self._paths)):
                path_i = self._paths[i]
                path_j = self._paths[j]

                if RoutingPath.are_connected(path1=path_i, path2=path_j):
                    connected_paths.append((path_i, path_j))
        
        #add edges between connected paths
        self._graph.add_edges_from(connected_paths)
    
    def _add_path_to_graph(self, path : RoutingPath):
        """Add a path to the connection graph.

        Args:
            path (RoutingPath): Path which shall be added.
        """
        connected_paths = []

        for node in self._graph.nodes:
            assert isinstance(node, RoutingPath)
            if RoutingPath.are_connected(path1=path, path2=node):
                connected_paths.append((path, node))
        
        self._graph.add_edges_from(connected_paths)

    def route(self) -> list[RoutingPath]:
        """Connect the paths.

        Raises:
            ValueError: If the paths can't be connected.

        Returns:
            list[RoutingPath]: List of paths, connecting the paths of the StrategyRouter.
        """

        #get the next min. spaced and not connected path pair
        next_path_pair = self.get_next_paths_to_be_connected()
        #connect the paths until all paths are connected
        while not (next_path_pair is None):
            #find a route which connects the paths.
            router = Router(next_path_pair[0], next_path_pair[1], route=self._route)
            router.add_route_lines(list(self._path_lines_H), list(self._path_lines_V))
            path = router.route()
            
            #add the path to the connection graph
            if not (path is None):
                self._add_path_to_graph(path)
                path_lines = path.get_path_lines()
                self._path_lines_H.update(path_lines[0])
                self._path_lines_V.update(path_lines[1])

                #self._graph.add_node(path)
                #edges = [(next_path_pair[0], path), (path, next_path_pair[1])]
                #self._graph.add_edges_from(edges)
            else:
                raise ValueError("No path found!")
            
            #get the next path-pair
            next_path_pair = self.get_next_paths_to_be_connected()

        #return the new generated paths.
        new_paths = list(set(self._graph.nodes)-set(self._paths))

        return new_paths

    def get_next_paths_to_be_connected(self) -> tuple[RoutingPath, RoutingPath] | None:
        """Get the next min. spaced path-pairs which shall be connected.

        Returns:
            tuple[RoutingPath, RoutingPath] | None: Path-pairs if not all paths are connected, else None.
        """

        #find the connected components of the graph.
        components = [self._graph.subgraph(c) for c in nx.connected_components(self._graph)]

        min_distance = float('inf')
        path_pair = None

        #if there are at least two not connected sets
        if len(components)>1:
            #find the path - pairs which are min. spaced.
            # iterate over all pairs of unconnected subgraphs
            for i in range(len(components)-1):
                for j in range(i+1, len(components)):
                    #iterate over all pairs of paths
                    #between the unconnected subgraphs
                    for p1 in components[i].nodes:
                        for p2 in components[j].nodes:
                            dist = RoutingPath.get_minimum_distance_between(p1, p2)
                            if dist < min_distance:
                                #save the path-pair
                                min_distance = dist
                                path_pair = (p1, p2)
            
            return path_pair
        else:
            return None
    

class DiePinRouter:
    def __init__(self, die_pins : list[MagicDiePin], paths : list[RoutingPath], route : Route) -> None:
        """Router to connect die pins, to paths (a routing of a net).

        Args:
            die_pins (list[MagicDiePin]): List of die pins.
            paths (list[RoutingPath]): List of paths.
            route (Route): Route to which the pins and paths belong.
        """
        self._die_pins = die_pins
        self._paths = paths
        self._route = route
        self._pdk = route._pdk
        self._net = route._net

        self._graph = nx.Graph()
        self._setup_graph()

        assert self._paths_connected(), "Can't route die-pins if internal net isn't fully connected!"

    def _setup_graph(self):
        """Setup a connection graph.
        """
        self._graph.add_nodes_from(self._paths)

        connected_paths = []
        for i in range(len(self._paths)-1):
            for j in range(1,len(self._paths)):
                path_i = self._paths[i]
                path_j = self._paths[j]

                if RoutingPath.are_connected(path1=path_i, path2=path_j):
                    connected_paths.append((path_i, path_j))
        
        self._graph.add_edges_from(connected_paths)
    
    def _paths_connected(self) -> bool:
        """Check if all paths are connected.

        Returns:
            bool: True, if connected, otherwise False.
        """
        components = [self._graph.subgraph(c) for c in nx.connected_components(self._graph)]

        return len(components)==1
    
    def _get_min_dist_path(self, die_path : RoutingPath) -> RoutingPath:
        """Get the path which is minimum spaced to a die-pin.

        Args:
            die_path (RoutingPath): Path of the die pin.

        Returns:
            RoutingPath: Min. spaced path.
        """
        min_dist = float('inf')
        min_dist_path = None
        for path in self._paths:
            dist = RoutingPath.get_minimum_distance_between(path, die_path)
            if dist < min_dist:
                min_dist = dist
                min_dist_path = path
        
        return min_dist_path
            

    def route(self) -> list[RoutingPath]:
        """Connect the die-pins with paths.

        Raises:
            ValueError: If the die-pins cann't be connected to the paths.

        Returns:
            list[RoutingPath]: List of paths, connecting the paths with the die-paths.
        """
        route_order = sorted(self._die_pins, key=lambda pin : pin.coordinate)

        die_paths = [RoutingPath([GridNode(*pin.coordinate, pin.layer)], pdk=self._pdk) for pin in route_order]
        paths = []
        for die_path in die_paths:
            min_dist_path = self._get_min_dist_path(die_path)
            path = Router(die_path, min_dist_path, route=self._route).route()
            if path:
                paths.append(path)
                self._paths.append(path)
            else:
                raise ValueError(f"No path for die-pin of net {self._net} found!")
        
        return paths

