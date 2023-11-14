from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PDK.Layers import Layer
    from SchematicCapture.Net import Net
    from Magic.Cell import Cell

import numpy as np
import math 
from Magic.MagicLayer import Rectangle

class MagicPin:
    """Class to store a physical pin of a device.
    """
    def __init__(self, x : float|int, y : float|int, rotation : int, layer : Layer, net : Net, cell : Cell, magic_terminal : MagicTerminal, bounding_box : Rectangle = None) -> None:
        """Setup a physical pin.

        Args:
            x (float | int): x-coordinate
            y (float | int): y-coordinate
            rotation (int): Rotation of the pin.
            layer (Layer): Layer of the pin.
            net (Net): Net connected to the pin.
            cell (Cell): Cell to which the pin belongs.
            magic_terminal (MagicTerminal): Terminal to which the pin belongs.
            bounding_box (Rectangle, optional): Area of the pin. Defaults to None.
        """
        self._layer = layer
        self._net = net
        self._cell = cell
        self._x = x
        self._y = y
        self._rotation = rotation
        self._bounding_box = bounding_box
        self._magic_terminal = magic_terminal
        
        #if a terminal were specified, register the pin at the terminal.
        if not (magic_terminal is None):
            self._magic_terminal.add_pin(self) #add the pin to the terminal

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(c={self.coordinate}, layer={self.layer}, terminal={self.magic_terminal})"
    
    @property
    def layer(self) -> Layer:
        """Get the layer of the pin.

        Returns:
            Layer: Layer of the pin.
        """
        return self._layer
    
    @property
    def net(self) -> Net:
        """Get the net of the pin.

        Returns:
            Net: Net of the pin.
        """
        return self._net
    
    @property
    def cell(self) -> Cell:
        """Get the cell of the pin.

        Returns:
            Cell: Cell of the pin.
        """
        return self._cell
    
    @property
    def coordinate(self) -> tuple[float|int, float|int]:
        """Coordinate of the pin.

        Returns:
            tuple: (x,y)
        """
        return (self._x, self._y)
    
    @property
    def rotation(self) -> int:
        """Rotation of the pin in deg.

        Returns:
            int: Rotation between 0-359
        """
        return self._rotation%360
    
    @property
    def bounding_box(self) -> Rectangle:
        """Get the bounding box of the pin.

        Returns:
            Rectangle: Bounding box of the pin.
        """
        return self._bounding_box

    def get_bounding_box_on_grid(self) -> Rectangle:
        """Get the boundary - rectangle of the pin, which lies on the grid,
            and the coordinates are divisible by 2.

        Returns:
            Rectangle: Boundary rectangle.
        """
        bound = self.bounding_box.bounding_box
        x_min = math.floor(bound[0]/2.)*2
        y_min = math.floor(bound[1]/2.)*2
        x_max = math.ceil(bound[2]/2.)*2
        y_max = math.ceil(bound[3]/2.)*2

        return Rectangle(x_min, y_min, x_max, y_max)
    
    def get_coordinate_on_grid(self) -> tuple[int, int]:
        """Get the coordinate of the pin which lies on the grid, 
        and is divisible by 2.

        Returns:
            tuple[int, int]: (x,y)
        """
        coordinate = self.coordinate
        x = round(coordinate[0]/2.)*2
        y = round(coordinate[1]/2.)*2
        
        return (x,y)

    @property
    def magic_terminal(self) -> MagicTerminal:
        """Get the terminal of the pin.

        Returns:
            MagicTerminal: Terminal of the pin.
        """
        return self._magic_terminal
    
    def __eq__(self, __value: object) -> bool:
        return (isinstance(__value, MagicPin) and 
                (self._x == __value._x) and 
                (self._y == __value._y) and 
                (self._layer == __value.layer) and 
                (self.net == __value.net))

    def __hash__(self) -> int:
        return hash((self._x, self._y, hash(self._layer), hash(self.net)))
    
    def move_by(self, dx : float, dy : float):
        """Move the pin by the amount specified by dx and dy.

        Args:
            dx (float): x-amount the pin gets shifted.
            dy (float): y-amount the pin gets shifted.
        """
        self._x += dx
        self._y += dy
        if self._bounding_box:
            self._bounding_box.move((dx,dy))
    
    def move_to(self, x : float, y : float):
        """Move the pin to the coordinate (x,y)

        Args:
            x (float): New x-coordinate.
            y (float): New y-coordinate.
        """
        if self._bounding_box:
            dx = x - self._x
            dy = y - self._y
            self._bounding_box.move((dx,dy))
        
        self._x = x
        self._y = y

    def rotate_by(self, coordinate : tuple[float, float], angle : int):
        """Rotate the pin, counter-clockwise, around the coordinate <coordinate>,
        by the amount of angle.

        Args:
            angle (int): Rotation angle, multiple of 90degree.
            coordinate (tuple): (x,y) coordinate of the rotation-point.

        Raises:
            ValueError: If angle is not a multiple of 90degree.
        """
        if angle%90 == 0:
            
            self._rotation += angle

            #rotate the bounding box of the pin.
            if self._bounding_box:
                self._bounding_box.rotate(coordinate, angle)
            
            #rotate the x,y coordinate of the pin.
            mean = np.array(coordinate)
            c = np.array([self._x, self._y])
            
            angle = angle * np.pi/180
            rot_mat = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
            
            v = c-mean
            
            v = np.round(rot_mat.dot(v),2)
            
            c_new = v + mean

            self._x = c_new[0]
            self._y = c_new[1]


        else:
            raise ValueError("Only angles multiple of 90deg are supported!")

    def plot(self, ax, color=None, text=True):
        """Plot the pin on axis <ax>.

        Args:
            ax (axis): Axis on which the pin shall be plotted.
            color (str, optional): Color of the pin. Defaults to None.
            text (bool, optional): If True, the name of the pins terminal will be plotted. Defaults to True.
        """
        self.bounding_box.plot(ax, color=color, hatch = '//')
        if text:
            ax.plot(*self.coordinate, 'x', color='k')
            ax.text(*self.coordinate, self.magic_terminal.name, 
                    horizontalalignment='center',
                    verticalalignment='bottom',
                    )

