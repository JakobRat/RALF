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

from Routing_v2.Primitives import PDK
if TYPE_CHECKING:
    from Routing_v2.Path import Path
    from Magic.MagicTerminal import MagicPin
    from SchematicCapture.Net import Net
    from Magic.MagicDie import MagicDiePin, MagicDie
    from Routing_v2.WirePlanning import RoutePlanner

from itertools import count
from abc import ABCMeta, abstractmethod
from Routing_v2.Primitives import *
from PDK.PDK import global_pdk
from rtree import index
from SchematicCapture.Net import Net, same_root_net
from SchematicCapture.utils import get_all_primitive_devices
from Rules.RoutingRules import ObstacleRule

import os

from Routing_v2.Grid import global_grid
from PDK.PDK import global_pdk

from collections import deque

class GlobalObstacles:
    """Class to store obstacles for multiple routes and processing them.
    """
    def __init__(self) -> None:

        #store the obstacles of each net
        self._obstacles : dict[Net, list[Obstacles]]
        self._obstacles = {}

        #store general obstacles, which aren't linked with a net
        self._general_obstacles : list[Obstacle]
        self._general_obstacles = []

        #store a rtree for intersection retrieval
        self._rtree_obstacles = None
        
        #store the actual net and pdk for which the rtree were builded
        self._actual_net = None
        self._actual_pdk = None

        #store the area of each obstacle
        self._areas : dict[int, tuple[float, float, float, float, float, float]]
        self._areas = {}

        #store a map to link areas with obstacles
        self._id_obstacle_map : dict[int, Obstacles]
        self._id_obstacle_map = {}

        #setup a cache for obstacles
        self._cache_obstacles = deque(maxlen=100)
        #setup a cache for empty space
        self._cache_empty_space = deque(maxlen=100)

        #define a length for which will be searched for a empty space
        # ToDo: generalize
        self._empty_space_search_length = 14*10

    def add_obstacle(self, obstacle : Obstacles, net : Net):
        """Add a obstacle to the global obstacles.

        Args:
            obstacle (Obstacles): Obstacles.
            net (Net): Net to which the obstacles belongs.
        """
        if net in self._obstacles:
            self._obstacles[net].append(obstacle)
        else:
            self._obstacles[net] = [obstacle]
        
        #add the grid lines of the obstacles to the global grid
        global_grid.setup_grid_for_obstacles(obstacles=self.get_obstacle_list(), pdk=global_pdk)
        
    def add_general_obstacle(self, obstacle : Obstacle):
        """Add a obstacle without a net property, to the global obstacles.

        Args:
            obstacle (Obstacle): Obstacle to be added.
        """
        self._general_obstacles.append(obstacle)

    def get_obstacle_list(self) -> list[Obstacles]:
        """Get a list of all obstacles in the global obstacles.

        Returns:
            list[Obstacles]: List of obstacles.
        """
        obstacles = []
        for net, obstacle_list in self._obstacles.items():
            obstacles.extend(obstacle_list)
        
        obstacles.extend(self._general_obstacles)
        
        return obstacles

    def setup_obstacle_grid_for_pdk(self, pdk : PDK):
        """Setup the global grid for the obstacles in the global obstacles and PDK <pdk>.

        Args:
            pdk (PDK): PDK which shall be used fo setting up the grid.
        """
        self._actual_pdk = pdk
        global_grid.setup_grid_for_obstacles(obstacles=self.get_obstacle_list(), pdk=pdk)

    def setup_obstacle_grid_for_area(self, area : tuple[int, int, int, int], pdk : PDK, net : Net):
        """Setup the obstacle grid for obstacles in area <area> for PDK <pdk> and Net <net>.

        Args:
            area (tuple[int, int, int, int]): Area for which a obstacle grid shall be set up
            pdk (PDK): PDK which shall be used.
            net (Net): Specifies the net, for which obstacles aren't considered.
        """
        self._actual_pdk = pdk
        self._actual_net = net

        #setup the rtree
        self.setup_obstacle_rtree_for_net(net)

        #get all obstacles in the area on each layer
        obstacles = []
        for layer in pdk.metal_layers.values():
            bound_3d = (area[0], area[1], hash(layer), area[2], area[3], hash(layer))

            obstacles.extend(self.get_intersecting_obstacles(bound_3d=bound_3d))

        #setup the grid for the obstacles in this area 
        global_grid.setup_grid_for_obstacles(obstacles=obstacles, pdk=pdk)

    def setup_obstacle_grid_for_route_planner(self, plan : RoutePlanner, pdk : PDK, net : Net):
        """Setup a grid for the area defined by the plan of a RoutePlanner <plan>.

        Args:
            plan (RoutePlanner): Plan for which the grid shall be set up.
            pdk (PDK): PDK which shall be used.
            net (Net): Specifies the net, for which obstacles aren't considered.
        """
        self._actual_pdk = pdk
        self._actual_net = net
        self.setup_obstacle_rtree_for_net(net)
        
        #get all obstacles which intersect with tiles of the plan
        obstacles = []
        tiles_x = []
        tiles_y = []
        for tile in plan._actual_plan.nodes:
            
            bound_3d = (tile.bounding_box[0], tile.bounding_box[1], hash(tile.layer), tile.bounding_box[2], tile.bounding_box[3], hash(tile.layer))
            tiles_x.append((tile.bounding_box[0]+tile.bounding_box[2])/2)
            tiles_y.append((tile.bounding_box[1]+tile.bounding_box[3])/2)
            
            obstacles.extend(self.get_intersecting_obstacles(bound_3d=bound_3d))

        #setup the grid
        if len(obstacles)>0:
            #if there were obstacles, setup the grid for these obstacles.
            global_grid.setup_grid_for_obstacles(obstacles=obstacles, pdk=pdk)
        else:
            #no obstacle found
            # -> add all obstacles to the grid to make sure there will be a path
            self.setup_obstacle_grid_for_pdk(pdk)
        
    def setup_obstacle_rtree_for_net(self, net : Net|None):
        """Setup a rtree for the net <net>.

        Args:
            net (Net|None): If specified, the obstacles of Net <net> will not be included to the rtree.
        """
        #clear the caches
        self._cache_empty_space.clear()
        self._cache_obstacles.clear()

        #set the actual net
        self._actual_net = net

        #reset the areas
        self._areas = {}
        self._id_obstacle_map = {}

        #delete the last rtree
        if os.path.exists(f'RTreeObstacles/global_obstacle.data'):
            os.remove(f'RTreeObstacles/global_obstacle.data')

        if os.path.exists(f'RTreeObstacles/global_obstacle.index'):
            os.remove(f'RTreeObstacles/global_obstacle.index')

        #setup a new rtree
        p = index.Property()
        p.dimension = 3
        p.dat_extension = "data"
        p.idx_extension = "index"     
        self._rtree_obstacles = index.Index(f'RTreeObstacles/global_obstacle', properties=p)
        
        #add all obstacles to the rtree
        i_id = 0
        if not (net is None):
            #if a net were specified
            for obs_net, obstacles_list in self._obstacles.items():
                #iterate over all obstacles
                if not same_root_net(net, obs_net):
                    #only add obstacles if obs_net and net don't share a common net
                    for obstacles in obstacles_list:
                        #iterate over the obstacles in obstacles
                        for obstacle in obstacles.obstacles:
                            for area in obstacle.get_area_3d():
                                #insert the area into the rtree
                                self._rtree_obstacles.insert(i_id, area)
                                #save the area
                                self._areas[i_id] = area
                                #save a mapping to the obstacles
                                self._id_obstacle_map[i_id] = obstacles
                                i_id += 1
        else:
            #no net were specified
            for obs_net, obstacles_list in self._obstacles.items():
                #iterate over all obstacles
                for obstacles in obstacles_list:
                    #iterate over the obstacles in obstacles
                    for obstacle in obstacles.obstacles:
                        for area in obstacle.get_area_3d():
                            #insert the area into the rtree
                            self._rtree_obstacles.insert(i_id, area)
                            #save the area
                            self._areas[i_id] = area
                            #save a mapping to the obstacles
                            self._id_obstacle_map[i_id] = obstacles
                            i_id += 1

        #add general obstacles
        for obstacle in self._general_obstacles:
            for area in obstacle.get_area_3d():
                #insert the area into the rtree
                self._rtree_obstacles.insert(i_id, area)
                #save the area
                self._areas[i_id] = area
                #save a mapping to the obstacle
                self._id_obstacle_map[i_id] = obstacle
                i_id += 1

    def get_obstacles_in_area(self, bound_3d : tuple) -> list[tuple]:
        """Get all obstacles which intersect with the area defined by <bound_3d>.

        Args:
            bound_3d (tuple): (min_x, min_y, layer, max_x, max_y, layer)

        Returns:
            list[tuple]: List of 3d-areas.
        """
        assert not (self._rtree_obstacles is None), f"No rtree set for area check!"

        #get a list of area id's which intersect with the bound.
        intersections = list(self._rtree_obstacles.intersection(bound_3d))
        #return a list of the areas
        return [self._areas[i] for i in intersections]
    
    def intersects(self, node : GridNode, offset : float = 0.0) -> bool:
        """Check if a node intersects with one of the obstacles.

        Args:
            node (GridNode): Node to be checked.
            offset (float, optional): Expansion of the node-point to a square with side lengths: 2*offset. Defaults to 0.0.

        Returns:
            bool: True, if the node intersects with a obstacle, otherwise False.
        """
        assert not (self._actual_net is None), f"No net set for feasibility check!"
        assert not (self._actual_pdk is None), f"No PDK set for feasibility check!"
        assert not (self._rtree_obstacles is None), f"No rtree set for feasibility check!"
        
        #expand the node to a square with side length 2*offset
        bound_3d = (node.coordinate[0]-offset, node.coordinate[1]-offset, hash(node.layer),
                    node.coordinate[0]+offset, node.coordinate[1]+offset, hash(node.layer))
        
        #check if the square lies in a cached space to early stop
        if self._lies_in_space_cache(bound3d=bound_3d):
            return False

        #check if the square intersects with a cached obstacle
        if self._intersects_with_obstacle_cache(bound_3d):
            return True

        #get all intersections with obstacles
        intersections = list(self._rtree_obstacles.intersection(bound_3d))
        if len(intersections)>0:
            #if there were intersections, add the areas of the obstacles to the cache
            for intersection_id in intersections:
                #append at the left to the cache, such that last inserted obstacles 
                #will be first checked
                self._cache_obstacles.appendleft(self._areas[intersection_id])
        else:
            #no intersection -> add the node to the space cache
            self._add_to_space_cache(node=node)

        #return True if there were intersections, else False
        return len(intersections)>0
    
    def intersects_with_area(self, bound_3d : tuple[int, int, int, int, int, int]) -> bool:
        """Check if a 3d-area intersects with one of the obstacles.

        Args:
            bound_3d (tuple[int, int, int, int, int, int]): (min_x, min_y, n_layer, max_x, max_y, n_layer)

        Returns:
            bool: True, if the node intersects with a obstacle, otherwise False.
        """
        assert not (self._actual_net is None), f"No net set for feasibility check!"
        assert not (self._actual_pdk is None), f"No PDK set for feasibility check!"
        assert not (self._rtree_obstacles is None), f"No rtree set for feasibility check!"
        
        #check if the bound lies in a cached space, for early stopping
        if self._lies_in_space_cache(bound3d=bound_3d):
            return False

        #check if the bound intersects with a cached obstacle
        if self._intersects_with_obstacle_cache(bound_3d):
            return True

        #get all intersections with obstacles
        intersections = list(self._rtree_obstacles.intersection(bound_3d))
        if len(intersections)>0:
            #if there were intersections, add the areas of the obstacles to the cache
            for intersection_id in intersections:
                #append at the left to the cache, such that last inserted obstacles 
                #will be first checked
                self._cache_obstacles.appendleft(self._areas[intersection_id])
        else:
            #no intersection -> add the bound to the space cache
            self._cache_empty_space.appendleft(tuple(bound_3d))
        
        #return True if there were intersections, else False
        return len(intersections)>0
    
    def get_intersecting_obstacles(self, bound_3d : tuple[int, int, int, int, int, int]) -> list[Obstacle]:
        """Get all obstacles which intersect with the 3d area <bound_3d>.

        Args:
            bound_3d (tuple[int, int, int, int, int, int]): Boundary of the area which is searched.

        Returns:
            list[Obstacle]: All obstacles which intersect with this area.
        """
        assert not (self._actual_net is None), f"No net set for feasibility check!"
        assert not (self._actual_pdk is None), f"No PDK set for feasibility check!"
        assert not (self._rtree_obstacles is None), f"No rtree set for feasibility check!"

        #get a list of all intersecting areas
        intersections = list(self._rtree_obstacles.intersection(bound_3d))

        #get the obstacles of the areas
        obstacles = set()
        for i in intersections:
            obstacles.add(self._id_obstacle_map[i])
        
        return list(obstacles)

    def _add_to_space_cache(self, node : GridNode):
        """Add the free space of a node, to the free space cache.

        Args:
            node (GridNode): Node for which the free space shall be added.
        """
        #expand the node by the search length for an empty space 
        offset = self._empty_space_search_length
        bound_3d = (node.coordinate[0]-offset, node.coordinate[1]-offset, hash(node.layer),
                    node.coordinate[0]+offset, node.coordinate[1]+offset, hash(node.layer))
        #get all intersecting areas
        intersections = list(self._rtree_obstacles.intersection(bound_3d))
        
        node_c = node.coordinate

        bound_3d = list(bound_3d)
        #shrink the free space for each intersection with a obstacle
        for i in intersections:
            area = self._areas[i]
            #area = (x_min, y_min, layer, x_max, y_max, layer)
            if area[0]<node_c[0] and area[3]<node_c[0]: #obstacle is left of node
                bound_3d[0] = max(bound_3d[0], area[3])
            elif area[0]>node_c[0] and area[3]>node_c[0]: #obstacle is right of node
                bound_3d[3] = min(bound_3d[3], area[0])
            elif area[1]<node_c[1] and area[4]<node_c[1]: #obstacle is below of node
                bound_3d[1] = max(bound_3d[1], area[4])
            elif area[1]>node_c[1] and area[4]>node_c[1]: #obstacle is above of node
                bound_3d[4] = min(bound_3d[4], area[1])
            else:
                assert ValueError
        #add the free space to the cache
        self._cache_empty_space.appendleft(tuple(bound_3d))

    def _intersects_with_obstacle_cache(self, bound3d : tuple) -> bool:
        """Check if a 3d bounding box intersects with a obstacle in the cache.

        Args:
            bound3d (tuple): (min_x, min_y, layer, max_x, max_y, layer)

        Returns:
            bool: True, if there is a intersection, else False.
        """
        #iterate over each area of the cache
        for area in self._cache_obstacles:
            if GlobalObstacles.intersecting_areas(bound3d, area):
                return True
        
        return False

    def _lies_in_space_cache(self, bound3d : tuple) -> bool:
        """Check if a 3d bounding box is enclosed by a bounding box in the space cache.

        Args:
            bound3d (tuple): (min_x, min_y, layer, max_x, max_y, layer)

        Returns:
            bool: True, if the boundary lies in the space cache, else False.
        """
        for area in self._cache_empty_space:
            if GlobalObstacles.is_inside(bound3d, area):
                return True
        
        return False
    
    @staticmethod
    def intersecting_areas(bound1 : tuple, bound2 : tuple) -> bool:
        """Check if two areas are intersecting.

        Args:
            bound1 (tuple): (min_x, min_y, layer, max_x, max_y, layer)
            bound2 (tuple): (min_x, min_y, layer, max_x, max_y, layer)

        Returns:
            bool: True, if they intersect, otherwise False.
        """
        if bound1[2]==bound2[2]:
            EX1 = bound1[0] - bound2[3]
            EX2 = bound1[3] - bound2[0]
            EX3 = bound1[4] - bound2[1]
            EX4 = bound1[1] - bound2[4]

            if EX1>0 or EX2<0 or EX3<0 or EX4>0: #rects do not overlap
                return False
            else:
                return True
        else: #different layers
            return False
    
    @staticmethod
    def is_inside(bound1 : tuple, bound2 : tuple) -> bool:
        """Checks if bound1 is inside bound2.

        Args:
            bound1 (tuple): 1st rectangle (min_x, min_y, layer, max_x, max_y, layer)
            bound2 (tuple): 2nd rectangle (min_x, min_y, layer, max_x, max_y, layer)

        Returns:
            bool: True if bound1 is inside bound2 (including edges).
        """
        if bound1[2]==bound2[2]:
            EX1 = bound1[0] - bound2[0]
            EX2 = bound1[3] - bound2[3]
            EX3 = bound1[1] - bound2[1]
            EX4 = bound1[4] - bound2[4]

            if EX1>=0 and EX2<=0 and EX3>=0 and EX4<=0:
                return True
            else:
                return False
        else: #different layers
            return False

