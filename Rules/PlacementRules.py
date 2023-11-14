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
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Magic.Cell import Cell
    from Magic.MacroCell import MacroCell
    from PDK.Layers import Layer
    from SchematicCapture.Net import Net

import abc
from collections import deque

class PlacementRules:
    """Class to store placement rules for a cell.
    """
    def __init__(self, cell : Cell, rules:list[PlacementRule]) -> None:
        """Merge all placement-rules given by rules, into one rule.

        Args:
            cell (Cell): Cell for which the placement-rules apply.
            rules (list[PlacementRule]): Placement rules of the cell.
        """
        self._cell = cell
        self._rules = rules
    

    @property
    def cell(self) -> Cell:
        """Get the cell of the placement rules.

        Returns:
            Cell: Cell of the placement rules.
        """
        return self._cell
    
    @property
    def rules(self) -> list[PlacementRule]:
        """Get a list of placement rules.

        Returns:
            list[PlacementRule]: List of placement rules.
        """
        return self._rules

    def generate_rule(self, other_rules : PlacementRules) -> tuple[float, float, float, float]:
        """Generate a rule to satisfy all placement rules between, self and other_rules.

        Args:
            other_rules (PlacementRules): Other placement rules.

        Returns:
            tuple: (min_x, min_y, max_x, max_y) of the resulting rule.
        """
        bound = self.cell.get_bounding_box()
        for rule1 in self.rules:
            for rule2 in other_rules.rules:
                if rule1.conflict(rule2):
                    rule_bound = rule1.generate_rule(rule2)
                    bound[0] = min(bound[0],rule_bound[0])
                    bound[1] = min(bound[1],rule_bound[1])
                    bound[2] = max(bound[2],rule_bound[2])
                    bound[3] = max(bound[3],rule_bound[3])
        
        return bound                  
                    


class PlacementRule(metaclass = abc.ABCMeta):
    """Class to store a placement rule.
    """
    @abc.abstractmethod
    def __init__(self, *, cell : Cell, name : str) -> None:
        self._name = name
        self._cell = cell

    def __repr__(self) -> str:
        cname = self.__class__.__name__
        return f"{cname}(name={self._name})"
    
    def __eq__(self, __value: object) -> bool:
        """Rules are equal if they have the same name.

        Args:
            __value (object): Object to be compared.

        Returns:
            bool: True if object is a rule, and has the same name as self.
        """
        return (isinstance(__value, PlacementRule)) and (self._name == __value._name)
    
    def __hash__(self) -> int:
        return hash(self._name)
    
    @property
    def name(self) -> str:
        """Get the name of the rule.

        Returns:
            str: Name of the rule.
        """
        return self._name

    @property
    def cell(self) -> Cell:
        """Get the cell, to which the rule belongs.

        Returns:
            Cell: Cell of the rule.
        """
        return self._cell
    
    @abc.abstractmethod
    def conflict(self, other_rule : PlacementRule) -> bool:
        """Check if this rule is in conflict with another rule.

        Args:
            other_rule (PlacementRule): Other placement rule.

        Returns:
            bool: True if there is a conflict, else False.
        """
        pass

    @abc.abstractmethod
    def generate_rule(self, other_rule : PlacementRule):
        """Get the bounding box of the cell, which satisfies
            the rules. 

        Args:
            other_rule (PlacementRule): Other placement rule.

        Returns:
            tuple: (min_x, min_y, max_x, max_y) 
        """
        return tuple()

