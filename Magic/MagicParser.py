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

from Magic.MagicLayer import MagicLayer, Rectangle, Color
import numpy as np

#define layers which shall be skipped by the parser
SKIPPED_LAYERS = ["checkpaint", "properties"]

class MagicParser:
    """Class to parse a .mag file.
    """
    def __init__(self, magic_file : str):
        """Parse a .mag file.

        Args:
            magic_file (str): Name of the file.

        Raises:
            ValueError: If the file-ending isn't .mag.
            ValueError: If the file can't be read
        """
        
        if not magic_file.endswith(".mag"):
            raise ValueError("Only .mag files are supported!")
            
        self._src = magic_file
        
        try:
            with open(str(self._src),'r') as f:
                lines = f.readlines()
        except:
            raise ValueError
        
        #set the scaling as 1
        self._magscale = 1

        #get all layers
        self._layers = self.get_layers(lines)
            
    
    @property
    def layers(self) -> dict[str, MagicLayer]:
        """Get the parsed layers, and rectangles on them

            The coordinates of the rectangles are given 
            in lambda units, which are 10nm.
             
        Returns:
            dict[str, MagicLayer]: key: Name of the layer, value: MagicLayer
        """
        return self._layers
    
    def get_layers(self, lines : list[str]) -> dict[str, MagicLayer]:
        """Get the layers and rectangles defined in lines <lines>.

        Args:
            lines (list[str]): Lines of a .mag file.

        Returns:
            dict[str, MagicLayer]: key: Name of the layer (as in the .mag file). value: MagicLayer
        """
        layers = {}
        
        n = 0
        #iterate over the lines
        while n<len(lines):
            l = lines[n]

            #check if the file uses another scale 
            if l.startswith("magscale"):
                splitted = l.split()
                self._magscale = int(splitted[2])

            #if a new layer were defined
            if MagicParser.get_layer(l): 
                #set a random color for this layer
                color = Color((np.random.randint(0, 255),np.random.randint(0, 255), np.random.randint(0, 255)))
                
                #generate a MagicLayer for this layer
                layer = MagicLayer(MagicParser.get_layer(l), color)
                n += 1
                #get the defined rectangles on this layer
                rect = self.get_rect(lines[n])
                while rect:
                    layer.add_rect(rect)
                    n+=1
                    rect = self.get_rect(lines[n])
                
                n -= 1
                layers[layer.name] = layer
            n += 1
        return layers
            
            
    @staticmethod
    def get_layer(line : str) -> str | bool | None:
        """Get the name of the layer, defined in line <line>.
            To get a name, the line must have the structure
                << layer_name >>.
        Args:
            line (str): Line in .mag file.

        Returns:
            str|bool|None: The name of the layer, False|None if no layer was found.
        """
        if line.startswith("<< end >>"):
            return False
        elif line.startswith("<<"):
            layer = line[3:-4]
            if layer not in SKIPPED_LAYERS:
                return layer
            else:
                return False
        else:
            return None
    
    def get_rect(self, line : str) -> Rectangle|None:
        """Get a rectangle from a .mag file line.
            The line must have the following structure:
            
            rect x_min y_min x_max y_max.

            ------------(x_max, y_max)
            |                   |
            |                   |
            |                   |
        (x_min, y_min)----------


        Args:
            line (str): .mag file line

        Returns:
            Rectangle|None: Rectangle if the line starts with 'rect', else None.
        """
        if line.startswith("rect"):
            l = line.split()
            return Rectangle(int(l[1])/self._magscale,
                            int(l[2])/self._magscale, 
                            int(l[3])/self._magscale,
                            int(l[4])/self._magscale)
        else:
            return None
        
        