#setup a global variable for the global-obstacles
global_obstacles = GlobalObstacles()

class Obstacles:
    """Class to store the obstacles of a net.
    """
    def __init__(self, net : Net) -> None:
        """Setup a storage for obstacles for Net <net>.

        Args:
            net (Net): Net to which the obstacles belong.
        """
        self._net = net
        self._name = net.name
        self._obstacles = {}

    @property
    def obstacles(self) -> list[Obstacle]:
        """Get a list of stored obstacles.

        Returns:
            list[Obstacle]: List of Obstacles.
        """
        return list(self._obstacles.values())

    @property
    def net(self) -> Net:
        """Get the net of the obstacles.

        Returns:
            Net: Net of the obstacles.
        """
        return self._net

    def add_obstacle(self, obstacle : Obstacle):
        """Add a obstacle to the obstacle storage.

        Args:
            obstacle (Obstacle): Obstacle which shall be added.
        """
        self._obstacles[obstacle] = obstacle
        
    def remove_obstacle(self, obstacle : Obstacle):
        """Remove a obstacle from the obstacle dict.

        Args:
            obstacle (Obstacle): Obstacle which shall be removed.
        """
        if obstacle in self._obstacles:
            del self._obstacles[obstacle]

    def grid_lines(self, pdk : PDK) -> tuple[list, list]:
        """Get the grid lines defined by the obstacles.

        Args:
            pdk (PDK): PDK which shall be used for the generation.

        Returns:
            tuple[list, list]: (grid_x, grid_y)
        """
        #get all grid-lines of the obstacles
        grid_x = []
        grid_y = []
        obstacle : Obstacle
        for obstacle in self._obstacles.values():
            x,y = obstacle.grid_lines(pdk=pdk)
            grid_x.extend(x)
            grid_y.extend(y)
        
        #return sorted, non-duplicating lists of x & y grid lines.
        grid_x = set(grid_x)
        grid_y = set(grid_y)

        sorted(grid_x)
        sorted(grid_y)

        return (list(grid_x), list(grid_y))
    
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Obstacles) and self._net == __value._net
    
    def __hash__(self) -> int:
        return hash(self._net)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(net={self._net})"

