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
    from SchematicCapture.Circuit import Circuit
    from PDK.Layers import Layer
    from lef_def_parser.def_util import Pin, Pins
    from lef_def_parser.def_util import Layer as lef_Layer
    

from lef_def_parser.def_parser import DefParser
from PDK.PDK import global_pdk
from Magic.MagicLayer import Rectangle
from SchematicCapture.Net import Net

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

INTERNAL_SCALE = 10 #nm

class MagicDie:
    """Class to store the die of the circuit.
        - The die specifies the max. boundary of the placement and routing.
        - The die specifies the IO-pins of the circuit.
    """
    def __init__(self, circuit : Circuit, def_file : str = None) -> None:
        """Setup a die.

        Args:
            circuit (Circuit): Circuit of the die.
            def_file (str, optional): Def-file of the die. Defaults to None.
                                        The def-file defines the die-area and IO-pins.
        Raises:
            ValueError: If the Def-file can't be parsed.
        """

        if not (def_file is None):
            try:
                self._def_parser = DefParser(def_file=def_file)
                self._def_parser.parse()

                assert self._def_parser.units == 'MICRONS' f"Unsupported unit {self._def_parser.units} detected!"
                self._def_scale = self._def_parser.scale

            except:
                raise ValueError(f"Parsing of def file {def_file} failed!")
        else:
            self._def_parser = None
            self._def_scale = 1

        self._circuit = circuit
        self._name = self._circuit.name
        self._nets = {}
        self._bounding_box = self._get_bounding_box()
        self._pins = {}
        self._setup_pins_and_nets()        

    def _get_bounding_box(self) -> Rectangle:
        """Get the bounding box of the die.

        Returns:
            tuple[int, int, int, int]: (x_min, y_min, x_max, y_max)
        """

        if not (self._def_parser is None):
            parser_area = self._def_parser.diearea
            parser_scale = (int(self._def_parser.scale)/1000) * INTERNAL_SCALE #convert the scale to nm and multiply with the internal scale

            return Rectangle(parser_area[0][0]/parser_scale, parser_area[0][1]/parser_scale, parser_area[1][0]/parser_scale, parser_area[1][1]/parser_scale)
        else:
            return None
        
    def _setup_pins_and_nets(self):
        """Setup the io-pins and the io-nets.

        Raises:
            ValueError: If a io-pin has a not supported layer.
        """
        if not (self._def_parser is None):
            
            #iterate over the io-pins
            pin : Pin
            for pin in self._def_parser.pins:
                parser_scale = int(self._def_parser.scale)/1000 * INTERNAL_SCALE
                layer : lef_Layer
                layer = pin.layer
                layer_name = layer.name
                layer_points = layer.points #((x_min, y_min), (x_max, y_max))
                #convert the coordinates to the internal scale
                layer_points = (layer_points[0][0]/parser_scale, layer_points[0][1]/parser_scale, layer_points[1][0]/parser_scale, layer_points[1][1]/parser_scale)
                
                pin_placed_at = pin.placed #center-point of the pin
                #convert the coordinates to the internal scale
                pin_placed_at = (pin_placed_at[0]/parser_scale, pin_placed_at[1]/parser_scale)
                #generate a rectangle for the pin
                pin_rectangle = Rectangle(layer_points[0]+pin_placed_at[0], layer_points[1]+pin_placed_at[1], 
                                        layer_points[2]+pin_placed_at[0], layer_points[3]+pin_placed_at[1])
                
                #get the net-name of the pin
                net = pin.net

                #try to get the internal net of the pin
                try:
                    circuit_net = self._circuit._nets[net]
                except:
                    print(f"Net {net} couldn't be found in the circuit! Probably unconnected net. Adding new net to die.")
                    circuit_net = Net(net, self._circuit)

                #try to get the PDK layer of the pin
                try:
                    pdk_layer = global_pdk.get_layer(layer_name)
                except:
                    raise ValueError(f"Layer {layer_name} couldn't be found in the PDK!")
                
                #if the pin is connected to a internal net
                if circuit_net:
                    #generate a physical DiePin and add the pin to the net
                    self._nets[net] = circuit_net

                    #init a new pin
                    die_pin = MagicDiePin(*pin_placed_at, layer=pdk_layer, net=circuit_net, bounding_box=pin_rectangle)
                    circuit_net.add_die_pin(die_pin) #add the pin to the net
                    
                    if circuit_net in self._pins:
                        self._pins[circuit_net].add(die_pin)
                    else:
                        self._pins[circuit_net] = set([die_pin])
            
            
    @property
    def bounding_box(self) -> Rectangle:
        """Get the bounding box of the die.

        Returns:
            Rectangle: Rectangle defining the bounding box of the chip.
        """
        return self._bounding_box
    
    @property
    def pins(self) -> dict[Net, set[MagicDiePin]]:
        """Get the pins of the die

        Returns:
            dict[Net, set[MagicDiePin]]: key: Net of the pin, value: set of die pins connected to the net.
        """
        return self._pins
    
    @property
    def name(self) -> str:
        """Get the name of the die.

        Returns:
            str: Name of the die.
        """
        return self._name
    
    @property
    def circuit(self) -> Circuit:
        """Get the circuit of the die.

        Returns:
            Circuit: Circuit of the die.
        """
        return self._circuit
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, circuit={self._circuit})"

    def plot(self, ax):
        """
            Plot the die and io-pins.
        """
        coordinates = self.bounding_box.get_coordinates()
        patch = patches.Rectangle((coordinates[0], coordinates[1]), 
                                  self.bounding_box.width, 
                                  self.bounding_box.height,
                                  edgecolor='k',
                                  facecolor=None,
                                  alpha=1.0,
                                  fill=False,)
        ax.add_patch(patch)

        for net, pins in self.pins.items():
            for pin in pins:
                pin.plot(ax)
        

