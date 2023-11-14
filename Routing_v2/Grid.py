from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Magic.MagicTerminal import MagicPin
    from Magic.MagicDie import MagicDiePin
    from Routing_v2.Obstacles import Obstacles
    from PDK.PDK import PDK

from Routing_v2.Primitives import GridNode
from PDK.PDK import global_pdk

class Grid:
    """Class to store a detail-routing grid.
    """
    def __init__(self) -> None:
        
        self._pin_grid_x = set()
        self._pin_grid_y = set()

        self._obstacle_grid_x = set()
        self._obstacle_grid_y = set()

        self._grid_x = set()
        self._grid_y = set()

    def setup_grid_for_pins(self, pins : list[MagicPin|MagicDiePin]):
        """Setup the grid, to include the x-y coordinates of the pins in <pins>.

        Args:
            pins (list[MagicPin | MagicDiePin]): List of pins, which shall be included.
        """
        self._pin_grid_x = set()
        self._pin_grid_y = set()

        for pin in pins:
            #add the coordinate of the pin which lies on the lambda grid.
            c = pin.get_coordinate_on_grid()
            self._pin_grid_x.add(c[0])
            self._pin_grid_y.add(c[1])
        
        self._pin_grid_x = sorted(self._pin_grid_x)
        self._pin_grid_y = sorted(self._pin_grid_y)

    @property
    def dimension(self) -> tuple[int, int]:
        """Get the grid-dimension

        Returns:
            tuple[int, int]: (number of x coordinates, number of y coordinates)
        """
        return (len(self._grid_x), len(self._grid_y))
    
    def setup_grid_for_obstacles(self, obstacles : list[Obstacles], pdk : PDK):
        """Setup the grid for the obstacles given in obstacles.

        Args:
            obstacles (list[Obstacles]): List of obstacles.
            pdk (PDK): PDK which shall be used.
        """
        self._obstacle_grid_x = set()
        self._obstacle_grid_y = set()
        
        #iterate over each obstacle and add the grid lines
        for obstacle in obstacles:
            grid_x, grid_y = obstacle.grid_lines(pdk=pdk)
            self._obstacle_grid_x.update(set(grid_x))
            self._obstacle_grid_y.update(set(grid_y))

        self._grid_x = set()
        self._grid_y = set()

        #add the pins to the grid
        self._grid_x.update(self._pin_grid_x)
        #add the obstacles to the grid
        self._grid_x.update(self._obstacle_grid_x)
        self._grid_x=sorted(self._grid_x)

        self._grid_y.update(self._pin_grid_y)
        self._grid_y.update(self._obstacle_grid_y)
        self._grid_y = sorted(self._grid_y)

    def setup_grid_for_path(self, start : GridNode, goal : GridNode):
        """Setup the grid, such that the coordinates of <start> and <goal> are included,
            and previously defined grid-lines of obstacles.

        Args:
            start (GridNode): Start node.
            goal (GridNode): Goal node.
        """
        self._grid_x = set()
        self._grid_y = set()
        
        self._grid_x.update(self._obstacle_grid_x)
        self._grid_y.update(self._obstacle_grid_y)

        self._grid_x.add(start.coordinate[0])
        self._grid_x.add(goal.coordinate[0])
        self._grid_y.add(start.coordinate[1])
        self._grid_y.add(goal.coordinate[1])

        self._grid_x = sorted(self._grid_x)
        self._grid_y = sorted(self._grid_y)
    
    def add_grid_lines(self, x_lines : list, y_lines : list):
        """Add grid lines to the actual grid.

        Args:
            x_lines (list): List of x-coordinates which shall be added.
            y_lines (list): List of y-coordinates which shall be added.
        """
        self._grid_x = set(self._grid_x)
        self._grid_y = set(self._grid_y)
        self._grid_x.update(set(x_lines))
        self._grid_y.update(set(y_lines))
        self._grid_x = sorted(self._grid_x)
        self._grid_y = sorted(self._grid_y)
        
    def get_neighbors(self, node : GridNode) -> list[GridNode]:
        """Get the neighbors of the node <node>.

        Args:
            node (GridNode): Node for which the neighbors shall be found.

        Returns:
            list[GridNode]: List of neighboring grid nodes.
        """
        grid_x = list(self._grid_x)
        grid_y = list(self._grid_y) 
        i = grid_x.index(node.coordinate[0])
        j = grid_y.index(node.coordinate[1])

        neighbors = []

        #add lower layer node
        try: 
            lower_layer = global_pdk.get_lower_metal_layer(str(node.layer))
            if lower_layer != 'li':
                neighbors.append(GridNode(*node.coordinate, lower_layer))
        except:
            pass
        
        #add higher layer node
        try: 
            higher_layer = global_pdk.get_higher_metal_layer(str(node.layer))
            neighbors.append(GridNode(*node.coordinate, higher_layer))
        except:
            pass
        
        #add left node
        if i>0:
            x = grid_x[i-1]
            y = grid_y[j]

            neighbors.append(GridNode(x,y, node.layer))
        
        #add lower node
        if j>0:
            x = grid_x[i]
            y = grid_y[j-1]

            neighbors.append(GridNode(x,y, node.layer))

        #add right node
        if i+1<len(grid_x):
            x = grid_x[i+1]
            y = grid_y[j]

            neighbors.append(GridNode(x,y, node.layer))
        
        #add higher node
        if j+1<len(grid_y):
            x = grid_x[i]
            y = grid_y[j+1]

            neighbors.append(GridNode(x,y, node.layer))

        return neighbors

#setup a global grid
global_grid = Grid()