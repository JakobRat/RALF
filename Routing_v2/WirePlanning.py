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
    from Routing_v2.Route import Route
    from Routing_v2.Primitives import GridNode
    from Magic.MagicTerminal import MagicTerminal, MagicPin

from Routing_v2.PlanningGraph import PlanningGraph, Tile
from Routing_v2.Path import Path
from Routing_v2.TileRouter import TileRouter

import networkx as nx
import heapq
from tqdm import tqdm

import matplotlib.pyplot as plt
from matplotlib import cm
import  matplotlib.patches as mpatches


class WirePlanner:
    """Class to plan the wires for multiple nets.
    """
    def __init__(self, routes : list[Route], planning_graph : PlanningGraph) -> None:
        """Plan the wires of the routes in <routes>, on planning graph <planning_graph>.

        Args:
            routes (list[Route]): List of routes.
            planning_graph (PlanningGraph): Planning graph.
        """
        self._routes = routes
        self._planning_graph = planning_graph
        #setup for each route a planner.
        self._route_planners : dict[Route, RoutePlanner]
        self._route_planners = {}
        self._setup_routeplanners() 

        self.log = {'penalty' : [],
               'crossing_nets' : [],
               'overflow' : []}
        
    def _setup_routeplanners(self):
        """Setup a route planner for each route.
        """
        for route in self._routes:
            self._route_planners[route] = RoutePlanner(route=route, planning_graph=self._planning_graph)
            route.set_route_planner(self._route_planners[route])

    def plan_routes(self, n_iterations : int = 1):
        """Plan the routes for n_iterations.

        Args:
            n_iterations (int, optional): Number of planning iterations. Defaults to 1.
        """
        
        
        super_pbar = tqdm(range(n_iterations), desc = "Wireplanning")
        for i in super_pbar:
            
            #get the route order
            route_order = self._get_route_order()

            #plan each route
            pbar = tqdm(route_order, desc="Planning route", leave=False)
            for route in pbar:
                pbar.set_description(f"Planning route {route}")
                route_planner = self._route_planners[route]
                route_planner.plan_route()

            #set the penalty for the next planning stage
            self._planning_graph.set_penalty()

            #print stats of actual round
            penalty = round(self._planning_graph.get_total_penalty(),2)
            crossing_nets = self._planning_graph.get_total_crossing_nets()
            overflow = round(self._planning_graph.get_total_overflow_percentage(),2)
            self.log['penalty'].append(penalty)
            self.log['crossing_nets'].append(crossing_nets)
            self.log['overflow'].append(overflow)

            super_pbar.set_postfix_str(f"#Crossing-Net-Tiles: {crossing_nets}, Total Penalty: {penalty}, Total Overflow percentage: {overflow}")

        
    def _get_route_order(self) -> list[Route]:
        """Get the order of the routes, for the planning.
            Starting by the route whose route-plan maximizes 
                
                FOM(route-plan)=length(route-plan)+congestion(route-plan).

        Returns:
            list[Route]: List of routes, describing the route order.
        """

        #determine for each route the FOM and push it on the heap
        order = []
        i = 0
        for route, route_plan in self._route_planners.items():
            fom = 0
            if route_plan.has_plan():
                fom = route_plan.get_plan_length() + route_plan.get_plan_congestion()

            heapq.heappush(order, (fom, i, route))
            i += 1

        #sort the list in desc order.
        route_order = []
        #for item in order:
        #    route_order.insert(0, item[2])
        while len(order):
            route_order.insert(0, heapq.heappop(order)[2])
    
        return route_order

    def plot(self, plot_only : list[str] = []):
        """Plot the wire plan.

        Args:
            plot_only (list[str], optional): List of Route-plan names which shall be plotted. Defaults to [].
        """
        n_axes = len(self._planning_graph._layers)
        fig, axs = plt.subplots(1,n_axes)
        fig.suptitle("Wireplan")
        layer_ax_map = {layer : ax for layer, ax in zip(self._planning_graph._layers, axs)}
        for layer, ax in zip(self._planning_graph._layers, axs):
            ax.set_title(str(layer))
            ax.set_aspect('equal')
            ax.set_xlim(self._planning_graph.bounding_box[0], self._planning_graph.bounding_box[2])
            ax.set_ylim(self._planning_graph.bounding_box[1], self._planning_graph.bounding_box[3])
            
            ax.plot()

        colors = cm.get_cmap('brg', len(self._route_planners))
        for route_plan, i in zip(self._route_planners.values(), range(len(self._route_planners))):
            if plot_only:
                if not route_plan._net.name in plot_only:
                    continue
                
            color = colors(i)
            route_plan.plot(layer_ax_mapping=layer_ax_map, color=color)

        fig.legend([mpatches.Patch(color=colors(i), alpha=0.7) for i in range(len(self._route_planners))],
                   [route for route in self._route_planners])
        plt.show()

    def plot_on_ax(self, ax, plot_only = []):
        """Plot the plan on a axis.

        Args:
            ax (axis): Axis on which the wire plan shall be plotted.
            plot_only (list, optional): If specified, only these nets will be plotted. Defaults to [].
        """
        for route_plan in self._route_planners.values():
            if plot_only:
                if not route_plan._net.name in plot_only:
                    continue

            route_plan.plot_on_ax(ax)