class DieObstacles:
    """Class to store obstacles of a die.
    """
    def __init__(self, die : MagicDie) -> None:
        """Class to register obstacles from a Die to the global_obstacles.

        Args:
            die (MagicDie): MagicDie
        """
        self._die = die
        self._obstacles = {}
        self._general_obstacles = []
        self._setup_die_obstacles()

    def _setup_die_obstacles(self):
        #add the die pins as obstacles
        if not (self._die.pins is None):
            for net, die_pins in self._die.pins.items():
                self._obstacles[net] = Obstacles(net)
                global_obstacles.add_obstacle(self._obstacles[net], net)
                for pin in die_pins:
                    obstacle = PinObstacle(pin=pin)
                    self._obstacles[net].add_obstacle(obstacle)
        
        #add the route-obstacles
        prim_devices = get_all_primitive_devices(self._die.circuit)

        for device in prim_devices:
            rules = device.get_routing_rules()
            for rule in rules:
                if type(rule)==ObstacleRule:
                    obstacle = RouteObstacle(rule)
                    self._general_obstacles.append(obstacle)
                    global_obstacles.add_general_obstacle(obstacle=obstacle)
            
class Obstacle(metaclass = ABCMeta):
    """Abstract class for a obstacle.
    """
    #setup a counter, to generate unique id's
    obstacle_id = count()
    def __init__(self, net : Net = None) -> None:
        """Setup a obstacle for Net <net>.

        Args:
            net (Net, optional): If specified, the obstacle belongs to Net <net>.. Defaults to None.
        """
        self._net = net
        self._id = Obstacle.obstacle_id.__next__()
        
        if not (net is None):
            self._name = f"{net.name}_{self._id}"
        else:
            self._name = f"{__class__.__name__}_{self._id}"
    
    @property
    def net(self) -> Net|None:
        """Get the net of the obstacle.

        Returns:
            Net|None: Net object.
        """
        return self._net

    @abstractmethod
    def get_area(self) -> list[tuple[int, int, int, int]]:
        """Get the area of the unexpanded obstacle.
            -> Area which is blocked by the obstacle, and no other Via/Wire can be placed.
        Returns:
            list[tuple[int, int, int, int]]: (x_min, y_min, x_max, y_max)
        """
        pass
    
    @abstractmethod
    def get_area_3d(self) -> list[tuple[int, int, int, int, int, int]]:
        """Get the 3d-area of the unexpanded obstacle.
            -> Area which is blocked by the obstacle, and no other Via/Wire can be placed.
        Returns:
            list[tuple[int, int, int, int, int, int]]: (x_min, y_min, layer, x_max, y_max, layer)
        """
        pass
    
    @abstractmethod
    def get_area_enlarged(self, pdk : PDK) -> list[tuple[int, int, int, int]]:
        """Get the area of the expanded obstacle for PDK <pdk>.
            -> The boundary of the areas define the grid-lines where 
               Vias and Wires under PDK <pdk> can be placed, without 
               violating minSpace DRC errors.

        Args:
            pdk (PDK): PDK which shall be used for expansion.

        Returns:
            list[tuple[int, int, int, int]]: (x_min, y_min, x_max, y_max)
        """
        pass

    def grid_lines(self, pdk : PDK) -> tuple[list[int], list[int]]:
        """Get the grid lines which are induced from the obstacle.

        Args:
            pdk (PDK): PDK which will be used for obstacle expansion.

        Returns:
            tuple[list[int], list[int]]: (x-grid lines, y-grid lines)
        """

        #get the expanded area of the obstacle
        areas = self.get_area_enlarged(pdk=pdk)
        x_lines = set()
        y_lines = set()
        
        #add the boundary-lines of each area to the grid-lines
        for area in areas:
            x_lines.add(area[0])
            x_lines.add(area[2])
            y_lines.add(area[1])
            y_lines.add(area[3])
        
        return (list(x_lines), list(y_lines))
      
    def get_expansion_for_wire(self, pdk : PDK, layer : Layer) -> float:
        """Get the width by which a obstacle must be expanded, to draw a valid wire.

        Args:
            pdk (PDK): PDK of the wire to be drawn.
            layer (Layer): layer of the obstacle.

        Returns:
            float: Width of the expansion.
        """
        pdk_layer = pdk.get_layer(str(layer))

        return pdk_layer.width/2

    def get_expansion_for_via(self, pdk : PDK, layer : Layer) -> tuple[float, float]:
        """Get the width by which a obstacle must be expanded, to draw a valid via.

        Args:
            pdk (PDK): PDK of the wire to be drawn.
            layer (Layer): layer of the obstacle.

        Returns:
            tuple[float, float]: (Width of the expansion for the lower via, Width of the expansion for the higher via).
        """
        #get the layers
        pdk_layer = pdk.get_layer(str(layer))
        higher_layer = pdk.get_higher_metal_layer(pdk_layer)
        lower_layer = pdk.get_lower_metal_layer(pdk_layer)
        
        dw_h = 0
        dw_l = 0

        #calculate the expansion values for lower and higher layer
        if not (higher_layer is None):
            #expansion based on the bottom-plate of the via
            via_layer = pdk.get_via_layer(pdk_layer, higher_layer)
            dw_h = via_layer.width/2+via_layer.minEnclosure_bottom

        if not (lower_layer is None):
            #expansion based on the top-plate of the via
            via_layer = pdk.get_via_layer(pdk_layer, lower_layer)
            dw_l = via_layer.width/2+via_layer.minEnclosure_top

        return (dw_l, dw_h)
    
    def expand_primitive_for_wire(self, pdk : PDK, primitive : Conductor) -> list[tuple[int, int, int, int]]:
        """Expand a primitive for a wire.

        Args:
            pdk (PDK): PDK of the wire.
            primitive (Conductor): Primitive to be expanded.

        Returns:
            list[tuple[int, int, int, int]]: Expanded areas.
        """
        areas = []
        if type(primitive)==Via:
            bottom_plate = primitive.bottom_plate
            top_plate = primitive.top_plate
            areas.append(bottom_plate.blockage_enlarged(self.get_expansion_for_wire(pdk, bottom_plate.layer)))
            areas.append(top_plate.blockage_enlarged(self.get_expansion_for_wire(pdk, top_plate.layer)))
        else:
            areas.append(primitive.blockage_enlarged(self.get_expansion_for_wire(pdk, primitive.layer)))
        
        return areas
    
    def expand_primitive_for_via(self, pdk : PDK, primitive : Conductor) -> list[tuple[int, int, int, int]]:
        """Expand a primitive for a via.

        Args:
            pdk (PDK): PDK
            primitive (Conductor): Primitive to be expanded.

        Returns:
            list[tuple[int, int, int, int]]: Expanded areas.
        """
        areas = []
        if type(primitive)==Via:
            bottom_plate = primitive.bottom_plate
            top_plate = primitive.top_plate
            #expand the bottom plate
            for dw in self.get_expansion_for_via(pdk, bottom_plate.layer):
                if dw>0:
                    areas.append(bottom_plate.blockage_enlarged(dw))

            #expand the top plate
            for dw in self.get_expansion_for_via(pdk, top_plate.layer):
                if dw>0:
                    areas.append(top_plate.blockage_enlarged(dw))
        else:
            #expand the wire
            for dw in self.get_expansion_for_via(pdk, primitive.layer):
                if dw>0:
                    areas.append(primitive.blockage_enlarged(dw))
        
        return areas
    
    def __hash__(self) -> int:
        return self._id
    
    def __eq__(self, __value: object) -> bool:
        return (isinstance(__value, Obstacle)) and self._id == __value._id
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(net={self._net}, id={self._id})"

