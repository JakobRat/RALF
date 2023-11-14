from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from PDK.Layers import Layer
    from SchematicCapture.Net import Net

from PDK.PDK import global_pdk
from Rules.NetRules import MinNetWireWidth
import math

from Routing_v2.Geometrics import Rectangle, Rectangle3D, get_free_space, merge_rects

from Routing_v2.Obstacles import global_obstacles

import time

from tqdm.auto import tqdm
import numpy as np

import matplotlib.pyplot as plt

import heapq

class AstarData:
    """Class to store data which is needed for the A*-algorithm.
    """
    def __init__(self) -> None:
        self._parent = None
        self._cost = float('inf')
        self._g = float('inf')
    
    @property
    def parent(self):
        """Get the parent of this node.

        Returns:
            Any: Parent node.
        """
        return self._parent

    @property
    def cost(self) -> float:
        """Get the cost of the node.

        Returns:
            float: Cost of the node.
        """
        return self._cost
    
    @property
    def g(self) -> float:
        """Get the g-value (total cost) of the node.

        Returns:
            float: g-value
        """
        return self._g
    
    def set_cost(self, cost : float):
        """Set the cost of the node.

        Args:
            cost (float): Cost of the node.
        """
        self._cost = cost

    def set_g(self, g : float):
        """Set the g-value (total cost) of the node.

        Args:
            g (float): g-value of the node.
        """
        self._g = g
    
    def set_parent(self, parent):
        """Set the parent of the node.

        Args:
            parent (Any): Parent of the node.
        """
        self._parent = parent
    
    def reset(self):
        """Reset the data (parent, cost and g-value).
        """
        self._parent = None
        self._cost = float('inf')
        self._g = float('inf')

