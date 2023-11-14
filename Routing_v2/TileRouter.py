from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Routing_v2.PlanningGraph import PlanningGraph
    from SchematicCapture.Net import Net

import heapq
from Routing_v2.PlanningGraph import Tile
import numpy as np
import networkx as nx

class TileRouter:
    def __init__(self, graph : PlanningGraph, net : Net = None, connected_tiles_graph : nx.Graph = None) -> None:
        """Setup a TileRouter to connect tiles on PlanningGraph <graph> for Net <net> with pre-connected tiles given in Graph <connected_tiles_graph>.

        Args:
            graph (PlanningGraph): PlanningGraph which shall be used.
            net (Net, optional): Net which shall be routed. Defaults to None.
            connected_tiles_graph (nx.Graph, optional): Graph of pre-connected tiles. Defaults to None.
        """
        self._graph = graph
        self._net = net
        self._connection_graph = nx.Graph()
        if not (connected_tiles_graph is None):
            self._connection_graph = connected_tiles_graph
    
    def connect_tiles(self, tiles : list[Tile]) -> nx.Graph:
        """Connect the tiles given in <tiles>.

        Args:
            tiles (list[Tile]): List of tiles, which shall be connected.

        Returns:
            nx.Graph: Graph which describes the connection between the tiles.
        """
        #add the tiles to the connection graph
        self._connection_graph.add_nodes_from(tiles)

        #get the next tiles which shall be connected
        next_tiles = self._get_next_tiles_to_be_connected()

        #connect tiles until all are connected
        while not (next_tiles is None):
            
            #reset the AStar-data for each tile
            self._graph.reset_tiles_for_Astar()

            #find a path from the start to the goal tile
            path = self.astar(next_tiles[0], next_tiles[1])

            #add the path to the connection graph
            self._add_path_to_connection_graph(path)

            #get the next tiles which shall be connected
            next_tiles = self._get_next_tiles_to_be_connected()

        return self._connection_graph
    
    def _add_path_to_connection_graph(self, path : list[Tile]):
        """Add a path of tiles to the connection graph.

        Args:
            path (list[Tile]): List of tiles describing a path.
        """
        edges = []
        #generate edges between the tiles
        for i in range(len(path)-1):
            edges.append((path[i], path[i+1]))

        #add the edges to the graph
        self._connection_graph.add_edges_from(edges)

    def _get_next_tiles_to_be_connected(self) -> tuple[Tile, Tile] | None:
        """Get the next tiles which shall be connected.
            The tiles which aren't connected and minimum spaced will be returned.

        Returns:
            tuple[Tile, Tile] | None: The two tiles which shall be connected, None if all tiles are connected.
        """
        if len(self._connection_graph.nodes)>0:
            components = list(nx.connected_components(self._connection_graph))
            if len(components)>1: #there are unconnected tiles
                heap = []
                #get the tiles which are minimum spaced and not connected.
                for i in range(len(components)-1):
                    for j in range(i+1, len(components)):
                        min_dist_tiles = self._get_min_dist_tiles(list(components[i]), list(components[j]))
                        heapq.heappush(heap, min_dist_tiles)
                
                tiles = heapq.heappop(heap)[1]

                return tiles
            else: #all connected
                return None
        else:
            return None

    def _get_min_dist_tiles(self, tiles1 : list[Tile], tiles2 : list[Tile]) -> tuple[float, tuple[Tile, Tile]]:
        """Get the tiles with minimum distance between them.

        Args:
            tiles1 (list[Tile]): first list of tiles.
            tiles2 (list[Tile]): Second list of tiles.

        Returns:
            tuple[float, tuple[Tile, Tile]]: Distance, (Tile of tiles1, Tile of tiles2)
        """
        
        heap = []

        #calculate the distances between all tiles
        for tile1 in tiles1:
            for tile2 in tiles2:
                dist = Tile.distance_between(tile1, tile2)
                heapq.heappush(heap, (dist, (tile1, tile2)))
        
        #return the tiles with min. distance.
        return heapq.heappop(heap)
    
    def heuristic(self, start : Tile, goal : Tile):
        """Heuristic which will be used for the a* search.

        Args:
            start (Tile): Starting tile.
            goal (Tile): Goal tile.

        Returns:
            int: Number of tiles between start and goal in an L1-norm fashion.
        """
        nx = abs(start.coordinate[0]-goal.coordinate[0])//(start.width)
        ny = abs(start.coordinate[1]-goal.coordinate[1])//(start.height)
        nl = abs(hash(start.layer)-hash(goal.layer))

        return nx+ny+nl

    def get_cost(self, tile : Tile, neighbor : Tile) -> float:
        """Get the edge cost between Tile <tile> and Tile <neighbor>.

        Args:
            tile (Tile): Tile
            neighbor (Tile): Neighboring tile.

        Returns:
            float: Edge cost.
        """
        
        #get the edge names
        edge_tile = tile.get_edge_name(neighbor)
        edge_neighbor = neighbor.get_edge_name(tile)
        
        #add the net at the edge to calculate the resulting overflow        
        tile.add_net_to_edge(self._net, edge=edge_tile)
        neighbor.add_net_to_edge(self._net, edge=edge_neighbor)

        if edge_tile == 'H' or edge_tile == 'L': #if the edge is a VIA edge -> use interlayer capacity
                edge_tile = 'I'

        if edge_neighbor == 'H' or edge_neighbor == 'L': #if the edge is a VIA edge -> use interlayer capacity
                edge_neighbor = 'I'

        
        #get the number of nets already in the neighboring tile
        n_nets = len(neighbor._nets)

        #get the usage of the edge 
        usage = tile.get_overflow_percentage(edge=edge_tile, clipped=False) + neighbor.get_overflow_percentage(edge=edge_neighbor, clipped=False)
        
        #overflow = np.clip(overflow/2-0.5, 0, 1.5)
        #calculate the overflow by using a step function
        overflow = np.clip(usage/2-0, 0, 2)

        #overflow = 2/(1+np.exp(-overflow))-1
        
        #calculate the cost of the edge
        # cost function adapted from:
        # L. McMurchie and C. Ebeling, "Pathfinder: A negotiation-based performance-driven router for FPGAs", 
        # in Proc. ACM Symp. Field-Programmable Gate Array, Feb. 1995, pp. 111-117
        # Since the overflow is given in %, and if the neighbor is penalized, the cost should increase tremendously
        # the cost function is multiplied by 100.
        # 1 is added to the cost, to guaranty a admissible heuristic, since h(node, neighbor)=1, therefore g(goal)>=h(start, goal).
        cost = ((overflow + neighbor.penalty)*(n_nets))*100 + 1
        
        #remove the net from the tiles
        tile.remove_net_from_tile(self._net)
        neighbor.remove_net_from_tile(self._net)

        if overflow>0:
            pass

        return cost

    def _feasible_neighbor(self, tile : Tile, neighbor : Tile) ->bool:
        """Check if a neighboring tile is feasible.
            A neighboring tile is feasible, if the edge-capacity between the tiles 
            is greater than 0.

        Args:
            tile (Tile): Tile.
            neighbor (Tile): Neighboring tile.

        Returns:
            bool: True, if feasible, otherwise False.
        """
        e = neighbor.get_edge_name(tile)
        if e == 'H' or e=='L':
            e = 'I'

        if neighbor.get_edge_capacities(self._net)[e]>0:
            return True
        else:
            return False

    def astar(self, start : Tile, goal : Tile) -> list[Tile]|None:
        """A* algorithm to find a path from start to goal tile.

        Args:
            start (Tile): Starting tile.
            goal (Tile): Goal tile.

        Returns:
            list[Tile]|None: List of tiles, describing a path from start to goal.
                                If no path were found, None will be returned.
        """
        open_list = []
        closed_list = set()

        start.AstarData.set_g(0)
        start.AstarData.set_parent(None)

        heapq.heappush(open_list, (self.heuristic(start, goal), start))
        #heapq.heappush(open_list, (0, start))
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

            for neighbor in self._graph.get_neighbors(current_tile):
                if neighbor in closed_list:
                    continue
                
                if not self._feasible_neighbor(current_tile, neighbor):
                    continue
                
                tentative_score = current_tile.AstarData.g + self.get_cost(current_tile, neighbor)

                if tentative_score<neighbor.AstarData.g:
                    neighbor.AstarData.set_parent(current_tile)
                    neighbor.AstarData.set_g(tentative_score)
                    
                    if neighbor not in open_list:
                        heapq.heappush(open_list, (neighbor.AstarData.g+self.heuristic(neighbor, goal), neighbor))
                        #heapq.heappush(open_list, (neighbor.AstarData.g, neighbor))
                    else:
                        i = open_list.index(neighbor)
                        old_value = open_list.pop(i)
                        heapq.heapify(open_list)
                        heapq.heappush(open_list, (neighbor.AstarData.g+self.heuristic(neighbor, goal), neighbor))
                        #heapq.heappush(open_list, (neighbor.AstarData.g, neighbor))

        return None