class PathObstacle(Obstacle):
    """Class to setup a obstacle for a path.
    """
    def __init__(self, path : Path, net : Net) -> None:
        """Setup a obstacle for a path.

        Args:
            path (Path): Path for which a obstacle shall be set up.
            net (Net): Net of the obstacle.
        """
        assert path
        self._path = path
        super().__init__(net=net)
        

    def get_area(self) -> list[tuple[int, int, int, int]]:
        
        areas = []
        #iterate over each primitive of the path
        for primitive in self._path.primitives:
            #add the blocked area of each primitive to the areas
            if type(primitive)==Via:
                areas.append(primitive.bottom_plate.blockage())
                areas.append(primitive.top_plate.blockage())
            else:
                areas.append(primitive.blockage())
        
        return areas
    
    def get_area_3d(self) -> list[tuple[int, int, int, int, int, int]]:
        areas = []
        #iterate over each primitive of the path
        for primitive in self._path.primitives:
            #add the blocked area of each primitive to the areas
            if type(primitive)==Via:
                areas.append(primitive.bottom_plate.blockage3d())
                areas.append(primitive.top_plate.blockage3d())
            else:
                areas.append(primitive.blockage3d())
        return areas

    def get_area_enlarged(self, pdk: PDK) -> list[tuple[int, int, int, int]]:
        areas = []
        
        #iterate over each primitive of the path
        for primitive in self._path.primitives:
            #add the expanded areas for wires
            areas.extend(self.expand_primitive_for_wire(pdk=pdk, primitive=primitive))

            #don't add expanded areas for vias, to reduce the number of grid lines
            #to improve the runtime
            #areas.extend(self.expand_primitive_for_via(pdk=pdk, primitive=primitive))
        
        return areas
    
