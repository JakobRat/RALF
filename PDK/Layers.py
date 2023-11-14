
from __future__ import annotations

from abc import ABCMeta, abstractmethod
import math
import json
from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from PDK.PDK import PDK

class Layer:
    """Class to store a layer of the PDK.
    """
    def __init__(self, name : str, minWidth : float, minSpace : float, resistivity : float = 0.0, pdk : PDK = None) -> None:
        """Setup a PDK layer.

        Args:
            name (str): Name of the layer.
            minWidth (float): Minimum width of the layer.
            minSpace (float): Minimum space of the layer.
            resistivity (float, optional): Resistivity of the layer, in Ohm/sq. Defaults to 0.0.
            pdk (PDK, optional): PDK of the layer. Defaults to None.
        """
        self._name = name
        self._minWidth = minWidth
        self._minSpace = minSpace
        self._resistivity = resistivity
        self._pdk = pdk
        #default: set the width of the layer as the minimum width
        self._width = minWidth

    @property
    def name(self) ->str:
        """Get the name of the layer.

        Returns:
            str: Name of the layer.
        """
        return self._name
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name})"

    def __str__(self) -> str:
        return self._name
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Layer) and not isinstance(__value, str):
            return NotImplemented
        
        if isinstance(__value, str):
            return self._name == __value
        else:
            return self._name == __value._name

    def __hash__(self) -> int:
        return self.pdk.get_layer_number(self._name)
    
    def __le__(self, obj: object):
        if not isinstance(obj, Layer):
            return NotImplemented
        
        return hash(self)<hash(obj)
    
    def __gt__(self, obj: object):
        if not isinstance(obj, Layer):
            return NotImplemented
        return hash(self)>hash(obj)
    
    @property
    def minWidth(self) -> float:
        """
        Returns:
            float: Minimum width of the layer.
        """
        return self._minWidth
    
    @property
    def minSpace(self) -> float:
        """Get the minimum space of the layer.

        Returns:
            float: Minimum space of the layer.
        """
        return self._minSpace

    @property
    def resistivity(self) -> float:
        """
        Returns:
            float: Resistivity of the layer in Ohm/sq.
        """
        return self._resistivity
    
    @property
    def pdk(self) -> PDK:
        """Get the PDK of the layer.

        Returns:
            PDK: PDK of the layer.
        """
        return self._pdk
    
    @property
    def width(self) -> float:
        """
        Returns:
            float: Width of the layer.
        """
        return self._width

    def set_width(self, new_width : float):
        """Set a new width for the layer.

        Args:
            new_width (float): New width of the layer.
        """
        self._width = new_width

class MetalLayer(Layer):
    """Class to store a metal-layer. 
        E.g. m1, m2, ...
    """
    def __init__(self, name: str, minWidth : float, minSpace : float, minArea : float = 0, resistivity : float = 0.0, pdk : PDK = None) -> None:
        """Setup a metal-layer.
                    
                    -------------           -------------
                    |           |           |           |
                    |           |           |           |
                    |           |           |           |
                    |     1     |           |           |
                    |<--------->|           |           |
                    |           |           |     3     |
                    |           |           |           |
                    |           |     2     |           |
                    |           |<--------->|           |   
                    |           |           |           |
                    ------------            ------------
                1 ... minWidth
                2 ... minSpace
                3 ... minArea
        Args:
            name (str): Name of the layer.
            minWidth (float): Minimum width of the layer.
            minSpace (float): Minimum space of the layer.
            minArea (float, optional): Minimum are of the layer. Defaults to 0.
            resistivity (float, optional): Resistivity of the layer. Defaults to 0.0.
            pdk (PDK, optional): PDK of the layer. Defaults to None.
        """
        self._minArea = minArea
        super().__init__(name, minWidth, minSpace,resistivity, pdk)
        #store the upper and lower via layer
        self._lower_via = None
        self._upper_via = None
    
    @property
    def lower_via_layer(self) -> ViaLayer | None:
        """Get the lower-via layer of the layer.

        Returns:
            ViaLayer | None: ViaLayer if there is one, else None.
        """
        return self._lower_via
    
    @property
    def upper_via_layer(self) -> ViaLayer | None:
        """Get the upper-via layer of the layer.

        Returns:
            ViaLayer | None: ViaLayer if there is one, else None.
        """
        return self._upper_via
    
    @property
    def lower_layer(self) -> MetalLayer | None:
        """Get the lower-metal layer of the layer.

        Returns:
            ViaLayer | None: MetalLayer if there is one, else None.
        """
        if self.lower_via_layer:
            return self.lower_via_layer.bottom_layer
        else:
            return None
        
    @property
    def upper_layer(self) -> MetalLayer | None:
        """Get the upper-metal layer of the layer.

        Returns:
            ViaLayer | None: MetalLayer if there is one, else None.
        """
        if self.upper_via_layer:
            return self.upper_via_layer.top_layer
        else:
            return None
    
    @property
    def minArea(self) -> float:
        """Get the minimum Area of the layer.

        Returns:
            float: Minimum area
        """
        return self._minArea
    
    def get_via(self, layer2 : MetalLayer) -> ViaLayer | None:
        """Get the via-layer between self and layer2.

        Args:
            layer2 (MetalLayer): Second (neighboring) metal-layer.

        Returns:
            ViaLayer | None: ViaLayer if there is a layer between the metal-layers, else None.
        """
        return self.pdk.get_via_layer(self, layer2)

    def set_lower_via(self, via : ViaLayer):
        """Set the lower-via-layer of the metal layer.

        Args:
            via (ViaLayer): Lower via layer.
        """
        assert type(via)==ViaLayer
        self._lower_via = via
    
    def set_upper_via(self, via : ViaLayer):
        """Set the upper-via-layer of the metal layer.

        Args:
            via (ViaLayer): Upper via layer.
        """
        assert type(via)==ViaLayer
        self._upper_via = via
        
