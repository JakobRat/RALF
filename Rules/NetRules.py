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

from SchematicCapture.Net import Net

if TYPE_CHECKING:
    from Magic.Cell import Cell
    from Magic.MacroCell import MacroCell
    from PDK.Layers import Layer
    from SchematicCapture.Net import Net
    from Magic.MagicLayer import Rectangle

import abc
from Rules.Rule import Rule


class NetRule(Rule, metaclass = abc.ABCMeta):
    """
        A NetRule gets applied on a specific net. E.g. minimum wire-width of an net.
    """ 
    def __init__(self, *, net : Net, name: str) -> None:
        super().__init__(name=name)
        self._net = net
        self._net.add_rule(self) #add the rule to the net
    
    @property
    def net(self) -> Net:
        """Get the net of the rule.

        Returns:
            Net: Net of the rule.
        """
        return self._net

class MinNetWireWidth(NetRule):
    """Define a minimum wire-width for a net.
    """
    def __init__(self, *, net: Net, min_width : float) -> None:
        name = f"{self.__class__.__name__}({net.name}, {round(min_width,2)})"
        super().__init__(net=net, name=name)
        self._min_width = min_width
    
    @property
    def min_width(self) -> float:
        """Get the minimum width of the net.

        Returns:
            float: Minimum width of the net.
        """
        return self._min_width

class Port(NetRule):
    """Set a net as a port.
    """
    def __init__(self, *, net: Net) -> None:
        name = f"{self.__class__.__name__}({net.name})"
        super().__init__(net=net, name=name)

class Ports:
    """Set for multiple nets ports.
    """
    def __init__(self, *, nets: list[Net]) -> None:
        for net in nets:
            Port(net=net)

class PowerNet(NetRule):
    """Define a net as a power net. E.g. Vdd, Vss, VGND, ...
    """
    def __init__(self, *, net: Net) -> None:
        name = f"{self.__class__.__name__}({net.name})"
        super().__init__(net=net, name=name)

class PowerNets:
    """Define multiple nets as power nets.
    """
    def __init__(self, *, nets: list[Net]) -> None:
        for net in nets:
            PowerNet(net=net)