class PinObstacle(Obstacle):
    """Class to setup a obstacle for a path.
    """
    def __init__(self, pin : MagicPin) -> None:
        """Setup a obstacle for a pin.

        Args:
            pin (MagicPin): Pin for which a obstacle shall be generated.
        """
        self._pin = pin
        if self._pin.layer == 'li':
            #if the pin is at 'li' -> a via will be inserted for the pin.
            # ToDo: Generalize for other PDKs
            node1 = GridNode(*self._pin.get_coordinate_on_grid(), layer=global_pdk.get_layer('li'))
            node2 = GridNode(*self._pin.get_coordinate_on_grid(), layer=global_pdk.get_higher_metal_layer('li'))
            edge = GridEdge(node1, node2)
            self._primitive = Via(edge)
        else:
            #generate a plate as obstacle
            node = GridNode(*self._pin.get_coordinate_on_grid(), layer=pin.layer)
            pin_bound = self._pin.get_bounding_box_on_grid()
            w = pin_bound.width
            h = pin_bound.height

            self._primitive = Plate(node=node, length=w, width=h)
        
        super().__init__(net=pin.net)

    
    def get_area(self) -> list[tuple[int, int, int, int]]:
        if type(self._primitive)==Via:
            return [self._primitive.bottom_plate.blockage(), self._primitive.top_plate.blockage()]
        else:
            return [self._primitive.blockage()]
    
    def get_area_3d(self) -> list[tuple[int, int, int, int, int, int]]:
        if type(self._primitive)==Via:
            return [self._primitive.bottom_plate.blockage3d(), self._primitive.top_plate.blockage3d()]
        else:
            return [self._primitive.blockage3d()]
    
    def get_area_enlarged(self, pdk: PDK) -> list[tuple[int, int, int, int]]:
        areas = []
        
        #add the expanded areas for wires
        areas.extend(self.expand_primitive_for_wire(pdk=pdk, primitive=self._primitive))

        #don't add expanded areas for vias, to reduce the number of grid lines
        #to improve the runtime
        #areas.extend(self.expand_primitive_for_via(pdk=pdk, primitive=self._primitive))
        
        return areas
    