class MagicTerminal:
    """Class to store a physical terminal of a device.
        - A MagicTerminal is a set of MagicPin(s) which originate from the same cell, and are connected to the same net.
        - E.g. The gate-terminal of a MOS with 5-fingers contains 5 MagicPin(s)
    """
    def __init__(self, name : str, parent_cell : Cell, net : Net) -> None:
        """Setup a MagicTerminal.

        Args:
            name (str): Name of the terminal.
            parent_cell (Cell): Name of the cell, the terminal belongs.
            net (Net): Name of the net, the terminal is connected with.
        """
        self._name = name
        self._parent_cell = parent_cell
        self._net = net
        self._pins : list[MagicPin]
        self._pins = []

    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, cell={self.parent_cell}, net={self.net})"
    
    @property
    def name(self) -> str:
        """Name of the terminal.

        Returns:
            str: Name of the terminal.
        """
        return self._name
    
    @property
    def parent_cell(self) -> Cell:
        """Get the cell of the terminal.

        Returns:
            Cell: Cell from which the terminal originates.
        """
        return self._parent_cell
    
    @property
    def net(self) -> Net:
        """Get the net connected to the terminal.

        Returns:
            Net: Net connected to the terminal.
        """
        return self._net

    @property
    def pins(self) -> list[MagicPin]:
        """Get the pins of the terminal.

        Returns:
            list[Pins]: List of pins connected to the terminal.
        """
        return self._pins
    
    @property
    def bounding_box(self) -> tuple:
        """Get the bounding box of the terminal, defined by it's pins.

            ```
                                     (max_x, max_y)
                    ----------------x
                    | x         x   |
                    |       x       |
                    |   x       x   |
                    x---------------
              (min_x, min_y)

              x ... Pins
            ```

        Returns:
            tuple: (min_x, min_y, max_x, max_y)
        """
        c0 = self._pins[0].coordinate
        min_x = c0[0]
        min_y = c0[1]
        max_x = c0[0]
        max_y = c0[1]

        for i in range(1, len(self._pins)):
            c = self._pins[i].coordinate

            min_x = min(min_x, c[0])
            min_y = min(min_y, c[1])

            max_x = max(max_x, c[0])
            max_y = max(max_y, c[1])
        
        return (min_x, min_y, max_x, max_y)

    def add_pin(self, pin : MagicPin):
        """Add a pin to the terminal.

        Args:
            pin (MagicPin): Pin which shall be added.
        """
        self._pins.append(pin)

    def move_by(self, dx : float, dy : float):
        """Move the terminal by the amount of dx and dy.

        Args:
            dx (float): x-amount the terminal gets shifted.
            dy (float): y-amount the terminal gets shifted.
        """
        pin : MagicPin
        for pin in self._pins:
            pin.move_by(dx,dy)
    
    def rotate_by(self, coordinate : tuple[float|int, float|int], angle : int):
        """Rotate the terminal counter-clockwise by the amount of angle around the coordinate <coordinate>.

        Args:
            coordinate (tuple): Center-point (x,y) of the rotation. 
            angle (int): Rotation-angle multiple of 90deg.
        """
        try:
            for pin in self._pins:
                pin.rotate_by(coordinate, angle)
        except:
            ValueError("Rotation angle must be multiple of 90deg!")
    
    def plot(self, ax, color=None, text=True):
        """Plot the terminal on axis <ax>.

        Args:
            ax (axis): Axis on which the terminal shall be plotted.
            color (str, optional): Color of the terminal. Defaults to None.
            text (bool, optional): If True, the name of the terminal will be plotted. Defaults to True.
        """
        for pin in self.pins:
            pin.plot(ax, color, text)