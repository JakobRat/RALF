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

from PDK.PDK import PDK
from Routing_v2.WirePlanning import RoutePlanner
from SchematicCapture.Net import Net
if TYPE_CHECKING:
    from PDK.PDK import PDK
    from Routing_v2.WirePlanning import RoutePlanner
    from matplotlib.pyplot import axis
    
import copy
from Rules.NetRules import MinNetWireWidth
from PDK.Layers import Layer
from SchematicCapture.Net import Net, SubNet
from Routing_v2.Pins import global_pins
from Routing_v2.Obstacles import global_obstacles, Obstacles, PinObstacle, PathObstacle
from Routing_v2.Router import TerminalRouter, StrategyRouter, DiePinRouter
from Routing_v2.Path import Path
from Routing_v2.Primitives import MetalWire, GridNode

import networkx as nx

class Route:
    """Class to route a net.
    """
    def __init__(self, net : Net, pdk : PDK) -> None:
        """Setup a route for Net <net> and PDK <pdk>.

        Args:
            net (Net): Net which shall be routed.
            pdk (PDK): PDK which shall be used.
        """
        self._net = net

        #setup the min. width of the net
        self._pdk = copy.deepcopy(pdk)
        self._setup_pdk()

        #store all connections in a graph
        self._connection_graph = nx.Graph()

        self._route_plan : RoutePlanner
        self._route_plan = None
        
        #setup child routes
        self._child_routes = {}
        self._setup_child_routes()

        #store the terminals which belong to this route
        self._magic_terminals = self._net.get_MagicTerminals(only_primitive=True) #get the terminals which are connected with primitive devices
        
        #store the die-pins of the route
        self._die_pins = self._net.die_pins
        
        #setup the pins of the route
        self._pins = []
        self._setup_pins()

        #setup obstacles for the pins and add them to the global obstacles
        self._obstacles = Obstacles(self._net)
        self._setup_obstacles_from_pins()
        global_obstacles.add_obstacle(self._obstacles, self._net)
        
        #store the paths of the route
        self._paths = []

        #place the devices pins
        #and add the to the obstacles
        self._place_pins()

    def _setup_pdk(self):
        """Setup the min. wire width for the route. 
        """
        min_width = None
        for rule in self._net.rules:
            if type(rule) == MinNetWireWidth:
                min_width = rule.min_width
                break
        
        if min_width:
            for (l, layer) in self._pdk.metal_layers.items():
                assert isinstance(layer, Layer)
                if layer.width <= min_width:
                    layer.set_width(min_width)

    
    def _setup_child_routes(self):
        """Setup a route for each child net.
        """

        for child_net in self._net.child_nets:
            sub_route = SubRoute(child_net, self._pdk, self)
            self._child_routes[child_net] = sub_route

            #add a node for the subroute to the connection graph
            self._connection_graph.add_node(sub_route)

    def _setup_pins(self):
        """Setup the pins of the route. And add them to the global pins.
        """
        for terminal_name, terminal in self._magic_terminals.items():
            self._pins.extend(terminal.pins)
            for pin in terminal.pins:
                global_pins.add_pin(pin, self._net)
        
        for pin in self._die_pins:
            global_pins.add_pin(pin, self._net)

    def _setup_obstacles_from_pins(self):
        """Setup obstacles for each pin.
        """
        for pin in self._pins:
            self._obstacles.add_obstacle(PinObstacle(pin))
        
        for pin in self._die_pins:
            self._obstacles.add_obstacle(PinObstacle(pin))

    def route_terminals(self):
        """Connect the terminal pins for each terminal of the route..
        """

        #connect the terminals of each child route.
        child : SubRoute
        for child in self._child_routes.values():
            child.route_terminals()

        #connect the terminals
        for terminal_name, terminal in self._magic_terminals.items():
            #get the paths which connect the pins of the terminals
            paths = TerminalRouter(terminal=terminal, route=self).route()
            
            #add the paths to the obstacles and the connection graph
            self._paths.extend(paths)
            for path in paths:
                self._obstacles.add_obstacle(PathObstacle(path, self._net))
                self._connection_graph.add_node(path)


    def _add_paths_to_connection_graph(self, paths : list[Path]):
        """
            Add paths to the connection graph.
        """
        #iterate over the paths.        
        for path in paths:
            assert isinstance(path, Path), f"Node {path} isn't a path!"
            
            #get the nodes which are connected to the path
            connected_nodes = self._connected_to_path(path=path)
            #add the path to graph
            self._connection_graph.add_node(path)
            #calculate the edges
            edges = []
            for node in connected_nodes:
                edges.append((path, node))

            self._connection_graph.add_edges_from(edges)


    def _connected_to_path(self, path : Path) -> list[Path|SubRoute]:
        """Get a list of Path|SubRoute to which the Path <path> is connected.

        Args:
            path (Path): Path which shall be checked.

        Raises:
            ValueError: If a node of the connection graph isn't a SubRoute or a Path.

        Returns:
            list[Path|SubRoute]: List of the nodes to which the path is connected.
        """
        connections = []
        for node in self._connection_graph.nodes:
            if type(node)==SubRoute: 
                #if the node is a subroute
                # check if the path is connected to a path of the subroute
                sub_route_connections = node._connected_to_path(path=path)
                if len(sub_route_connections)>0:
                    connections.append(node)
            elif type(node)==Path:
                #check if the path if connected to a path of the route.
                if Path.are_connected(path1=path, path2=node):
                    connections.append(node)
            else:
                raise ValueError(f"Type {type(node)} for a node not supported.")


        return connections 


    def __hash__(self) -> int:
        return hash(self._net)
    
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Route) and self._net == __value._net
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(net={self._net})"
    
    def _get_connected_terminal_paths(self) -> list[list[Path]]:
        """Get a list of all connected terminal paths.

        Returns:
            list[list[Path]]: List of a list of connected terminal paths.
        """

        path_nodes = list(filter(lambda node: isinstance(node, Path), self._connection_graph.nodes))

        subgraph = self._connection_graph.subgraph(path_nodes)

        return [list(c) for c in nx.connected_components(subgraph)]

    @property
    def name(self)-> str:
        """Get the name of the route,
        induced by the routes net.

        Returns:
            str: Name of the route.
        """
        return self._net.name
    
    @property
    def connection_graph(self) -> nx.Graph:
        """Get the connection graph of the route.

        Returns:
            nx.Graph: Connection graph
        """
        return self._connection_graph
    
    def set_route_planner(self, route_planner : RoutePlanner):
        """Set a route-planner for the route.

        Args:
            route_planner (RoutePlanner): Route-planner for this route.
        """
        self._route_plan = route_planner

    def get_route_planner(self) -> RoutePlanner | None:
        """Get the route plan of the route.

        Returns:
            RoutePlanner | None: Returns the plan, if there is one, otherwise None.
        """
        return self._route_plan
    
    def get_all_paths(self) -> list[Path]:
        """Get all paths of the route, including all paths of possible SubRoute's.

        Returns:
            list[Path]: List of paths.
        """
        paths = []
        for node in self._connection_graph.nodes:
            if type(node)==SubRoute:
                paths.extend(node.get_all_paths())
            else:
                paths.append(node)
        return paths
    
    def get_flat_connection_graph(self) -> nx.Graph:
        """Get a flattend version of the connection graph.

        Returns:
            nx.Graph: Flattend connection graph.
        """
        #get all nodes which are paths
        path_nodes = list(filter(lambda node: isinstance(node, Path), self._connection_graph.nodes))
        
        #get all nodes which are subroutes
        subroute_nodes = list(filter(lambda node: isinstance(node, SubRoute), self._connection_graph.nodes))

        flat_graph : nx.Graph
        #setup the flat graph, by the path nodes of this route
        flat_graph = self._connection_graph.subgraph(path_nodes).copy()
        
        #now get the flat-subgraphs of possible SubRoutes's
        subroute_graphs = {}
        for subroute in subroute_nodes:
            assert type(subroute)==SubRoute
            subroute_graph = subroute.get_flat_connection_graph()
            subroute_graphs[subroute] = subroute_graph
            flat_graph = nx.compose(flat_graph, subroute_graph) #add the flat subroute graph to the flat graph
        
        #now connect the subroute-paths to the paths of this route
        for subroute, graph in subroute_graphs.items():
            #get all edges to the subroute
            for edge in self._connection_graph.edges(subroute):
                #sort the edge, such that the actual subroute is the first entry
                if edge[1] == subroute:
                    edge = (edge[1], edge[0])
                
                assert type(edge[0])==SubRoute

                #find common path nodes
                if type(edge[1])==Path:
                    for path in subroute_graphs[edge[0]].nodes:
                        if Path.are_connected(path1=path, path2=edge[1]):
                            assert (path in flat_graph.nodes) and (edge[1] in flat_graph.nodes)
                            flat_graph.add_edge(path, edge[1])
                elif type(edge[1])==SubRoute:
                    for path1 in subroute_graphs[edge[0]].nodes:
                        for path2 in subroute_graphs[edge[1]].nodes:
                            assert type(path1)==Path
                            assert type(path2)==Path
                            if Path.are_connected(path1=path1, path2=path2):
                                assert (path1 in flat_graph.nodes) and (path2 in flat_graph.nodes)
                                flat_graph.add_edge(path1, path2)
        return flat_graph
    
    def get_flat_nodes_graph(self) -> nx.Graph:
        """Get a graph of all connected grid-nodes,
        defined by the route.

        Returns:
            nx.Graph: Connection graph.
        """
        graph = nx.Graph()
        for path in self.get_all_paths():
            graph = nx.compose(graph, path.graph)
        
        return graph

    def get_terminal_paths(self) -> list[Path]:
        """Get all paths, which connect terminals of the route.

        Returns:
            list[Path]: List of paths.
        """
        path_nodes = list(filter(lambda node: isinstance(node, Path), self._connection_graph.nodes))

        return path_nodes
    
    def _place_pins(self):
        """Place the Pins and make obstacles.
        """

        #place pins for each child route.
        #child : SubRoute
        #for child in self._child_routes.values():
        #    child._place_pins()

        print(f"Placing pins for {self}.")
        paths = []

        #place pins for each terminal which is at 'li'
        #setup a obstacle for each pin which is above 'li'
        # ToDo: Generalize!
        for terminal_name, terminal in self._magic_terminals.items():
            for pin in terminal.pins:
                if pin.layer == 'li':
                    path = Path([GridNode(*pin.get_coordinate_on_grid(), self._pdk.get_layer('li')),
                                 GridNode(*pin.get_coordinate_on_grid(), self._pdk.get_layer('m1'))],
                                 pdk=self._pdk)
                    paths.append(path)
                else:
                    self._obstacles.add_obstacle(PinObstacle(pin))
            
        #add the paths to the obstacles and the connection graph
        self._paths.extend(paths)
        for path in paths:
            self._obstacles.add_obstacle(PathObstacle(path, self._net))
            self._connection_graph.add_node(path)

    def connect_terminals(self):
        """Connect the terminals of the route.
        """

        #connect all terminals
        print(f"Connecting terminals for net {self._net}.")
        connected_terminals = self._get_connected_terminal_paths()
        if len(connected_terminals)>1: #not all terminals are connected
            paths_to_connect = []
            for connected_paths in connected_terminals:
                paths_to_connect.extend(connected_paths)

            #find paths which connect the unconnected paths
            paths = StrategyRouter(paths_to_connect, route=self).route()
            
            #add the paths to the connection graph and to the obstacles
            self._paths.extend(paths)
            self._add_paths_to_connection_graph(paths=paths)
            for path in paths:
                self._obstacles.add_obstacle(PathObstacle(path, self._net))
        
        #connect all terminals of child routes.
        for child in self._child_routes.values():
            child.connect_terminals()
        
    
    def connect_with_child_routes(self):
        """Connect the routing to the routing of possible subroutes.
        """

        if len(self._child_routes)>0: #only connect if there is at least one child route
            
            if len(self._get_connected_terminal_paths())>1:
                #if the terminals aren't connected, connect them first
                self.connect_terminals()

            for child in self._child_routes.values():
                #connect all child-routes first
                child.connect_with_child_routes()

            paths = []
            child : SubRoute
            for child in self._child_routes.values():
                paths.extend(child.get_all_paths()) #add all paths of the child
            
            paths.extend(self.get_terminal_paths()) #add all paths of this route

            #connect all paths
            print(f"Connecting child nets for net {self._net}.")
            paths = StrategyRouter(paths, route=self).route()
            
            #add the paths to the connection graph and to the obstacles
            self._paths.extend(paths)
            self._add_paths_to_connection_graph(paths)
            for path in paths:
                    self._obstacles.add_obstacle(PathObstacle(path, self._net))


    def connect_with_die_pins(self):
        """Connect the routing to die-pins.
        """
        if len(self._die_pins)>0:
            paths = []
            for path in self._paths:
                paths.append(path)
            
            die_paths = DiePinRouter(self._die_pins, paths, route=self).route()

            self._paths.extend(die_paths)
            self._add_paths_to_connection_graph(die_paths)

    def plot(self, ax : axis):
        """Plot the routing.

        Args:
            ax (axis): Axis on which the route shall be plotted.
        """
        path : Path
        for path in self._paths:
            path.plot(ax)

        if self._paths:
            last_node = path.nodes[-1]
            ax.text(*last_node.coordinate, self._net.name)
        
        for child_route in self._child_routes.values():
            child_route.plot(ax)

    def get_route_length(self) -> float:
        """Get the total wire-length of the route.

        Returns:
            float: Total wire-length of the route.
        """
        all_nodes = self.get_flat_nodes_graph()

        length = 0
        for edge in all_nodes.edges:
            if edge[0].layer == edge[1].layer:
                length += GridNode.get_distance_between(edge[0], edge[1])
        
        return length

    def get_number_of_vias(self) -> int:
        """Get the number of vias, of the route.

        Returns:
            int: Number of vias.
        """
        all_nodes = self.get_flat_nodes_graph()

        vias = 0
        for edge in all_nodes.edges:
            if edge[0].layer != edge[1].layer:
                vias += 1
        
        return vias
    
    def write_route_to_file(self, file : str, with_label : bool = True):
        """Write the route to a file.

        Args:
            file (str): Name of the file.
        """

        for child in self._child_routes.values():
            child.write_route_to_file(file)
        
        file = open(file, 'a')
        path : Path
        for path in self._paths:
            for primitive in path.primitives:
                file.write(primitive.generate_magic())
        
        if with_label and type(self)==Route:
            label = self._get_magic_label_for_route()
            if label:
                file.write(label)
        file.close()

    def _get_magic_label_for_route(self) -> str:
        """Generate a label for the route.

        Returns:
            str: Command to generate a label.
        """
        #find a wire
        net = self._net
        if type(net) == SubNet:
            net_name = f"{net.name}_{net.parent_device.name}"
        else:
            net_name = net.name

        for path in self.get_flat_connection_graph().nodes:
            for primitive in path.primitives:
                if type(primitive)==MetalWire:
                    wire = primitive
                    #place a label on top of the wire
                    command = ""
                    command += f"box {wire.bound()[0]} {wire.bound()[1]} {wire.bound()[2]} {wire.bound()[3]}\n"
                    command += f"label {net_name} 1 10 0 0 0 center {str(wire.layer)}\n"
                    return command

class SubRoute(Route):
    """Class to route a subnet of a net.
    """
    def __init__(self, net: SubNet, pdk: PDK, parent_route : Route) -> None:
        self._parent_route = parent_route
        super().__init__(net, pdk)

    def _setup_pdk(self):
        """PDK is already defined from the parent route.
        """
        pass

    def get_route_planner(self) -> RoutePlanner | None:
        return self._parent_route.get_route_planner()