class RoutePlanner:
    """Class to plan the wires for a net.
    """
    def __init__(self, route : Route, planning_graph : PlanningGraph) -> None:
        """RoutePlanner for planning the wires of the Route <route> on PlanningGraph <planning_graph>.

        Args:
            route (Route): Route which shall be planned.
            planning_graph (PlanningGraph): PlanningGraoh which shall be used for planning.
        """
        self._route = route
        self._net = route._net
        self._planning_graph = planning_graph
        
        self._terminal_tiles = set()
        self._setup_terminal_tiles()

        self._connected_tiles : nx.Graph
        self._connected_tiles = None
        self._setup_connected_tiles_from_route()
        
        self._actual_plan : nx.Graph
        self._actual_plan = None

    def _setup_terminal_tiles(self):
        """Setup the terminal tiles of the Route, which are induced from the pin-locations.
        """
        tiles = set()

        for terminal_name, terminal in  self._route._net.get_MagicTerminals().items():
            for pin in terminal.pins:
                if pin.layer == 'li':
                    #if the pin is on layer 'li' 
                    #skip the layer and use the tile at layer m1
                    # ToDo: Generalize for other PDKs
                    tile = self._planning_graph.get_tile(*pin.get_coordinate_on_grid(), pin.layer.pdk.get_higher_metal_layer(str(pin.layer)))
                    tiles.add(tile)
                else:
                    tile = self._planning_graph.get_tile(*pin.get_coordinate_on_grid(), pin.layer)
                    tiles.add(tile)
        self._terminal_tiles = tiles
    
    def _setup_connected_tiles_from_route(self):
        """Get a graph of connected tiles, induced from the route.
        """
        connected_tiles = nx.Graph()

        #get the flat connection graph
        flat_connection_graph = self._route.get_flat_connection_graph()
        #go through each path of the route
        for path in flat_connection_graph.nodes:
            assert type(path)==Path
            #setup a tiles-path for each path
            
            path_edges = list()
            for edges in path.graph.edges:
                node1 = edges[0]
                node2 = edges[1]

                if (node1.layer in self._planning_graph._layers) and (node2.layer in self._planning_graph._layers):
                    tile1 = self._planning_graph.get_tile(*node1.coordinate, node1.layer)
                    tile2 = self._planning_graph.get_tile(*node2.coordinate, node2.layer)

                    tile_path = self._planning_graph.get_simple_tile_path(tile1, tile2)

                    for i in range(1,len(tile_path)):
                        path_edges.append((tile_path[i-1], tile_path[i]))
                    
            #add the connected tiles to the graph
            connected_tiles.add_edges_from(path_edges)

        self._connected_tiles = connected_tiles

    def plan_route(self):
        """Plan the route.
        """
        
        #remove the actual plan from the planning graph
        if not (self._actual_plan is None):
            self._actual_plan : nx.Graph
            for node in self._actual_plan.nodes:
                assert type(node)==Tile
                node.remove_net_from_tile(net=self._net)

        #setup a router for the graph
        router = TileRouter(self._planning_graph, net=self._net, connected_tiles_graph=self._connected_tiles.copy())
        
        #connect all terminal tiles
        connection_graph = router.connect_tiles(list(self._terminal_tiles))

        #add the new plan to the graph
        self._add_plan_to_graph(connection_graph=connection_graph)

    def get_plan_length(self) -> float|None:
        """Get the length of the plan, given by length of the path describing the plan.

        Returns:
            float|None: Returns the length if there is allready a plan, otherwise None.
        """
        if not (self._actual_plan is None):
            length = 0
            edge : tuple[Tile, Tile]
            for edge in self._actual_plan.edges:
                length += Tile.distance_between(edge[0], edge[1]) #add the distance between the tiles
            
            return length
        else:
            return None

    def node_is_in_plan_area(self, grid_node : GridNode) -> bool:
        """Check if a node is in the area of the plan.

        Args:
            grid_node (GridNode): Node which shall be checked.

        Returns:
            bool: True, if in plan area, otherwise False.
        """

        try:
            tile = self._planning_graph.get_tile(*grid_node.coordinate, grid_node.layer)
            if tile in self._actual_plan.nodes:
                return True
            else:
                return False
        except:
            return False

    def get_plan_congestion(self) -> float|None:
        """Get the congestion of the plan, given by the sum of all edge-overflow-percentages of the plans edges.

        Returns:
            float|None: Returns the congestion if there is allready a plan, otherwise None.
        """
        if not (self._actual_plan is None):

            congestion = 0
            edge : tuple[Tile, Tile]
            for edge in self._actual_plan.edges:
                
                #get the tile-edge names
                e1 = Tile.get_edge_name(edge[0], edge[1])
                e2 = Tile.get_edge_name(edge[1], edge[0])
                
                #check if the edge is a interlayer-edge
                if e1=='H' or e1=='L':
                    e1 = 'I'

                if e2=='H' or e2=='L':
                    e2 = 'I'

                #add the overflow-percentage of both edges to the congestion
                congestion += edge[0].get_overflow_percentage(e1) + edge[1].get_overflow_percentage(e2)

            return congestion
        else:
            return None
    
    def remove_plan_from_graph(self):
        """Remove the actual plan from the planning graph.
        """
        #remove the actual plan from the planning graph
        if not (self._actual_plan is None):
            #iterate over each tile of the plan
            self._actual_plan : nx.Graph
            for node in self._actual_plan.nodes:
                assert type(node)==Tile
                #remove the net of the route from the tile
                node.remove_net_from_tile(net=self._net)

    def has_plan(self) -> bool:
        """Check if there is a route plan.

        Returns:
            bool: True if there is one, otherwise False.
        """
        return not (self._actual_plan is None)

    def plot(self, layer_ax_mapping : dict, color = 'b'):
        """Plot the plan.

        Args:
            layer_ax_mapping (dict): key: layer value: axis on wich the tiles shall be plotted.
            color (str, optional): Color of the plan. Defaults to 'b'.
        """
        if self._actual_plan:
            node : Tile
            for node in self._actual_plan.nodes:
                ax = layer_ax_mapping[node.layer]
                node.plot(ax, color=color)
    
    def plot_on_ax(self, ax):
        """Plot the plan on a single axis.

        Args:
            ax (axis): Axis on which the plan shall be plotted.
        """
        if self._actual_plan:
            cm = plt.get_cmap('Set1')
            node : Tile
            for node in self._actual_plan:
                color = cm(hash(node.layer)%9)
                node.plot(ax, color)

    def _add_plan_to_graph(self, connection_graph : nx.Graph):
        """Add/Update the plan of the route in the planning graph. 

        Args:
            connection_graph (nx.Graph): Graph of connected tiles, describing the new plan.
        """
        #add the actual plan to the planning graph
        #by iterating over each edge of the connection graph
        #and registering the net at the tiles edges
        for edge in connection_graph.edges:
            tile1 : Tile
            tile2 : Tile
            tile1 = edge[0]
            tile2 = edge[1]

            edge1 = tile1.get_edge_name(tile2)
            edge2 = tile2.get_edge_name(tile1)

            tile1.add_net_to_edge(net=self._net, edge=edge1)
            tile2.add_net_to_edge(net=self._net, edge=edge2)

        #update the actual plan
        self._actual_plan = connection_graph


        