class Tile:
    """Class which represents a tile on the planning graph.
    """
    def __init__(self, bounding_box : tuple[float, float, float, float], layer : Layer) -> None:
        """Setup a tile.

        Args:
            bounding_box (tuple[float, float, float, float]): Bounding box of the tile.
            layer (Layer): Layer of the tile.
        """
        self._bounding_box = bounding_box
        self._layer = layer
        #store rectangles of the bounding box
        self._rectangle_3d = Rectangle3D(*bounding_box, hash(layer))
        self._rectangle = Rectangle(*bounding_box)

        #store neighbors
        self._neighbors = {"E" : None, "W" : None, "N" : None, "S" : None, "L" : None, "H" : None}
        
        #store the nets connected with the tile
        self._nets = set()

        #map the edges to the nets connected to them
        self._edge_nets : dict[str, set[Net]]
        self._edge_nets = {"E" : set(), "W" : set(), "N" : set(), "S" : set(), "L" : set(), "H" : set()}
        
        #store data for the A*-algorithm
        self.AstarData = AstarData()

        #store the penalty of the tile
        self._penalty = 0 #penalty for high congested tiles
        
        #store the edge capacities for each net
        self._edge_capacities : dict[Net, dict[str, float]]
        self._edge_capacities = {}

    @property
    def layer(self) -> Layer:
        """Get the layer of the tile.

        Returns:
            Layer: Layer of the tile.
        """
        return self._layer
    
    @property
    def bounding_box(self) -> tuple[float, float, float, float]:
        """Get the bounding box of the tile.

        Returns:
            tuple[float, float, float, float]: (min_x, min_y, max_x, max_y)
        """
        return self._bounding_box
    
    @property
    def width(self) -> float:
        """Get the width of the tile.

        Returns:
            float: Width of the tile (max_x-min_x)
        """
        return self.bounding_box[2]-self.bounding_box[0]
    
    @property
    def height(self) -> float:
        """Get the height of the tile.

        Returns:
            float: Height of the tile. (max_y-min_y)
        """
        return self.bounding_box[3]-self.bounding_box[1]
    
    @property
    def coordinate(self) -> tuple[float, float, Layer]:
        """Get the coordinate of the tile.

        Returns:
            tuple[float, float, Layer]: (lower left x, lower left y, layer)
        """
        return (self.bounding_box[0], self.bounding_box[1], self.layer)
    
    @property
    def penalty(self) -> float:
        """Get the penalty of the tile.

        Returns:
            float: Penalty of the tile.
        """
        return self._penalty

    def set_penalty(self, penalty : float):
        """Set the penalty of the tile.

        Args:
            penalty (float): Penalty of the tile
        """
        self._penalty = penalty

    def set_penalty_from_congestion(self, forgetting_factor = 0):
        """Set the penalty as the congestion of the tile.
        """
        
        congestion = 0
        k = 5
        for (c, d) in zip(self._edge_capacities.values(), self.get_edge_demand().values()):
            congestion += 2/(1+np.exp(-k*(max(d - c, 0)/(c+1e-3))))-1

        self.set_penalty(congestion/5 + forgetting_factor*self.penalty)

    def get_total_overflow(self) -> float:
        """Get the sum of all overflows of the tile.

        Returns:
            float: Sum(overflow(edge), for all edges of the tile)
        """
        overflow  = 0
        for net in self._nets:
            edge_demand = self.get_edge_demand(net)
            for (edge, c) in self.get_edge_capacities(net).items():
                if edge == 'I':
                    d = edge_demand['H']+edge_demand['L']
                else:
                    d = edge_demand[edge]

                overflow += max(d - c, 0)
        
        return overflow
    
    def get_total_overflow_percentage(self) -> float:
        """Get the total overflow percentage of the tile.

        Returns:
            float: Sum of overflow percentages of all edges.
        """
        overflow = 0
        for edge in ['E','W','S','N','I']:
            
            edge_overflow = 0
            
            edge_overflow += self.get_overflow_percentage(edge)

            overflow += edge_overflow

        return overflow

    def get_overflow_percentage(self, edge : str, clipped = True) -> float:
        """Get the percentage of the overflow at edge <edge>.
            overflow_percentage = (edge_demand)/(edge_capacity +1)

        Args:
            edge (str): Edge for which the overflow percentage is searched. (One of E,W,N,S,I)
            clipped (bool): If True, the excess percentage (max(overflow_percentage-1,0)) will be returned, otherwise overflow_percentage.
        Returns:
            float: Overflow percentage.
        """
        assert edge in ['E','W','N','S','I']

        usage = 0
        if edge != 'I':
            #N,S,E,W edge
            #iterate over all nets of the edge
            for net in self._edge_nets[edge]:
                #get the demand of the edge and net
                demand = self.get_edge_demand(net=net)[edge]
                #get the capacity of the edge for the net
                capacity = self.get_edge_capacities(net=net)[edge]
                
                #add the percentage of the usage to the total usage
                usage += demand/(capacity+1)
        else:
            for net_edge in ['H', 'L']:
                #interlayer edge
                #iterate of each net
                for net in self._edge_nets[net_edge]:
                    #get the demand of the edge and net
                    demand = self.get_edge_demand(net=net)[net_edge]
                    #get the capacity of the edge for the net
                    capacity = self.get_edge_capacities(net=net)[edge]

                    #add the percentage of the usage to the total usage
                    usage += demand/(capacity+1)
        
                        
        if clipped:
            #return the excess usage -> the overflow
            return max(usage-1, 0)
        else:
            #return the usage
            return usage
    
    def has_crossing_nets(self) -> bool:
        """Check if the tile has crossing nets.

        Returns:
            bool: True, if at least two nets are crossing, else False.
        """

        #store the direction of each net, if it passes the 
        #tile horizontally or vertically
        net_directions = []
        for net in self._nets:
            if net in self._edge_nets['E'] and net in self._edge_nets['W']:
                net_directions.append('H')
            elif net in self._edge_nets['N'] and net in self._edge_nets['S']:
                net_directions.append('V')
        
        #check if all directions are same
        #if not -> two nets are crossing -> can't be routed!
        if len(net_directions)>0:
            act_dir = net_directions[0]
            for dir in net_directions:
                if dir != act_dir:
                    return True
        
        return False

    def get_usage_percentage(self, edge : str) -> float:
        """Get the usage as percentage of the edge <edge>.
            usage_percentage = (edge_demand)/(edge_capacity+1)

        Args:
            edge (str): Edge one of 'E','W','N','S','I'

        Returns:
            float: usage_percentage
        """
        assert edge in ['E','W','N','S','I']

        usage = 0
        if edge != 'I':
            #N,S,E,W edge
            #iterate over all nets of the edge
            for net in self._edge_nets[edge]:
                #get the demand of the edge and net
                demand = self.get_edge_demand(net=net)[edge]
                #get the capacity of the edge for the net
                capacity = self.get_edge_capacities(net=net)[edge]
                
                #add the percentage of the usage to the total usage
                usage += demand/(capacity+1)
        else:
            for net_edge in ['H', 'L']:
                #interlayer edge
                #iterate of each net
                for net in self._edge_nets[net_edge]:
                    #get the demand of the edge and net
                    demand = self.get_edge_demand(net=net)[net_edge]
                    #get the capacity of the edge for the net
                    capacity = self.get_edge_capacities(net=net)[edge]

                    #add the percentage of the usage to the total usage
                    usage += demand/(capacity+1)
        return usage
    
    def set_neighbor(self, position : str, neighbor : Tile):
        """Set a neighbor at position <position> for the tile.

        Args:
            position (str): One of E,W,S,N,H,L
            neighbor (Tile): Neighboring tile

        Raises:
            ValueError: If the tile already has a neighbor at this position.
            ValueError: If the position is unsupported.
        """
        if position in self._neighbors:
            if self._neighbors[position] is None:
                self._neighbors[position] = neighbor
            else:
                raise ValueError(f"Tile {self} has already a neighbor at position {position}!")
        else:
            raise ValueError(f"Position {position} not supported!")
    
    def add_net_to_edge(self, net : Net, edge : str):
        """Add a net to a specific edge of the tile.

        Args:
            net (Net): Net to be added.
            edge (str): Edge of the tile. One of 'E', 'W', 'S', 'N', 'L', 'H'
        """

        assert edge in self._edge_nets, f"Edge {edge} not a valid identifier!"

        #add the net to the edge
        self._edge_nets[edge].add(net)
        #add the net to the nets
        self._nets.add(net) 

    def remove_net_from_tile(self, net : Net):
        """Remove a net from the tile.

        Args:
            net (Net): Net which shall be removed.
        """

        #check if the net is in the nets
        #and remove it
        if net in self._nets:
            self._nets.remove(net)
        
        #check all edges if there is the net registered
        # if registered, remove it from the edge
        for edge, nets in self._edge_nets.items():
            if net in nets:
                nets.remove(net)

    def get_edge_demand(self, net : Net = None) -> dict[str, float]:
        """Get the demand of the tiles boundaries/edges.
                The demand of net_i at edge_j is is given by:
                For E,W,S,N edge: d(net_i, edge_j) = (W(net_i)+minSpace(layer))*0.5
                For H,L edge: d(net_i, edge_j) = (W(via_plate)+minSpace(layer))²
                The demand of edge_j is given by d(edge_j) = Sum(d(net_i, edge_j), net_i in edge_j)
        Args:
            net (Net, optional): If specified, only the demand of Net <net> will be considered. Defaults to None.

        Returns:
            dict[str, float]: keys: 'E', 'W', 'S', 'N', 'H', 'L'
                                    'E' : demand of the east-boundary
                                    'W' : demand of the west-boundary
                                    'S' : demand of the south-boundary
                                    'N' : demand of the north-boundary
                                    'H' : demand of the higher-layer-boundary
                                    'L' : demand of the lower-layer-boundary
        """

        #setup a dict for the demands
        edge_dict = {'E' : 0, 'W' : 0, 'S' : 0, 'N' : 0, 'H' : 0, 'L' : 0}

        #iterate over all edges
        for edge, nets in self._edge_nets.items():

            #check if the edge is a interlayer-edge
            #if, calculate the width of the via-plate + space
            via_w = 0
            if edge == 'L':
                lower_layer = self.layer.pdk.get_lower_metal_layer(str(self.layer))
                if not (lower_layer is None):
                    via_layer = self.layer.pdk.get_via_layer(self.layer, lower_layer)
                    w = via_layer.width
                    e = via_layer.minEnclosure_top
                    via_w = w + 2*e + self.layer.minSpace

            elif edge == 'H':
                higher_layer = self.layer.pdk.get_higher_metal_layer(str(self.layer))
                if not (higher_layer is None):
                    via_layer = self.layer.pdk.get_via_layer(self.layer, higher_layer)
                    w = via_layer.width
                    e = via_layer.minEnclosure_bottom
                    via_w = w + 2*e + self.layer.minSpace

            #calculate the edge demand
            edge_demand = 0
            act_net : Net
            for act_net in nets:
                #iterate over each net of the edge
                if act_net == net or net == None:

                    if edge != 'H' and edge != 'L':
                        #N,S,E,W edge
                        #demand = (Width+minSpace)*(D/2)/D
                        # D ... depth of the tile (height or width)
                        width = self.layer.minWidth
                        for rule in act_net.rules:
                            if type(rule) == MinNetWireWidth:
                                width = max(rule.min_width, width)
                                break
                        edge_demand += (width + self.layer.minSpace)*0.5
                    else:
                        #Interlayer edge
                        # demand = (Plate_Width+minSpace)²
                        if act_net in self._edge_nets['L'] and act_net in self._edge_nets['H']:
                            # via connects two neighboring layers
                            # -> don't count the via twice
                            edge_demand += (via_w**2)/2
                        else:
                            edge_demand += via_w**2
            
            edge_dict[edge] += edge_demand
        
        return edge_dict

    def get_edge_capacities(self, net : Net = None) -> dict[str, float]:
        """Get the capacities of the tiles boundaries/edges.

        Args:
            net (Net, optional): If specified, the obstacles of Net <net> will not be considered. Defaults to None.

        Returns:
            dict[str, float]: keys: 'E', 'W', 'S', 'N', 'I'
                                    'E' : capacity of the east-boundary
                                    'W' : capacity of the west-boundary
                                    'S' : capacity of the south-boundary
                                    'N' : capacity of the north-boundary
                                    'I' : interlayer capacity
        """
        
        #check if the capacity were already calculated
        if net in self._edge_capacities:
            return self._edge_capacities[net]
        else:
            #calculate the capacity
            
            start = time.time()
            #setup the rtree to check for obstacles
            global_obstacles.setup_obstacle_rtree_for_net(net)
            
            #get the obstacles in the area defined by the tile.
            obstacles = global_obstacles.get_obstacles_in_area(self._rectangle_3d.bounding_box)
            
            #print(f"Getting obstacles took: {round((time.time()-start)*1e3, 2)}ms")
            start = time.time()
            
            #calculate the edge-capacities
            edge_dict = {}
            if len(obstacles)>0:

                layer_space = self.layer.minSpace
                #setup rectangles for the expanded obstacles 
                obstacle_rects = [Rectangle(o[0]-layer_space,o[1]-layer_space,o[3]+layer_space,o[4]+layer_space) for o in obstacles]
                
                #get the rectangles which form the free (non-blocked) space
                free_space = get_free_space(self._rectangle, obstacle_rects)
                
                #compute the interlayer capacity as the free-space area
                interlayer_capacity = 0
                for r in free_space:
                    interlayer_capacity += r.height*r.width

                #compute the capacity of the east and west edge
                if free_space:

                    #merge the free-space rectangles, such that the depth of the
                    #edge is maximized 
                    # -> first merge rectangles which share W and E edges
                    # -> then merge rectangles which share N and S edges
                    merged_for_EW = merge_rects(free_space, direction='V')
                    merged_for_EW = merge_rects(merged_for_EW, direction='H')

                    #get the rectangles which touch the W edge
                    W_rects = list(filter(lambda r: r.bounding_box[0]==self.bounding_box[0], merged_for_EW))
                    #get the rectangles which touch the E edge
                    E_rects = list(filter(lambda r: r.bounding_box[2]==self.bounding_box[2], merged_for_EW))
                else:
                    W_rects = []
                    E_rects = []

                #calculate the capacity of the W and E edge
                # c(edge) = Sum(height(R_i)*width(R_i)/D(Tile, edge), for R_i touching edge)
                W_cap = 0
                for r in W_rects:
                    W_cap += r.height * r.width / self.width
                
                E_cap = 0
                for r in E_rects:
                    E_cap += r.height * r.width / self.width
                
                #compute the capacity of the north and south edge
                if free_space:
                    #merge the free-space rectangles, such that the depth of the
                    #edge is maximized 
                    # -> first merge rectangles which share N and S edges
                    # -> then merge rectangles which share W and E edges
                    merged_for_SN = merge_rects(free_space, direction='H')
                    merged_for_SN = merge_rects(merged_for_SN, direction='V')

                    #get the rectangles which touch the S edge
                    S_rects = list(filter(lambda r: r.bounding_box[1]==self.bounding_box[1], merged_for_SN))
                    #get the rectangles which touch the N edge
                    N_rects = list(filter(lambda r: r.bounding_box[3]==self.bounding_box[3], merged_for_SN))
                else:
                    S_rects = []
                    N_rects = []
                
                #calculate the capacity of the S and N edge
                # c(edge) = Sum(height(R_i)*width(R_i)/D(Tile, edge), for R_i touching edge)
                S_cap = 0
                for r in S_rects:
                    S_cap += r.height * r.width / self.height
                
                N_cap = 0
                for r in N_rects:
                    N_cap += r.height * r.width / self.height
                
                edge_dict["E"] = E_cap
                edge_dict["W"] = W_cap
                edge_dict["N"] = N_cap
                edge_dict["S"] = S_cap
                edge_dict["I"] = interlayer_capacity
                #print(f"Computing capacities took: {round((time.time()-start)*1e3, 2)}ms")
            else:
                #there are no obstacles -> tile has full capacitance
                edge_dict["E"] = self.height
                edge_dict["W"] = self.height
                edge_dict["N"] = self.width
                edge_dict["S"] = self.width
                edge_dict["I"] = self.width*self.height

            self._edge_capacities[net] = edge_dict
            return edge_dict

    @staticmethod
    def distance_between(tile1 : Tile, tile2 : Tile) -> float:
        """Get the manhattan distance between tile1 and tile2.

        Args:
            tile1 (Tile): First tile.
            tile2 (Tile): Second tile.

        Returns:
            float: Distance between the tiles.
        """
        return (abs(tile1.coordinate[0]-tile2.coordinate[0]) + 
                abs(tile1.coordinate[1]-tile2.coordinate[1]) +
                abs(hash(tile1.layer)-hash(tile2.layer)))
    
    def get_edge_name(self, tile : Tile) -> str | None:
        """Get the name of the edge between <self> and Tile <tile>.

        Args:
            tile (Tile): Neighboring tile.

        Returns:
            str | None: One of N,S,E,W,L,H if the tile is a neighbor else None.
        """

        #     N
        #     |
        # E - T - W
        #     |
        #     S

        if tile.layer == self.layer: #tile is N;S;E;W
            if tile.coordinate[1] == self.coordinate[1]: #tile is E;W
                if self.coordinate[0]-self.width == tile.coordinate[0]: #tile is E
                    return 'E'
                elif self.coordinate[0]+self.width == tile.coordinate[0]: #tile is W
                    return 'W'
                else: #tile is not a neighbor
                    return None
            elif tile.coordinate[0] == self.coordinate[0]: #tile is N;S
                if self.coordinate[1]-self.height == tile.coordinate[1]: #tile is S
                    return 'S'
                elif self.coordinate[1]+self.height == tile.coordinate[1]: #tile is N
                    return 'N'
                else: #tile is not a neighbor
                    return None
        
        #   H - Layer i+1
        #   | 
        #   T - Layer i
        #   |
        #   L - Layer i-1

        elif tile.coordinate[0]==self.coordinate[0] and tile.coordinate[1]==self.coordinate[1]: #tile is L; H
            dLayer = hash(self.layer) - hash(tile.layer)
            if dLayer==1: #tile is L
                return 'L'
            elif dLayer==-1: #tile is H
                return 'H'
            else: #tile is not a neighbor
                return None
        else: #tile is not a neighbor
            return None
        
    def __eq__(self, __value: object) -> bool:
        return (isinstance(__value, Tile) and 
                self._bounding_box == __value.bounding_box and 
                self._layer == __value._layer)

    def __lt__(self, other: object) -> bool:
        return (isinstance(other, Tile) and 
                self.coordinate<other.coordinate)
    
    def __hash__(self) -> int:
        return hash(tuple([*self._bounding_box, hash(self._layer)]))
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(b={self.bounding_box}, l={self.layer})"
    
    def plot(self, ax, color = None):
        """Plot a rectangle for the tile, with color <color>.

        Args:
            ax (axis): Axis on which the tile shall be plotted
            color (str, optional): Color of the tile. Defaults to None.
        """
        self._rectangle.plot(ax, color=color)
            
        

