from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Magic.Cell import Cell
    from PDK.Layers import Layer

import abc
from Rules.Rule import Rule

class RoutingRule(Rule, metaclass = abc.ABCMeta):
    """
        A RoutingRule gets applied on a specific cell. E.g. define a obstacle from a cell.
    """ 
    def __init__(self, *, cell: Cell, name: str) -> None:
        super().__init__(name=name)
        self._cell = cell

    @property
    def cell(self):
        return self._cell
    
class AreaRule(RoutingRule, metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, *, cell: Cell, name: str) -> None:
        super().__init__(cell=cell, name=name)
            
    @abc.abstractmethod
    def get_area(self) -> tuple:
        """Get the area where routing is forbidden.

        Raises:
            NotImplementedError: If not implemented.

        Returns:
            tuple: tuple (x_min, y_min, x_max, y_max) defining the forbidden area.
        """
        raise NotImplementedError

class LayerRule(AreaRule, metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, *, cell: Cell, name: str, layer : Layer) -> None:
        super().__init__(cell=cell, name=name)
        self._layer = layer

    @property
    def layer(self) -> Layer:
        """Get the layer where routing is forbidden.

        Returns:
            Layer: Layer defining the forbidden layer.
        """
        return self._layer
    

class ObstacleRule(LayerRule):
    """Rule which defines a obstacle, given by the bounding box of the cell.
    """
    def __init__(self, *, cell: Cell, layer: Layer) -> None:
        """
        Args:
            cell (Cell): Cell for which the rule should be generated. 
            layer (Layer): Layer for which the rule holds.
        """
        name = f"{self.__class__.__name__}({layer.name}, {cell._name})"
        super().__init__(cell=cell, name=name, layer=layer)

    def get_area(self) -> tuple:
        """Get the area which is blocked, by the rule

        Returns:
            tuple: (min_x, min_y, max_x, max_y)
        """
        area = self.cell.get_bounding_box()
        area[0] -= self.layer.minSpace
        area[1] -= self.layer.minSpace
        area[2] += self.layer.minSpace
        area[3] += self.layer.minSpace
        
        return tuple(self.cell.get_bounding_box())

        