class ViaLayer(Layer):
    """Class to store a via-layer.
        E.g. via1, via2, ...
    """
    def __init__(self, name: str, minWidth : float, minSpace : float, minEnclosure_bottom : float,
                 minEnclosure_top : float,
                 bottom_metal : MetalLayer, top_metal : MetalLayer, resistivity : float = 0.0, pdk : PDK = None) -> None:
        """Setup a via-layer.
            ```
                    -------------------------
                    |                    2  |
                    |     -------------<--->|
                    |     |           |     |
                    |     |<--------->|     |
                    |     |    1      |     |
                    |     |           |     |
                    |      ------------     |
                    |                       |
               ---  -------------------------
                |
                | 3
                |
               ---   -------------------------
                    |                    2  |
                    |     -------------<--->|
                    |     |           |     |
                    |     |<--------->|     |
                    |     |    1      |     |
                    |     |           |     |
                    |      ------------     |
                    |                       |
                    -------------------------
                1 ... minWidth
                2 ... minEnclosure
                3 ... minSpace
            ```

        Args:
            name (str): Name of the layer.
            minWidth (float): Minimum width of the layer.
            minSpace (float): Minimum space of the layer.
            minEnclosure_bottom (float): Minimum enclosure from the bottom layer.
            minEnclosure_top (float): Minimum enclosure from the top layer.
            bottom_metal (MetalLayer): Metal layer at the bottom.
            top_metal (MetalLayer): Metal layer at the top.
            resistivity (float, optional): Resistivity of the layer in Ohm/sq. Defaults to 0.0.
            pdk (PDK, optional): PDK of the layer. Defaults to None.
        """
        super().__init__(name, minWidth, minSpace, resistivity, pdk)
        self._minEnclosure_bottom = minEnclosure_bottom
        self._minEnclosure_top = minEnclosure_top
        self._bottom_metal = bottom_metal
        self._top_metal = top_metal 

    @property
    def bottom_layer(self) -> MetalLayer:
        """
        Returns:
            MetalLayer: Bottom layer of the via.
        """
        return self._bottom_metal
    
    @property
    def top_layer(self) -> MetalLayer:
        """
        Returns:
            MetalLayer: Top layer of the via.
        """
        return self._top_metal

    @property
    def minEnclosure_bottom(self) -> float:
        """Get the minimum enclosure of the bottom layer.

        Returns:
            float: Minimum enclosure of the bottom layer.
        """
        return self._minEnclosure_bottom
    
    @property
    def minEnclosure_top(self) -> float:
        """Get the minimum enclosure of the top layer.

        Returns:
            float: Minimum enclosure of the top layer.
        """
        return self._minEnclosure_top