class PlanningGraph:
    """Class for a planning graph, which holds tiles for the wire planning.
    """
    def __init__(self, bounding_box : tuple[float, float, float, float], tile_width : float, tile_height : float, layers : list[str]) -> None:
        """Setup a planning graph.

        Args:
            bounding_box (tuple[float, float, float, float]): Minimum - bounding box of the planning graph.
            tile_width (float): Width of a tile
            tile_height (float): Height of a tile
            layers (list[str]): Layers which shall be used in the graph
        """
        self._bounding_box = bounding_box
        self._tile_width = tile_width
        self._tile_height = tile_height

        #get the layers
        self._pdk_layers = {layer : global_pdk.get_layer(layer) for layer in layers}
        #sort the layers according their layer number
        self._layers = sorted(self._pdk_layers.values())
        self._tiles_x = []
        self._tiles_y = []
        #store the tiles in a dict
        # key: (x, y, layer) value: tile
        self._tiles : dict[tuple[int, int, Layer], Tile]
        self._tiles = {}
        self._setup_tiles()
    
    def _setup_tiles(self):
        """Setup all tiles of the planning graph.
        """

        #calculate the number of tiles in x and y
        n_x = math.ceil((self._bounding_box[2]-self._bounding_box[0])/self._tile_width)
        n_y = math.ceil((self._bounding_box[3]-self._bounding_box[1])/self._tile_height)

        tiles : dict[tuple[int, int, Layer], Tile]
        tiles = {}

        #calculate the coordinates of the tiles
        x = [self._bounding_box[0] + i*self._tile_width for i in range(n_x+1)]
        y = [self._bounding_box[1] + i*self._tile_height for i in range(n_y+1)]

        #store the x and y coordinates of the tiles
        self._tiles_x = x[:-1]
        self._tiles_y = y[:-1]

        layers = list(self._pdk_layers.values())
        layers = sorted(layers)

        #setup all tiles
        for i in tqdm(range(len(x)-1), desc='x-tiles', leave=True):
            for j in tqdm(range(len(y)-1), desc='y-tiles', leave=False):
                x1, x2 = x[i], x[i+1]
                y1, y2 = y[j], y[j+1]

                for layer, n_layer in zip(layers, range(len(layers))):
                    tile = Tile((x1,y1,x2,y2), layer)
                    tiles[(x1,y1, layer)] = tile
        
        self._tiles = tiles

    def reset_tiles_for_Astar(self):
        """Reset the tiles of the graph for the A* search.
        """
        tile : Tile
        for tile_c, tile in self._tiles.items():
            tile.AstarData.reset()

    def set_penalty(self, forgetting_factor : float = 1.0):
        """Set the penalty of each tile.
            The penalty is calculated by : p(tile, t) = forgetting_factor*p(tile, t-1) + O(tile, t) + 100*N_crossing_nets(tile, t)
                                            O(tile, t) ... total overflow of the tile at timestamp t
                                            N_crossing_nets(tile, t) ... number of crossing nets in tile at timestamp t
        Args:
            forgetting_factor (float, optional): The amount the tile should forget about its last penalty.     
                                                If 1, none will be forgotten, if 0 all will be forgotten. Defaults to 1.0.
        """
        for tile in self._tiles.values():
            tile.set_penalty(forgetting_factor*tile.penalty + tile.get_total_overflow_percentage() + int(tile.has_crossing_nets())*100)

    def get_total_penalty(self) -> float:
        """Get the sum of all penalties.

        Returns:
            float: Sum of penalties.
        """
        penalty = 0
        for tile in self._tiles.values():
            penalty += tile.penalty
        
        return penalty

    def get_total_overflow(self) -> float:
        """Get the sum of all overflows.

        Returns:
            float: Sum of overflows.
        """
        overflow = 0
        for tile in self._tiles.values():
            overflow += tile.get_total_overflow()
        
        return overflow

    def get_total_overflow_percentage(self) -> float:
        """Get the sum of all overflow percentages.

        Returns:
            float: Sum of overflow percentages.
        """
        overflow = 0
        for tile in self._tiles.values():
            perc = tile.get_total_overflow_percentage()
            if perc>0:
                pass
            overflow += perc
        
        return overflow

    def get_total_crossing_nets(self) -> int:
        """Get the total number of tiles which have crossing nets.

        Returns:
            int: Number of tiles having crossing nets.
        """
        crossings = 0
        for tile in self._tiles.values():
            crossings += int(tile.has_crossing_nets())
                    
        return crossings
    
    @property
    def bounding_box(self) -> tuple[float, float, float, float]:
        """Get the bounding box of the planning graph.

        Returns:
            tuple[float, float, float, float]: (min_x, min_y, max_x, max_y)
        """
        return (self._bounding_box[0], self._bounding_box[1], 
                self._bounding_box[0]+len(self._tiles_x)*self._tile_width, 
                self._bounding_box[1]+len(self._tiles_y)*self._tile_height)
    
    @property
    def n_tyles_per_layer(self) -> tuple[int, int]:
        """Get the number of tiles in x and y per layer.

        Returns:
            tuple: (n(tiles) in x, n(tiles) in y)
        """
        return (len(self._tiles_x), len(self._tiles_y))
    

    def get_tile(self, x : float, y : float, layer : Layer) -> Tile:
        """Get the tile in which the point (x, y, layer) is enclosed.

        Args:
            x (float): x-coordinate
            y (float): y-coordinate
            layer (Layer): Layer

        Raises:
            ValueError: If there isn't a tile in which this coordinate is enclosed.

        Returns:
            Tile: Tile of the coordinate (x, y, layer).
        """
        assert x>=self.bounding_box[0] and x<= self.bounding_box[2], f"x-coordinate {x} out of range!"
        assert y>=self.bounding_box[1] and y<= self.bounding_box[3], f"y-coordinate {y} out of range!"
        
        #calculate the coordinate of the tile
        tile_x = ((x-self.bounding_box[0])//self._tile_width)*self._tile_width + self.bounding_box[0]
        tile_y = ((y-self.bounding_box[1])//self._tile_height)*self._tile_height + self.bounding_box[1]

        try:
            tile = self._tiles[(tile_x, tile_y, layer)]
        except:
            raise ValueError("Tile for coordinate ({x},{y}) and layer {layer} couldn't be found!")
        
        return tile

    def get_simple_tile_path(self, start : Tile, goal : Tile) -> list[Tile]|None:
        """Get a simple path from start to goal. 
           For a simple path start and goal must have same x and/or same y coordinate.

        Args:
            start (Tile): Start tile.
            goal (Tile): Goal tile.

        Returns:
            list[Tile]|None: List of connected tiles forming a path. None if no path was found.
        """
        
        #check if the tiles are in the graph
        assert start.coordinate in self._tiles
        assert goal.coordinate in self._tiles

        assert start.coordinate[0]==goal.coordinate[0] or start.coordinate[1]==goal.coordinate[1]

        #find a path from start to goal tile
        tile_path = self.astar(start=start, goal=goal)
        
        return tile_path
        

    def heuristic(self, start : Tile, goal : Tile) -> float:
        """Heuristic which will be used for the A* search.
            -> Manhattan distance between start and goal.
        Args:
            start (Tile): Staring tile.
            goal (Tile): Goal tile.

        Returns:
            float: Value of the heuristic.
        """
        return Tile.distance_between(start, goal)

    def astar(self, start : Tile, goal : Tile) -> list[Tile]|None:
        """Find a path from start to goal.

        Args:
            start (Tile): Starting tile.
            goal (Tile): Goal tile.

        Returns:
            list[Tile]|None: List of tiles forming a path from start to goal. None, if no path was found.
        """
        self.reset_tiles_for_Astar()
        open_list = []
        closed_list = set()

        start.AstarData.set_g(0)
        start.AstarData.set_parent(None)

        heapq.heappush(open_list, (self.heuristic(start, goal), start))
        while open_list:
            current_tile : Tile
            current_cost, current_tile = heapq.heappop(open_list)

            if current_tile == goal:
                #goal reached, reconstruct path
                path = []
                while current_tile:
                    path.append(current_tile)
                    current_tile = current_tile.AstarData.parent
                
                return path[::-1]
            
            closed_list.add(current_tile)

            for neighbor in self.get_neighbors(current_tile):
                if neighbor in closed_list:
                    continue
                
                
                tentative_score = current_tile.AstarData.g + Tile.distance_between(current_tile, neighbor)

                if tentative_score<neighbor.AstarData.g:
                    neighbor.AstarData.set_parent(current_tile)
                    neighbor.AstarData.set_g(tentative_score)
                    
                    if neighbor not in open_list:
                        heapq.heappush(open_list, (neighbor.AstarData.g+self.heuristic(neighbor, goal), neighbor))
                        
                    else:
                        i = open_list.index(neighbor)
                        old_value = open_list.pop(i)
                        heapq.heapify(open_list)
                        heapq.heappush(open_list, (neighbor.AstarData.g+self.heuristic(neighbor, goal), neighbor))
                        

        return None

    def plot(self):
        pass
    
    def get_neighbors(self, tile : Tile) -> list[Tile]:
        """Get all neighboring tiles of Tile <tile>.

        Args:
            tile (Tile): Tile which neighbors are searched.

        Returns:
            list[Tile]: List of neighboring tiles.
        """

        assert tile.coordinate in self._tiles, f"Tile {tile} not in graph! Can't get neighbors."

        tile_x, tile_y, layer = tile.coordinate


        neighbors = []
        #lower tile
        layer_index = self._layers.index(layer)
        if layer_index>0:
            lower_layer = self._layers[layer_index-1]
            neighbors.append(self._tiles[(tile_x, tile_y, lower_layer)])
        
        #higher tile
        if layer_index+1<len(self._layers):
            higher_layer = self._layers[layer_index+1]
            neighbors.append(self._tiles[(tile_x, tile_y, higher_layer)])
        
        #west tile
        try:
            neighbors.append(self._tiles[(tile_x-self._tile_width, tile_y, layer)])
        except:
            pass

        #east tile
        try:
            neighbors.append(self._tiles[(tile_x+self._tile_width, tile_y, layer)])
        except:
            pass
        
        #north tile
        try:
            neighbors.append(self._tiles[(tile_x, tile_y+self._tile_height, layer)])
        except:
            pass

        
        #south tile
        try:
            neighbors.append(self._tiles[(tile_x, tile_y-self._tile_height, layer)])
        except:
            pass

        return neighbors

