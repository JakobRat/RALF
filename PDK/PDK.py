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

import json
from pathlib import Path

from PDK.Layers import Layer, MetalLayer, ViaLayer

class PDK:
    """Class to store a PDK.
        A PDK defines the layers for the routing.
    """
    def __init__(self, pdk_file_path : str | Path) -> None:
        """Setup a PDK.

        Args:
            pdk_file_path (str | Path): Path to the PDK file. (json file)
        """
        #read in the PDK
        self._pdk_file_path = pdk_file_path
        with open(self._pdk_file_path) as json_file:
            self._pdk_definition = json.load(json_file)
        
        #get the scale factor to the internal lambda-scale
        # e.g. if the values in the PDK are given in nm
        # the scale factor has to be 10 
        self._scale_factor = self._pdk_definition["ScaleFactor"]

        #get aliases of the layer names
        self._aliases = self._pdk_definition["aliases"]

        #store the layers
        #store metal layers
        # key: layer name value: Layer
        self._metal_layers = {}
        #store via layers
        # key: layer name value: Layer
        self._via_layers = {}
        #store device layers
        # key: layer name value: Layer
        self._device_layers = {}
        #store all layers
        # key: layer name value: Layer
        self._layers = {}
        #store the layer numbers
        # key: layer name value: layer number
        self._layer_numbers = {}
        self._init_layers()

    @property
    def metal_layers(self) -> dict[str, Layer]:
        """Get the metal layers.

        Returns:
            dict: key -> layer name (str), value -> layer (Layer) 
        """
        return self._metal_layers
    
    @property
    def via_layers(self) -> dict[str, Layer]:
        """Get the via layers.

        Returns:
            dict: key -> layer name (str), value -> layer (Layer) 
        """
        return self._via_layers

    @property
    def device_layers(self) -> dict[str, Layer]:
        """Get the device layers. E.g. nwell, mimcap, ...

        Returns:
            dict: key -> layer name (str), value -> layer (Layer)
        """
        return self._device_layers
    
    @property
    def layers(self) -> dict[str, Layer]:
        """Get all layers of the PDK.

        Returns:
            dict: key -> layer name (str), value -> layer (Layer) 
        """
        return self._layers
    
    def _init_layers(self):
        #init device layers
        for l in self._pdk_definition["device_layers"]:
            minWidth = self._pdk_definition[l]["Width"]/self._scale_factor
            minSpace = self._pdk_definition[l]["Space"]/self._scale_factor 
            self._device_layers[l] = Layer(l, minWidth, minSpace)
        

        layer_number = 0
        #init metal layers
        for l in self._pdk_definition["layer_stack"]:
            minWidth = self._pdk_definition[l]["Width"]/self._scale_factor
            minSpace = self._pdk_definition[l]["Space"]/self._scale_factor
            resistivity = self._pdk_definition[l]["Resistivity"]/self._scale_factor
            minArea = self._pdk_definition[l]["MinArea"]/(self._scale_factor**2)
            
            self._metal_layers[l] = MetalLayer(name=l, minWidth=minWidth, minSpace=minSpace,
                                               minArea=minArea, resistivity=resistivity, pdk=self)
            self._layer_numbers[l] = layer_number
            layer_number += 1

        #init via layers
        for l in self._pdk_definition["via_stack"]:
            minWidth = self._pdk_definition[l]["WidthX"]/self._scale_factor
            minSpace = self._pdk_definition[l]["SpaceX"]/self._scale_factor
            resistivity = self._pdk_definition[l]["Resistivity"]/self._scale_factor
            min_enclosure = self._pdk_definition[l]["min_enclosure"]/self._scale_factor
            bottom_layer = self._metal_layers[self._pdk_definition[l]["Stack"][0]]
            top_layer = self._metal_layers[self._pdk_definition[l]["Stack"][1]]
            self._via_layers[l] = ViaLayer(l, minWidth, minSpace, min_enclosure, min_enclosure, bottom_layer, top_layer, resistivity, self)
            bottom_layer.set_upper_via(self._via_layers[l])
            top_layer.set_lower_via(self._via_layers[l])
            self._layer_numbers[l] = layer_number
            layer_number += 1

        #add the layers to the layers dict
        self._layers.update(self._device_layers)
        self._layers.update(self._metal_layers)
        self._layers.update(self._via_layers)
    
    def _get_name_from_alias(self, layer_alias : str) -> str | None:
        """Get the layer name (as in the PDK) for the alias <layer_alias>.

        Args:
            layer_alias (str): Alias of an layer

        Returns:
            str | None: PDK name of the layer, or None if the alias isn't in the PDK.
        """
        if layer_alias in self.layers:
            return layer_alias
        
        for layer_name, aliases in self._aliases.items():
            if layer_alias in aliases or layer_alias==layer_name:
                return layer_name
        
        return None

    def get_layer(self, layer : str) -> Layer:
        """Get the layer, with name <layer>.

        Args:
            layer (str): Name of the layer.

        Raises:
            ValueError: If the layer isn't in the PDK.

        Returns:
            Layer: Layer with name <layer>.
        """         
        layer = self._get_name_from_alias(layer)
        try:
            return self._layers[layer]
        except:
            raise ValueError(f"Layer {layer} not in PDK!")
    
    def get_layer_number(self, layer : str) -> int:
        """Get the number of the layer, with name <layer>.
            - The layer-number of two neighboring metal-layers differ by 1
            - The layer-number of two neighboring via-layers differ by 1
        Args:
            layer (str): Name of the layer.

        Raises:
            ValueError: If the layer isn't in the PDK.

        Returns:
            int: Layer number.
        """
        layer = self._get_name_from_alias(layer)
        try:
            return self._layer_numbers[layer]
        except:
            raise ValueError(f"Layer {layer} has no number!")
    
    def get_lower_metal_layer(self, layer : str) -> MetalLayer:
        """Get the metal layer one below metal-layer <layer>.

        Args:
            layer (str): Name of the layer.

        Raises:
            ValueError: If layer not in metal-stack.

        Returns:
            MetalLayer: MetalLayer one below <layer>. 
        """
        layer = self._get_name_from_alias(layer)
        metal_stack = self._pdk_definition["layer_stack"]
        try:
            index = metal_stack.index(layer)
        except:
            raise ValueError(f"Layer {layer} not defined in metal stack!")
        
        if index>0:
            return self._metal_layers[metal_stack[index-1]]
        else:
            return None
    
    def get_higher_metal_layer(self, layer : str) -> MetalLayer:
        """Get the metal layer one above metal-layer <layer>.

        Args:
            layer (str): Name of the layer.

        Raises:
            ValueError: If layer not in metal-stack.

        Returns:
            MetalLayer: MetalLayer one above <layer>. 
        """
        layer = self._get_name_from_alias(layer)
        metal_stack = self._pdk_definition["layer_stack"]
        try:
            index = metal_stack.index(layer)
        except:
            raise ValueError(f"Layer {layer} not defined in metal stack!")
        
        if index<(len(metal_stack)-1):
            return self._metal_layers[metal_stack[index+1]]
        else:
            return None
    
    def get_via_layer(self, layer1, layer2) -> ViaLayer | None:
        """Get the via between layer1 and layer2.

        Args:
            layer1 (MetalLayer): Bottom metal layer
            layer2 (MetalLayer): Top metal layer

        Returns:
            ViaLayer or None: ViaLayer between layer1 and layer2
        """
        for (k, v) in self._via_layers.items():
            if (v.bottom_layer == layer1 and v.top_layer == layer2) or (v.bottom_layer == layer2 and v.top_layer == layer1):
                return v
        
        return None

#setup a global pdk    
global_pdk = PDK('PDK/layers.json')