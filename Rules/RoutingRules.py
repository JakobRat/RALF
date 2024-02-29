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
        
        return tuple(area)

        