class MagicDiePin:
    """Class to store a IO-pin.
    """
    def __init__(self, x : float|int, y : float|int, layer : Layer, net : Net, bounding_box : Rectangle = None) -> None:
        self._layer = layer
        self._net = net
        self._x = x
        self._y = y
        self._bounding_box = bounding_box

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(c={self.coordinate}, layer={self.layer}, net={self.net})"
    
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
    def coordinate(self) -> tuple:
        """Coordinate of the pin.

        Returns:
            tuple: (x,y)
        """
        return (self._x, self._y)
        
    @property
    def bounding_box(self) -> Rectangle:
        return self._bounding_box

    def get_bounding_box_on_grid(self) -> Rectangle:
        """Get the boundary - rectangle of the pin, which lies on the grid.

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
        """Get the coordinate of the pin which lies on the grid internal grid.

        Returns:
            tuple[int, int]: (x,y)
        """
        coordinate = self.coordinate
        x = round(coordinate[0]/2.)*2
        y = round(coordinate[1]/2.)*2
        
        return (x,y)
    
    def __eq__(self, __value: object) -> bool:
        return (isinstance(__value, MagicDiePin) and 
                (self._x == __value._x) and 
                (self._y == __value._y) and 
                (self._layer == __value.layer) and 
                (self._net == __value._net))

    def __hash__(self) -> int:
        return hash((self._x, self._y, hash(self._layer), hash(self._net)))
    

    def plot(self, ax, color = 'gray'):
        """Plot the die pin.

        Args:
            ax (axis): Axis to plot on.
            color (str, optional): Color of the pin. Defaults to 'gray'.
        """
        coordinates = self.bounding_box.get_coordinates()
        patch = patches.Rectangle((coordinates[0], coordinates[1]), 
                                  self.bounding_box.width, 
                                  self.bounding_box.height,
                                  edgecolor="#000000",
                                  facecolor=color,
                                  alpha=1.0,
                                  fill=True,)
        ax.add_patch(patch)
        ax.text(x=self.coordinate[0], y=self.coordinate[1], s=self.net.name, fontsize=9, color='k')
