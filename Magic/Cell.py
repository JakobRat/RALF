# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:27:44 2023

@author: jakob
"""
from __future__ import annotations

from Magic.MagicLayer import MagicLayer, Rectangle, Color

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SchematicCapture.Devices import Device
    from Rules.PlacementRules import PlacementRules

from Magic.MagicTerminal_utils import *

class Cell:
    """Class to store the cell-view of a device.
    """
    def __init__(self, name : str, layer_stack : dict[str, MagicLayer], device : Device = None):
        """Setup a cell-view of a device.

        Args:
            name (str): Name of the cell.
            layer_stack (dict[str, MagicLayer]): Layers of the cell, key: Layer name, value: MagicLayer.
            device (Device, optional): Corresponding device of the cell. Defaults to None.
        """

        self._name = name
        self._layer_stack = layer_stack #layer-stack of the cell
        self._add_bounding_layer() #add a bounding layer to the layer stack
        
        self._device = device
        
        #store the path of the .mag file
        self._path = None

        #track if the cell is already placed
        self._placed = False

        #track the center-point of the cell
        self._center_point = (0,0)

        #track the rotation of the cell
        self._rotation = 0

        #track if the cell gets placed
        self._in_placement = False

        #Store the terminals of the cell
        self._terminals : dict[str, MagicTerminal]
        self._terminals = {}

        #Store the placement rules of the cell
        self._placement_rules = None

        #if a device were specified
        #add physical terminals to the cell
        if self._device:
            self.add_terminals()
        
        #setup features of the cell
        self._features = {
            "Bounding" : None,
            "Area" : None,
            "Placed" : None,
            "In_placement" : None,
            "Rotation" : None,
            "Center_Point" : None,
        }

        #reset the cell
        self.reset_place()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name}, device={self.device})"

    def add_path(self, path : str):
        """Set the path to the .mag file of the cell.

        Args:
            path (str): Path of the .mag file.
        """
        self._path = path

    def set_name(self, name : str):
        """Set the name of the cell.

        Args:
            name (str): Name of the cell.
        """
        self._name = name
    
    def set_device(self, device : Device):
        """Set the device of the cell.

        Args:
            device (Device): Device of the cell.
        """
        self._device = device

    def set_placement_rules(self, rules : PlacementRules):
        """Set the placement rules of the cell.

        Args:
            rules (PlacementRules): Placement rules of the cell.
        """
        self._placement_rules = rules
    
    @property
    def center_point(self) -> tuple[float|int, float|int]:
        """Get the center-point of the cell.

            ```
                    ----------------
                    |       |       |
                    |-----(x,y)-----|
                    |       |       |
                    ----------------
            ```
        Returns:
            tuple[float|int, float|int]: (x,y)
        """

        #get the bounding box of the cell
        bounding = self.get_bounding_box()
        
        #calculate the mean-coordinates
        mean_x = round((bounding[2]+bounding[0])/2, 2) #center-point x
        mean_y = round((bounding[3]+bounding[1])/2, 2) #center-point y

        #set the center-point of the cell
        self._center_point = (mean_x, mean_y)
        #return the center-point
        return self._center_point
    
    @property
    def rotation(self) -> int:
        """Rotation of the cell.

        Returns:
            int: Rotation of the cell (between 0-359 deg).
        """
        return self._rotation%360
    
    @property
    def path(self) -> str:
        """Path to the .mag file of the cell.

        Returns:
            str: Path to the .mag file.
        """
        return self._path
    
    @property
    def in_placement(self) -> bool:
        """Check if the cell is in placement.

        Returns:
            bool : True if cell gets placed next.
        """
        return self._in_placement

    @property
    def placed(self) -> bool:
        """ Check if the cell is already placed.

        Returns:
            bool : True if placed, else false 
        """
        return self._placed
    
    @property
    def area(self) -> float:
        """Get the area of the cell.

        Returns:
            float: Area of the cell.
        """
        #get the bounding of the cell
        bound = self.get_bounding_box()
        #calc height and width of the cell
        h = abs(bound[3]-bound[1])
        w = abs(bound[2]-bound[0])
        #return the area
        return h*w

    @property
    def height(self) -> float:
        """Get the height of the cell.
            The height is the length of the W and E edge of the 
            cells bounding box.
        Returns:
            float: Height of the cell.
        """
        bound = self.get_bounding_box()
        return abs(bound[3]-bound[1])
    
    @property
    def width(self) -> float:
        """Get the width of the cell.
            The width is the length of the S and N edge of the 
            cells bounding box.
        Returns:
            float: Width of the cell.
        """
        bound = self.get_bounding_box()
        return abs(bound[2]-bound[0])
    
    @property
    def features(self) -> dict[str,]:
        """Get the features of the cell.

        Returns:
            dict[str,]: Features of the cell. key: Name of the feature, value: Value of the feature
        """
        self._features["Bounding"] = self.get_bounding_box()
        self._features["Area"] = self.area
        self._features["Placed"] = int(self._placed)
        self._features["In_placement"] = int(self._in_placement)
        self._features["Rotation"] = self.rotation
        self._features["Center_Point"] = self.center_point

        return self._features
    
    @property
    def feature_list(self) -> list[float]:
        """Get a list of all feature values.

        Returns:
            list[float]: Feature values of the cell.
        """
        l = []
        for v in list(self.features.values()):
            if type(v) is list:
                l.extend(v)
            elif type(v) is tuple:
                l.extend(v)
            else:
                l.append(float(v))
        return l
    
    @property
    def device(self) -> Device:
        """Get the device of the cell.

        Returns:
            Device: Corresponding device of the cell.
        """
        return self._device
    
    @property
    def terminals(self) -> dict[str, MagicTerminal]:
        """Get the terminals of the cell.

        Returns:
            dict: key: Terminal name. value: Terminal
        """
        return self._terminals

    @property
    def placement_rules(self) -> PlacementRules:
        """Get the placement rules of the cell.

        Returns:
            PlacementRules: Placement rules of the cell.
        """
        return self._placement_rules
    
    def terminals_connected_to_net(self, net : Net) -> list[MagicTerminal]:
        """Get all terminals connected to the net <net>.

        Args:
            net (Net): Net to be evaluated.

        Returns:
            list[magicTerminal]: List of all magic-terminals connected to the net.
        """
        assert isinstance(self._device, PrimitiveDevice)
        
        #get the terminal-names which are connected to the net
        terminal_names = self._device.map_nets_to_terminal_names(net)
        
        #setup a list for the MagicTerminals, and add them to the list
        terminals = []
        for n in terminal_names:
            terminals.append(self._terminals[n])
        
        return terminals

    def add_terminals(self):
        """Add physical terminals to the cell.

        Raises:
            ValueError: If the cell has no device.
            ValueError: If the cells device, has no implemented method to retrieve the cells terminals.
        """
        if self._device:
            try:
                #get the name of the devices class
                suffix = self._device.__class__.__name__
                #set the name of the generator method
                func = "get_terminals_"+suffix
                self._terminals = globals()[func](self) #call the generator method for the terminals

                #register the cell-terminals at the devices terminal
                for (k, v)  in self._terminals.items():
                    self._device.terminals[k].set_magic_terminal(v)

            except:
                raise ValueError(f"Terminals for device {self.device.name} not implemented!")
        else:
            raise ValueError("Cell must have a device to add terminals!")

    def place(self, center_coord : tuple[int|float,int|float], rotation = 0):
        """Place the cell at the center coordinate with the given rotation.

        Args:
            center_coord (tuple): (x,y) - coordinate where the cell has to be placed.
            rotation (int): Resulting rotation of the cell, multiple of 90deg. 
        """
        #check if the cell has to be rotated
        if not rotation==self.rotation:
            #if rotate the cell around its center-point
            dphi = (rotation-self.rotation)
            self.rotate_center(dphi)
        
        #move the cell to the given coordinate
        self.move_center(center_coord)
        self._placed = True
        self._in_placement = False        
    
    def place_next(self):
        """Set the `in_placement` attribute, to signal
            that the cell gets placed as next.
        """
        self._in_placement = True

    def reset_place(self):
        """Reset the placement.
            - Rotate the cell, such that the initial rotation gets restored.
            - Move the cell, to the (0,0) coordinate.
            - Reset placement attributes.
        """
        if not self.rotation == 0:
            self.rotate_center(-self.rotation)

        self.move_center((0,0))
        self._placed = False
        self._in_placement = False
    
    def get_overlapping_rectangles(self, layer1 : str, layer2 : str) -> list[Rectangle]:
        """Get the rectangles of layer1 which overlap with rectangles of layer2.

        Args:
            layer1 (str): Name of layer1
            layer2 (str): Name of layer2

        Raises:
            ValueError: If layer1 not in layer-stack.
            ValueError: If layer2 not in layer-stack.

        Returns:
            list[Rectangle]: Overlapping rectangles of layer1.
        """
        try:
            l1 = self._layer_stack[layer1]
        except:
            raise ValueError(f"Layer {layer1} not in layer-stack of cell {self._name}.")
        
        try:
            l2 = self._layer_stack[layer2]
        except:
            raise ValueError(f"Layer {layer2} not in layer-stack of cell {self._name}.")
        
        return MagicLayer.get_overlaps(l1, l2)

    def get_placement_bounding_box(self, other_cell : Cell = None) -> tuple[float|int, float|int, float|int, float|int]:
        """Get the bounding box of the cell, such that all placement rules are satisfied.

        Args:
            other_cell (Cell, optional): Other cell. If specified, a bounding box will be generated, which
                                            satisfies the placement rules between both cells. Defaults to None.

        Returns:
            tuple[float|int, float|int, float|int, float|int]: (x_min, y_min, x_max, y_max)
        """
        if self._placement_rules and other_cell.placement_rules:
            #if both have a placement-rule
            #generate a bounding box, which satisfies the placement rules
            return self._placement_rules.generate_rule(other_cell.placement_rules)
        else:
            #return the bounding box of the cell
            return tuple(self.get_bounding_box())
    
    def _add_bounding_layer(self) -> bool:
        """Add a bounding layer which surrounds the cell.

        Returns:
            bool : True if bound were added.
        """
        #check if there is a layer-stack
        if self._layer_stack:
            
            # iterate over each layer to find
            # the bounding box
            layers = list(self._layer_stack.values())
            bounding = layers[0].get_bounding_box()
            
            for l in layers:
                r_bound = l.get_bounding_box()
                for i in range(2):
                    bounding[i] = min(bounding[i], r_bound[i])

                for i in range(2,4):
                    bounding[i] = max(bounding[i], r_bound[i])   
            
            #setup a rectangle for the boundary and add it to the layer stack
            bounding_rect = Rectangle(bounding[0], bounding[1], bounding[2], bounding[3])
            bounding_layer = MagicLayer("Bounding", Color((255,255,255)))
            bounding_layer.add_rect(bounding_rect)
            bounding_layer.dont_fill()
            
            self._layer_stack["Bounding"] = bounding_layer
            return True
        else:
            return False
    
    def _move_layers_to_bounding(self):
        """Move the layers of the cell,
        such that they match with the moved bounding box.
        """
        layers = []

        #get all layers except the bounding
        for k, v in self._layer_stack.items():
            if not k=="Bounding":
                layers.append(v)

        #get the bounding of the layers
        bounding = layers[0].get_bounding_box()
            
        for l in layers:
            r_bound = l.get_bounding_box()
            for i in range(2):
                bounding[i] = min(bounding[i], r_bound[i])

            for i in range(2,4):
                bounding[i] = max(bounding[i], r_bound[i])   
        
        bounding_rect = Rectangle(bounding[0], bounding[1], bounding[2], bounding[3])
        bounding_layer = MagicLayer("Bounding", Color((255,255,255)))
        bounding_layer.add_rect(bounding_rect)

        bounding_box = bounding_layer.get_bounding_box()

        mean_x = round((bounding_box[0]+bounding_box[2])/2,2)
        mean_y = round((bounding_box[1]+bounding_box[3])/2,2)
                
        #rotate the layers
        for l in layers:
            dphi = (self.rotation - l.rotation)%360
            if not dphi==0:
                l.rotate((mean_x,mean_y), dphi)

        #move the layers to the bounding box
        for l in layers:
            l.move((self.center_point[0]-mean_x, self.center_point[1]-mean_y))

    def draw(self, screen):
        """Draw the cell on a pygame surface.

        Args:
            screen (pygame.Surface): Surface to be drawn.
        """
        #move the internal layer to the bounding boy
        self._move_layers_to_bounding()

        #draw each layer
        for l in list(self._layer_stack.values()):
            l.draw(screen)
    
    def plot(self, ax, text : bool = True, with_terminals = False):
        """Plot the cells boundary and terminals on axis <ax>.

        Args:
            ax (axis): Axis on which the cell shall be plotted.
            text (bool, optional): If True, text will also be plotted. Defaults to True.
            with_terminals (bool, optional): If True, the terminals will also be plotted. Defaults to False.
        """
        bound = self.get_bounding_box()
        rect = Rectangle(*bound)
        rect.plot(ax, color=None)
        
        if text:
            mean = self.center_point
            probs = dict(boxstyle='round', facecolor='k', alpha=0.1)
            ax.text(*mean, self._name, fontsize=14, 
                    verticalalignment='center',
                    horizontalalignment='center',
                    bbox=probs)

        if with_terminals:
            for terminal in self.terminals.values():
                terminal.plot(ax, text=text)

    def _move(self, coordinate : tuple[int|float, int|float]):
        """Move the boundary and physical terminals of the cell,
        by the amount given in coordinate.

        Args:
            coordinate (tuple[int | float, int | float]): (dx, dy) - amount the cell has to be moved.
        """

        #move the bounding layer
        self._layer_stack["Bounding"].move(coordinate)

        #move all physical terminals
        for (name, term) in self._terminals.items():
            assert isinstance(term, MagicTerminal)
            term.move_by(*coordinate)
        

    def _rotate(self, coordinate : tuple[int|float, int|float], angle : int):
        """Rotate the bounding-layer and the terminals clockwise by the angle <angle>, 
        about the coordinate <coordinate>.

        Args:
            coordinate (tuple[int | float, int | float]): Center-coordinate of the rotation.
            angle (int): Rotation angle.
        """

        #rotate the bounding layer
        self._layer_stack["Bounding"].rotate(coordinate, angle)
        self._rotation += angle % 360

        #rotate the terminals
        for (name, term) in self._terminals.items():
            assert isinstance(term, MagicTerminal)
            term.rotate_by(coordinate, -angle)


    def rotate_center(self, angle : int):
        """ Rotate the bounding-layer and the terminals clockwise
        by the angle <angle>, about the center point of the cell.

        Args:
            angle (int): Rotation angle.
        """         
        self._rotate(self.center_point, angle)


    def rotate_ll(self, angle : int):
        """Rotate the bounding-layer and the terminals clockwise by the angle <angle>, about the lower left corner of the cell.

        Args:
            angle (int): Rotation angle.
        """
        bounding = self._layer_stack["Bounding"].get_bounding_box()
        
        mean_x = round(bounding[0],2)
        mean_y = round(bounding[1],2)
        
        left_bottom_coordinate = (mean_x, mean_y)
        
        #rotate the cell around the left-bottom coordinate
        self._rotate(left_bottom_coordinate, angle)

        self._move((0, bounding[3]-bounding[1]))

    def move_center(self, coordinate : tuple[int|float, int|float]):
        """Move the center of the bounding-layer and the terminals to center-point <coordinate>.

        Args:
            coordinate (tuple[int|float, int|float]): New center-coordinate of the cell.
        """
        
        mean_x = self.center_point[0]
        mean_y = self.center_point[1]
        
        move_by = (coordinate[0]-mean_x, coordinate[1]-mean_y)
        
        self._move(move_by)
     
    def get_bounding_box(self) -> list:
        """Get the bounding box of the cell.

            ```
                -------------(x1,y1)  
                |               |     
                |               |     
                |               |
             (x0,y0)------------   
            
            ```
        Returns:
            list: [x0, y0, x1, y1]
        """
        bounding = self._layer_stack["Bounding"].get_bounding_box()
        return bounding
    
    def collidates(self, cell : Cell) -> bool:
        """Check if the cell collidates with an other cell <cell>.
            Cells collidate if they overlap.
        Args:
            cell (Cell): other cell

        Returns:
            bool: True if the cells collidate.
        """
        
        b1 = self.get_bounding_box()
        b2 = cell.get_bounding_box()
        
        width_pos = min(b1[2], b2[2])>max(b1[0], b2[0])
        height_pos = min(b1[3], b2[3])>max(b1[1], b2[1])
        
        return width_pos and height_pos
    
    