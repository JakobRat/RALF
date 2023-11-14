from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABCMeta, abstractmethod
import math
import json
from pathlib import Path
from PDK.PDK import PDK, global_pdk
from PDK.Layers import Layer, MetalLayer, ViaLayer

import matplotlib.patches as patches
import matplotlib.pyplot as plt

class GridNode:
    """Class to store a Node of the detail routing grid.
    """
    def __init__(self, x : int, y : int, layer : Layer, parent = None, cost = 0) -> None:
        """Setup a node for the detail-routing grid.

        Args:
            x (int): x-coordinate
            y (int): y-coordinate
            layer (Layer): Layer of the node.
            parent (GridNode, optional): Parent grid node. Defaults to None.
            cost (int, optional): _description_. Defaults to 0.
        """
        assert isinstance(layer, Layer)
        self._x = x
        self._y = y
        self._layer = layer

        #definitions for a*
        self._parent = parent
        self._cost = cost
        self._g = 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self._x}, y={self._y}, l={self.layer})"

    @property
    def layer(self) -> Layer:
        """Get the layer of the node.

        Returns:
            Layer: Layer of the node.
        """
        return self._layer
    
    @property
    def coordinate(self) -> tuple[float, float]:
        """Get the x,y coordinate of the Node.

        Returns:
            tuple: (x,y)
        """
        return (self._x, self._y)
    
    @property
    def parent(self):
        """Get the parent of the node.

        Returns:
            GridNode|None: Parent node.
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
        """Get the total cost of the node.

        Returns:
            float: Total cost of the node.
        """
        return self._g
        
    def set_cost(self, cost : float):
        """Set the cost of the node.

        Args:
            cost (float): Cost of the node.
        """
        self._cost = cost

    def set_g(self, g : float):
        """Set the total cost of the node.

        Args:
            g (float): Total cost of the node.
        """
        self._g = g
    
    def set_parent(self, parent):
        """Set the parent of the node.

        Args:
            parent (GridNode): Parent node.
        """
        self._parent = parent

    @staticmethod
    def get_distance_between(node1, node2) -> float:
        """Get the manhattan distance between node1 and node2.

        Args:
            node1 (GridNode): First node.
            node2 (GridNode): Second node.

        Returns:
            float: Distance between the nodes.
        """
        assert isinstance(node1, GridNode)
        assert isinstance(node2, GridNode)

        return (abs(node1.coordinate[0]-node2.coordinate[0])+
                abs(node1.coordinate[1]-node2.coordinate[1])+
                abs(hash(node1.layer) - hash(node2.layer)))
    
    @staticmethod
    def get_direction_between(node1, node2) -> str:
        """Get the direction between the nodes.

        Args:
            node1 (GridNode): First node.
            node2 (GridNode): Second node.

        Raises:
            ValueError: If the nodes aren't vertically or horizontally aligned.
            ValueError: If the nodes aten't stacked. (If the layers aren't same.)

        Returns:
            str: H,V,VIA
        """
        assert isinstance(node1, GridNode)
        assert isinstance(node2, GridNode)
        if node1.layer == node2.layer: #if they share the same layer
            #check if they are vertically aligned
            if node1.coordinate[0] == node2.coordinate[0]:
                return 'V'
            #check if they are horizontally aligned
            elif node1.coordinate[1] == node2.coordinate[1]:
                return 'H'
            else:
                raise ValueError(f"Nodes {node1} and {node2} aren't aligned!")
        else: #they don't share a common layer -> via
            #check if they share neighboring layers
            if not abs(hash(node1.layer)-hash(node2.layer))>1:
                if node1.coordinate == node2.coordinate:
                    return 'VIA'
                else:
                    raise ValueError(f"Nodes {node1} and {node2} aren't stacked!")
            else:
                raise ValueError(f"Nodes {node1} and {node2} aren't stacked!")
            
    def __iter__(self):
        yield self._x
        yield self._y
        yield self._layer

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, GridNode):
            return NotImplemented
        
        return self._x == __value._x and self._y == __value._y and self._layer == __value._layer

    def __hash__(self) -> int:
        return hash((self._x, self._y, self._layer))
    
    def __lt__(self, obj: object):
        if not isinstance(obj, GridNode):
            return NotImplemented
        
        return self.coordinate < obj.coordinate and self.layer<obj.layer

    def __gt__(self, obj: object):
        if not isinstance(obj, GridNode):
            return NotImplemented
        
        return self.coordinate > obj.coordinate and self.layer>obj.layer

class GridEdge:
    """Class to store a grid edge, between two grid nodes.
    """
    def __init__(self, node1 : GridNode, node2 : GridNode) -> None:
        """Setup a grid edge, connecting two grid nodes.

        Args:
            node1 (GridNode): First node.
            node2 (GridNode): Second node.
        """
        self._node1 = node1
        self._node2 = node2

    @property
    def node1(self) -> GridNode:
        """Get the first grid node.

        Returns:
            GridNode: First grid node of the edge.
        """
        return self._node1
    
    @property
    def node2(self) -> GridNode:
        """Get the second grid node.

        Returns:
            GridNode: Second grid node of the edge.
        """
        return self._node2
    
    def __iter__(self):
        yield self.node1
        yield self.node2

    @property
    def length(self) -> float:
        """Get the length of the edge.

        Returns:
            float: Length of the edge.
        """
        return abs(self.node1.coordinate[0]-self.node2.coordinate[0])+abs(self.node1.coordinate[1]-self.node2.coordinate[1])
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, GridEdge):
            return NotImplemented
        
        return (self.node1==__value.node1 and self.node2 == __value.node2) or (self.node1==__value.node2 and self.node2==__value.node1)
    
    def __hash__(self) -> int:
        return hash((self.node1, self.node2))+hash((self.node2, self.node1))
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(n1={self.node1}, n2={self.node2})"
    
    @staticmethod
    def intersection(edge1, edge2):
        """Get the intersection node of edge1 and edge2.

        Args:
            edge1 (GridEdge): First edge.
            edge2 (GridEdge): Second edge.

        Returns:
            GridNode or None: If the edges intersect
        """
        assert isinstance(edge1, GridEdge)
        assert isinstance(edge2, GridEdge)
        if ((edge1.node1.layer == edge1.node2.layer)
            and (edge2.node1.layer == edge2.node2.layer) 
            and (edge1.node1.layer == edge2.node1.layer)):
            edge1 = list(sorted(list(edge1)))
            edge2 = list(sorted(list(edge2)))

            if edge1[0][1]==edge1[1][1]: #edge1 is horizontal
                if edge2[0][0]==edge2[1][0]: #edge2 is vertical
                    pass
                else:
                    return None
            else: #edge1 is vertical
                if edge2[0][1]==edge2[1][1]: #edge2 is horizontal
                    edge1, edge2 = edge2, edge1
                else:
                    return None
                
            if (edge2[0][0]>=edge1[0][0] and edge2[0][0]<=edge1[1][0]
                        and edge1[0][1]>=edge2[0][1] and edge1[0][1]<=edge2[1][1]): #edges intersect
                return GridNode(edge2[0][0], edge1[0][1], edge1[0][2])
            else:
                return None
        else:
            return None
        

class Conductor(metaclass = ABCMeta):
    """ Class to store a conductor.
    """
    def __init__(self, layer : Layer, length : float, width : float) -> None:
        """Setup a conductor on Layer <layer> with length <length> and width <width>.

        Args:
            layer (Layer): Layer of the conductor.
            length (float): Length of the conductor.
            width (float): Width of the conductor.
        """
        self._layer = layer
        self._length = length
        assert width>=layer.minWidth
        self._width = width
        
    @property
    def layer(self) -> Layer:
        """Get the layer of the conductor.

        Returns:
            Layer: Layer of the conductor.
        """
        return self._layer

    @property
    def width(self) -> float:
        """Get the width of the conductor.

        Returns:
            float: Width of the conductor.
        """
        return self._width
    
    @property
    def length(self) -> float:
        """Get the length of the conductor.

        Returns:
            float: Length of the conductor.
        """
        return self._length
    
    @property
    def resistance(self) -> float:
        """Get the resistance of the conductor, given by
            r = rho_sq * w/l                 

        Returns:
            float: Resistance of the conductor.
        """
        return self._layer.resistivity * self.length/self.width
    
    @property
    def area(self) -> float:
        """Get the area of the conductor.

        Returns:
            float: Area of the conductor.
        """
        return self.length * self.width
    
    def set_width(self, width : float):
        """Set the width of the conductor.

        Args:
            width (float): Width of the conductor.
        """
        self._width = width

    @abstractmethod
    def bound(self) -> tuple:
        """Get the 2d bound of the conductor.

        Returns:
            tuple: (x_min, y_min, x_max, y_max)
        """
        raise NotImplementedError
    
    @abstractmethod
    def bound3d(self) -> tuple:
        """Get the 3d bound of the conductor.

        Returns:
            tuple: (x_min, y_min, n_layer, x_max, y_max, n_layer)
        """
        raise NotImplementedError

    def blockage(self) -> tuple:
        """Get the box which defines the blocked area by the device.

        Returns:
            tuple: (x_min, y_min, x_max, y_max)
        """
        bound = self.bound()
        return (bound[0]-self.layer.minSpace, bound[1]-self.layer.minSpace, bound[2]+self.layer.minSpace, bound[3]+self.layer.minSpace)

    def blockage3d(self) -> tuple:
        """Get the 3d-box which defines the blocked area by the device.

        Returns:
            tuple: (x_min, y_min, n_layer, x_max, y_max, n_layer)
        """
        bound3d = self.bound3d()
        return (bound3d[0]-self.layer.minSpace, bound3d[1]-self.layer.minSpace, bound3d[2],
                bound3d[3]+self.layer.minSpace, bound3d[4]+self.layer.minSpace, bound3d[5])
    
    def blockage_enlarged(self, dw : float) -> tuple:
        """Get the enlarged blockage of the conductor.

        Args:
            dw (float): Amount of enlargement.

        Returns:
            tuple: Enlarged blockage. (x_min, y_min, x_max, y_max)
        """
        blockage = self.blockage()
        return (blockage[0]-dw, blockage[1]-dw, blockage[2]+dw, blockage[3]+dw)
    
    def blockage3d_enlarged(self, dw : float) -> tuple:
        """Get the enlarged blockage of the conductor.

        Args:
            dw (float): Amount of enlargement.

        Returns:
            tuple: (x_min, y_min, n_layer, x_max, y_max, n_layer)
        """
        blockage3d = self.blockage3d()
        return (blockage3d[0]-dw, blockage3d[1]-dw, blockage3d[2],
                blockage3d[3]+dw, blockage3d[4]+dw, blockage3d[5])
    
    @abstractmethod
    def generate_magic(self) -> str:
        """Generate a magic command to draw the conductor in magic.

            ToDo: Generalize for other tools.
        Returns:
            str: Magic command to draw the conductor.
        """
        pass

    def plot(self, ax, hatch=None):
        """Plot the conductor on axis <ax>, with the pattern given in <hatch>.

        Args:
            ax (axis): Axis on which the conductor shall be plotted.
            hatch (str, optional): Pattern of the conductor. Defaults to None.
        """
        bound = self.bound3d()
        #get a color map
        cm = plt.get_cmap('Set1')
        #get the color of the conductors layer
        color = cm(bound[2]%9)
        bound_rect = patches.Rectangle(
            (bound[0], bound[1]),
            bound[3]-bound[0],
            bound[4]-bound[1],
            edgecolor = color,
            linewidth=0.5,
            facecolor = color,
            fill=True,
            alpha=0.7,
            hatch=hatch,
        )
        ax.add_patch(bound_rect)

class Wire(Conductor, metaclass = ABCMeta):
    """Class to store a wire. A wire connects two grid nodes.
    """
    def __init__(self, edge : GridEdge, layer: Layer, length : float, width: float) -> None:
        """Setup a wire along the GridEdge <edge> on Layer <layer> with length <length> and width <width>.

        Args:
            edge (GridEdge): Edge of the wire.
            layer (Layer): Layer of the wire.
            length (float): Length of the wire.
            width (float): Width of the wire.
        """
        super().__init__(layer, length, width)
        
        self._edge = edge
        #store the direction of the wire
        self._direction = Wire._get_direction(edge)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(edge={self.edge}, l={self.layer}, w={self.width})"

    @staticmethod
    def _get_direction(edge : GridEdge) -> str|None:
        """Get the direction of the edge.

        Args:
            edge (GridEdge): Edge whose direction is searched. 

        Returns:
            str|None: One of 'N'-Via, 'V'-vertical, 'H'-horizontal
        """
        if edge.node1.layer != edge.node2.layer:
            if edge.node1.coordinate[0]==edge.node2.coordinate[0] and edge.node1.coordinate[1]==edge.node2.coordinate[1]:
                return 'N'
            else:
                return None
        else:
            if edge.node1.coordinate[0]==edge.node2.coordinate[0]:
                return 'V'
            elif edge.node1.coordinate[1]==edge.node2.coordinate[1]:
                return 'H'
            else:
                return None
        
    @property
    def edge(self) -> GridEdge:
        """
        Returns:
            GridEdge: Edge which connects the wire-nodes.
        """
        return self._edge
    
    @property
    def direction(self) -> str:
        """Get the direction of the wire.

        Returns:
            str: One of 'N'-Via, 'V'-vertical, 'H'-horizontal
        """
        return self._direction
    
class Via(Wire):
    """Class to store a Via.
    """
    def __init__(self, edge: GridEdge, width: float = None) -> None:
        """Setup a a Via on the edge.

        Args:
            edge (GridEdge): Edge of the via.
            width (float, optional): Width of the via. Defaults to None.
        """
        assert edge.node1.coordinate == edge.node2.coordinate, "Via top and bottom nodes not aligned!"
        assert type(edge.node1.layer)==MetalLayer, "Via top/bottom layer must be a MetalLayer"
        assert type(edge.node2.layer)==MetalLayer, "Via top/bottom layer must be a MetalLayer"
        assert abs(hash(edge.node1.layer)-hash(edge.node2.layer))==1, "Via-Plate layers must the neighboring layers!"
        
        #only square vias are supported.
        if width:
            super().__init__(edge, edge.node1.layer.get_via(edge.node2.layer), width, width)
        else:
            via_layer = edge.node1.layer.get_via(edge.node2.layer)
            super().__init__(edge, edge.node1.layer.get_via(edge.node2.layer), via_layer.minWidth, via_layer.minWidth)
        
        self._coordinate = edge.node1.coordinate

        #get the bottom and top node
        self._bottom_node = edge.node1 if edge.node1.layer == self.layer.bottom_layer else edge.node2
        self._top_node = edge.node1 if edge.node1.layer == self.layer.top_layer else edge.node2
        
        #setup top and bottom plates
        self._bottom_plate = ViaPlate(self._bottom_node, self.width+self.layer.minEnclosure_bottom*2, self)
        self._top_plate = ViaPlate(self._top_node, self.width+self.layer.minEnclosure_top*2, self)
        
        self._coordinate = self._bottom_node.coordinate
            
    @property
    def bottom_plate(self) -> ViaPlate:
        """Get the bottom plate of the via.

        Returns:
            ViaPlate: Bottom plate.
        """
        return self._bottom_plate
    
    @property
    def top_plate(self) -> ViaPlate:
        """Get the top plate of the via.

        Returns:
            ViaPlate: Top plate.
        """
        return self._top_plate
    
    @property
    def coordinate(self) -> tuple[float, float]:
        """Get the x and y coordinate of the via.

        Returns:
            tuple: (x,y)
        """
        return (self._coordinate[0], self._coordinate[1])
    
    def __hash__(self) -> int:
        return hash(self._edge)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Via):
            return NotImplemented
        return self._edge == __value._edge

    def bound(self):
        return (self.coordinate[0]-self.width/2, self.coordinate[1]-self.width/2, 
                self._coordinate[0]+self.width/2, self._coordinate[1]+self.width/2)
    
    def bound3d(self):
        return (self.coordinate[0]-self.width/2, self.coordinate[1]-self.width/2, hash(self.layer),
                self._coordinate[0]+self.width/2, self._coordinate[1]+self.width/2, hash(self.layer))
    
    def generate_magic(self) -> str:
        
        #generate the top plate
        top = self._top_plate.generate_magic()

        #generate the bottom plate if the plate isn't on layer 'li'
        # ToDo: generalize for other PDKs
        if self.bottom_plate.layer != 'li':
            bottom = self._bottom_plate.generate_magic()
        else:
            bottom = ""

        #generate the via
        via = f"wire segment {self.layer} {self.width} {int(round(self._coordinate[0]))} {int(round(self._coordinate[1]))} {int(round(self._coordinate[0]))} {int(round(self._coordinate[1]))}\n"
        return top + via + bottom
    
    def plot(self, ax):
        self._bottom_plate.plot(ax)
        super().plot(ax, hatch='///')
        self._top_plate.plot(ax)

class ViaPlate(Conductor):
    """Class to store a via plate.
    """
    def __init__(self, node: GridNode, width: float, via : Via) -> None:
        """Setup a via plate at GridNode <node>.

        Args:
            node (GridNode): Centerpoint of the plate.
            width (float): Width of the plate.
            via (Via): Via to which the plate belongs.
        """
        self._node = node
        self._layer = node.layer
        self._via = via
        super().__init__(self._layer, width, width)
        self._coordinate = self._node.coordinate

    @property
    def via(self) -> Via:
        """Get the via to which the plate belongs.

        Returns:
            Via: Via of the plate.
        """
        return self._via
    
    @property
    def node(self) -> GridNode:
        """Get the node at the centerpoint of the plate.

        Returns:
            GridNode: Node at the centerpoint of the plate.
        """
        return self._node
    
    @property
    def coordinate(self) -> tuple[float, float]:
        """Get the center coordinate of the plate.

        Returns:
            tuple[float, float]: (x,y)
        """
        return self._coordinate

    def __hash__(self) -> int:
        return hash((self._via, self._layer))

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ViaPlate):
            return NotImplemented
        return self._via == __value._via and self._layer==__value._layer
    
    def bound(self):
        return (self.coordinate[0]-self.width/2, self.coordinate[1]-self.width/2, self._coordinate[0]+self.width/2, self._coordinate[1]+self.width/2)

    def bound3d(self):
        return (self.coordinate[0]-self.width/2, self.coordinate[1]-self.width/2, hash(self.layer),
                self._coordinate[0]+self.width/2, self._coordinate[1]+self.width/2, hash(self.layer))
    
    def generate_magic(self) -> str:
        return f"wire segment {self.layer} {self.width} {int(round(self._coordinate[0]))} {int(round(self._coordinate[1]))} {int(round(self._coordinate[0]))} {int(round(self._coordinate[1]))}\n"
    
class Plate(Conductor):
    """Class to store a conducting plate.
    """
    def __init__(self, node : GridNode, length: float, width: float) -> None:
        """Setup a plate at GridNode <node>.

        Args:
            node (GridNode): Node at the centerpoint of the plate.
            length (float): Length of the plate. (along the x-axis)
            width (float): Width of the plate. (along the y-axis)
        """
        self._node = node
        super().__init__(node.layer, length, width)
        self._coordinate = node.coordinate

    def bound(self):
        c = self._node.coordinate
        w = self.width
        l = self.length
        return (c[0]-l/2, c[1]-w/2, c[0]+l/2, c[1]+w/2)
    
    def bound3d(self):
        c = self._node.coordinate
        w = self.width
        l = self.length
        return (c[0]-l/2, c[1]-w/2, hash(self.layer), c[0]+l/2, c[1]+w/2, hash(self.layer))
        
    def generate_magic(self) -> str:
        return f"wire segment {self.layer} {self.width} {int(round(self._coordinate[0]-self.length/2))} {int(round(self._coordinate[1]-self.length/2))} {int(round(self._coordinate[0]+self.length/2))} {int(round(self._coordinate[1]+self.length/2))} -noendcap\n"
    

class MetalWire(Wire):
    """Class to store a MetalWire.
    """
    def __init__(self, edge: GridEdge, width: float = None, left_offset : float = None, right_offset : float = None) -> None:
        """Setup a metal wire along the GridEdge <edge>.

                ---------------------------------   --
                |             edge              |   ^
                |       *---------------*       |   | width
                |                               |   Y
                ---------------------------------   --
                |<----->|               |<----->|
                 left offset             right offset
        Args:
            edge (GridEdge): Edge of the wire.
            width (float, optional): Width of the wire, if not specified, the min. width of the PDK will be used. Defaults to None.
            left_offset (_type_, optional): Offset at the left end of the wire. Defaults to None.
            right_offset (_type_, optional): Offset at the right end of the wire. Defaults to None.
        """

        self._endcap = True
        
        assert edge.node1.layer == edge.node2.layer, "MetalWire edges not on same layer!"

        if width:
            super().__init__(edge, edge.node1.layer, edge.length, width)
        else:
            super().__init__(edge, edge.node1.layer, edge.length, edge.node1.layer.minWidth)

        if left_offset:
            self._left_offset = left_offset
        else:
            self._left_offset = self.width/2
        
        if right_offset:
            self._right_offset = right_offset
        else:
            self._right_offset = self.width/2
        

        assert self.direction == 'H' or self.direction == 'V', "MetalWire has not supported direction!"
        
        #get the lower or left node
        self._node_ll = None
        #get the upper or right node
        self._node_ur = None
        
        if self._direction == 'H':
            self._node_ll = edge.node1 if edge.node1.coordinate[0]<=edge.node2.coordinate[0] else edge.node2
            self._node_ur = edge.node2 if self._node_ll == edge.node1 else edge.node1
        else:
            self._node_ll = edge.node1 if edge.node1.coordinate[1]<=edge.node2.coordinate[1] else edge.node2
            self._node_ur = edge.node2 if self._node_ll == edge.node1 else edge.node1   

    def __hash__(self) -> int:
        return hash(self._edge)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, MetalWire):
            return NotImplemented
        return self._edge == __value._edge
    
    def set_left_offset(self, offset : float):
        """Set the length of the left endcap.

        Args:
            offset (float): Left endcap length.
        """
        self._left_offset = offset

    def set_right_offset(self, offset : float):
        """Set the length of the right endcap.

        Args:
            offset (float): Right endcap length.
        """
        self._right_offset = offset
    
    def bound(self):
        c1 = self._node_ll.coordinate
        c2 = self._node_ur.coordinate
        w = self.width
        if self.direction == 'H':
            return (c1[0]-self._left_offset, c1[1]-w/2, c2[0]+self._right_offset, c2[1]+w/2)
        else:
            return (c1[0]-w/2, c1[1]-self._left_offset, c2[0]+w/2, c2[1]+self._right_offset)

    def bound3d(self):
        c1 = self._node_ll.coordinate
        c2 = self._node_ur.coordinate
        w = self.width
        if self.direction == 'H':
            return (c1[0]-self._left_offset, c1[1]-w/2, hash(self.layer), c2[0]+self._right_offset, c2[1]+w/2, hash(self.layer))
        else:
            return (c1[0]-w/2, c1[1]-self._left_offset, hash(self.layer), c2[0]+w/2, c2[1]+self._right_offset, hash(self.layer))

    def generate_magic(self) -> str:
        c1 = self._node_ll.coordinate
        c2 = self._node_ur.coordinate
        if self.direction == 'H':
            common_y = c1[1]
            x_left = c1[0]-self._left_offset
            x_right = c2[0]+self._right_offset

            return f"wire segment {self.layer} {self.width} {int(round(x_left))} {int(round(common_y))} {int(round(x_right))} {int(round(common_y))} -noendcap\n"
        else:
            common_x = c1[0]
            y_low = c1[1]-self._left_offset
            y_high = c2[1]+self._right_offset

            return f"wire segment {self.layer} {self.width} {int(round(common_x))} {int(round(y_low))} {int(round(common_x))} {int(round(y_high))} -noendcap\n"