class Spacing(PlacementRule):
    """ Class to generate a spacing rule.
    """
    def __init__(self, *, cell : Cell, layer : Layer, net : Net = None) -> None:
        """Spacing-Placement rule. 
        This rule specifies a bounding-box within those a other cell can't be placed.

            -------------------------
            |   ________________     |
            |   |               |<-->| layer.minSpace
            |   |   Cell        |    |
            |   |_______________|    |
            |                        |
            ------------------------
        
        Args:
            cell (Cell): Cell for which the placement bounding box gets specified.
            layer (Layer): Layer for which a spacing rule must be applied.
            net (Net, optional): Net connected to the layer. Defaults to None.
        """
        if net:
            name = f"{self.__class__.__name__}({layer.name}, {net.name}, {str(round(layer.minSpace, 2))})"
        else:
            name = f"{self.__class__.__name__}({layer.name}, {str(round(layer.minSpace, 2))})"        
        
        super().__init__(cell=cell, name=name)

        self._layer = layer
        self._net = net
        self._min_spacing = layer.minSpace

    @property
    def layer(self) -> Layer:
        """Get the layer of the rule.

        Returns:
            Layer: Layer of the rule.
        """
        return self._layer

    @property
    def net(self) -> Net:
        """Get the net of the rule.

        Returns:
            Net: Net of the rule.
        """
        return self._net
    
    def conflict(self, other_rule: PlacementRule) -> bool:
        """A spacing conflict appears, if the other rule is also a spacing rule
            and they have the same layer but different nets.
        Args:
            other_rule (Rule): Other rule for comparison.

        Returns:
            bool: True if there is a conflict between the rules.
        """
        if isinstance(other_rule, Spacing) and (self._layer == other_rule._layer):
            if self._net and other_rule._net:
                return self._net != other_rule._net
            else:
                return True
        else:
            return False
        
    def generate_rule(self, other_rule: PlacementRule) -> tuple[float, float, float, float]:
        """Get the bounding box of the cell, which satisfies
            the spacing rule. 

        Args:
            other_rule (PlacementRule): Other placement rule.

        Returns:
            tuple: (min_x, min_y, max_x, max_y) 
        """
        if self.conflict(other_rule):
            #if there is a conflict to the other rule
            #expand the cells bounding box by the amount of minSpace
            spacing = self._min_spacing
            bounding = self.cell.get_bounding_box()
            bounding[0] -= spacing
            bounding[1] -= spacing
            bounding[2] += spacing
            bounding[3] += spacing
            return tuple(bounding)
        else:
            return tuple(self.cell.get_bounding_box())
    
class MacroSpacing(Spacing):
    """Class to generate a spacing rule for a macro cell.
    """
    def __init__(self, *, cell: MacroCell, cell_spacing : Spacing, net: Net = None) -> None:
        """Setup a spacing rule for a macro cell.

        Args:
            cell (MacroCell): MacroCell to which the rule will be added.
            cell_spacing (Spacing): Spacing rule which shall be applied also to the macro.
            net (Net, optional): Net to which the rule belongs. Defaults to None.
        """
        layer = cell_spacing._layer
        super().__init__(cell=cell, layer=layer, net=net)
        
        #calculate the needed spacings from the cell given in cell_spacing
        cell_bound = cell_spacing.cell.get_bounding_box()
        cell_min_space = cell_spacing._min_spacing
        
        cell_bound_enlarged = [cell_bound[0]-cell_min_space, cell_bound[1]-cell_min_space, cell_bound[2]+cell_min_space, cell_bound[3]+cell_min_space]

        macro_bound = cell.get_bounding_box()

        #needed spacings
        self._spaces = [max(macro_bound[0]-cell_bound_enlarged[0],0), #needed spacing at the W side of the macro
                        max(macro_bound[1]-cell_bound_enlarged[1],0), #needed spacing at the S side of the macro
                        max(cell_bound_enlarged[2]-macro_bound[2],0), #needed spacing at the E side of the macro
                        max(cell_bound_enlarged[3]-macro_bound[3],0)] #needed spacing at the N side of the macro

        #store the initial rotation of the cell
        self._rotation = cell.rotation


    def generate_rule(self, other_rule: PlacementRule):
        """Get the bounding box of the cell, which satisfies
            the spacing rule. 

        Args:
            other_rule (PlacementRule): Other placement rule.

        Returns:
            tuple: (min_x, min_y, max_x, max_y) 
        """
        if self.conflict(other_rule):
            spacing = deque(self._spaces)
            #if the macro were rotated, -> calculate the new spacings
            if self.cell.rotation != self._rotation:
                #spacings rot = 0deg: W,S,E,N
                #spacings rot = 90deg: S,E,N,W
                #spacings rot = 180deg: E,N,W,S
                #spacings rot = 270deg: N,W,S,E
                # for each rotation of the macro cell by 90deg 
                # the spacing list has to be rotated left by one position 
                n_rot = (self._rotation-self.cell.rotation)//90
                spacing.rotate(n_rot)
            
            spacing = list(spacing)
            bounding = self.cell.get_bounding_box()
            bounding[0] -= spacing[0]
            bounding[1] -= spacing[1]
            bounding[2] += spacing[2]
            bounding[3] += spacing[3]
            return tuple(bounding)
        else:
            return tuple(self.cell.get_bounding_box())