class DiePinObstacle(Obstacle):
    """Class to store a obstacle for a DiePin.
    """
    def __init__(self, pin : MagicDiePin) -> None:
        """Setup a obstacle for a die-pin.

        Args:
            pin (MagicDiePin): DiePin for which a obstacle shall be generated.
        """
        self._pin = pin
        if self._pin.layer == 'li':
            node1 = GridNode(*self._pin.coordinate, layer=global_pdk.get_layer('li'))
            node2 = GridNode(*self._pin.coordinate, layer=global_pdk.get_higher_metal_layer('li'))
            edge = GridEdge(node1, node2)
            self._primitive = Via(edge)
        else:
            node = GridNode(*self._pin.coordinate, layer=pin.layer)
            w = self._pin.bounding_box.width
            h = self._pin.bounding_box.height

            self._primitive = Plate(node=node, length=w, width=h)

        super().__init__(net=pin.net)
    
    def get_area(self) -> list[tuple[int, int, int, int]]:
        if type(self._primitive)==Via:
            return [self._primitive.bottom_plate.blockage(), self._primitive.top_plate.blockage()]
        else:
            return [self._primitive.blockage()]
    
    def get_area_3d(self) -> list[tuple[int, int, int, int, int, int]]:
        if type(self._primitive)==Via:
            return [self._primitive.bottom_plate.blockage3d(), self._primitive.top_plate.blockage3d()]
        else:
            return [self._primitive.blockage3d()]
        
    def get_area_enlarged(self, pdk: PDK) -> list[tuple[int, int, int, int]]:
        areas = []
        
        areas.extend(self.expand_primitive_for_wire(pdk=pdk, primitive=self._primitive))
        #areas.extend(self.expand_primitive_for_via(pdk=pdk, primitive=self._primitive))
        
        return areas

class RouteObstacle(Obstacle):
    """Class to store a general obstacle defined by a ObstacleRule.
    """
    def __init__(self, rule : ObstacleRule, net: Net = None) -> None:
        """Setup a obstacle for a rule.

        Args:
            rule (ObstacleRule): Rule which defines a obstacle.
            net (Net, optional): Net of the rule. Defaults to None.
        """
        self._rule = rule
        super().__init__(net)
    
    def get_area(self) -> list[tuple[int, int, int, int]]:
        area = self._rule.get_area()
        return [area]

    def get_area_3d(self) -> list[tuple[int, int, int, int, int, int]]:
        area = self._rule.get_area()
        layer_id = hash(self._rule.layer)
        area_3d = (area[0], area[1], layer_id, area[2], area[3], layer_id)
        return [area_3d]
    
    def get_area_enlarged(self, pdk: PDK) -> list[tuple[int, int, int, int]]:
        layer = self._rule.layer
        offset = layer.minSpace + pdk.get_layer(str(layer)).width/2
        area = self._rule.get_area()
        area_enlarged = (area[0]-offset, area[1]-offset, area[2]+offset, area[3]+offset)
        return [area_enlarged]