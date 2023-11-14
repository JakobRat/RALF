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
    from SchematicCapture.Devices import Device, SubDevice
    from SchematicCapture.Net import Net
    from Magic.MagicTerminal import MagicTerminal

class Pin:
    """Class for storing a device pin.
        E.g. The gate-terminal of a MOS is a device pin.
    """
    def __init__(self, name : str, device : Device) -> None:
        """Setup a pin.

        Args:
            name (str): Name of the pin.
            device (Device): Device to which the pin belongs.
        """
        self._name = name #name of the pin
        self._device = device #device to which the pin belongs
        self._net : Net
        self._net = None #net to which the pin is connected
        self._magic_terminal : MagicTerminal
        self._magic_terminal = None #physical terminal of the device pin

    def set_net(self, net : Net):
        """Set the net connected with the pin.

        Args:
            net (Net): Net connected with the pin.
        """
        self._net = net

    def set_magic_terminal(self, terminal : MagicTerminal):
        """Set the corresponding physical terminal of the pin.

        Args:
            terminal (MagicTerminal): Physical terminal of the pin.
        """
        self._magic_terminal = terminal
        
    @property
    def net(self) -> Net:
        return self._net
    
    @property
    def name(self) -> str:
        """Get the name of the pin.

        Returns:
            str: Name of the pin.
        """
        return self._name
    
    @property
    def device(self) -> Device:
        """Get the device, to which the pin belongs.

        Returns:
            Device: Device of the pin.
        """
        return self._device
    
    def get_magic_terminal(self) -> MagicTerminal|None:
        """Get the physical terminal of the pin.

        Returns:
            MagicTerminal|None: Physical terminal of the pin.
        """
        return self._magic_terminal
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(device={self.device.name}, name={self.name})"
    
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Pin) and (self.name == __value.name) and (self._device==__value.device)
    

class Terminal(Pin):
    """ Same as SubDevicePin.
        Declared for sanity, because of renaming to SubDevicePin.
    """
    def __init__(self, name: str, device: SubDevice) -> None:
        super().__init__(name, device)
        self._child_net = None
    
    def update_name(self, new_name : str):
        self._name = new_name
    
    def set_child_net(self, net : Net):
        self._child_net = net

class SubDevicePin(Terminal):
    """Class to store a SubDevicePin.
        A SubDevicePin is a terminal of a sub-device, which connects
        the external net with internal-net of the sub-device.
    """
    def __init__(self, name: str, device: SubDevice) -> None:
        """Setup a pin for a SubDevive.

        Args:
            name (str): Name of the terminal.
            device (SubDevice): SubDevice of the terminal.
        """
        super().__init__(name, device)

        #store the inner-net of the pin.
        # -> the net within the sub-device
        self._child_net : Net
        self._child_net = None
    
    def update_name(self, new_name : str):
        """Update the name of the pin.

        Args:
            new_name (str): New name.
        """
        self._name = new_name
    
    def set_child_net(self, net : Net):
        """Set the child net of the pin.

        Args:
            net (Net): Child net/ inner net of the pin.
        """
        self._child_net = net