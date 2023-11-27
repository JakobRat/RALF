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
    from SchematicCapture.Devices import Device

from rectangle_packing_placement.rectangle_packing_solver.problem import Problem
from Environment.RUDY import RUDY
from PDK.PDK import global_pdk

class PlacementProblem(Problem):
    """Class to setup a placement problem.
    """
    def __init__(self, circuit : Circuit) -> None:
        """Init the problem.

        Args:
            circuit (Circuit): Circuit of the problem.
        """
        #store the circuit
        self.circuit = circuit

        #setup RUDY of the PDK, for 
        #wire-density estimation
        self.rudy = RUDY(global_pdk)

        #store a map between rectangles and devices
        self._rectangle_device_map = {}

        #setup the rectangles of the problem
        rectangles = []
        n_id = 0
        device : Device
        for name, device in circuit.devices.items():
            cell = device.cell
            rectangles.append([cell.width, cell.height, 1])
            self._rectangle_device_map[n_id] = name
            n_id += 1

        #setup the rectangle packing problem
        super().__init__(rectangles)

    def id_to_device(self, id : int) -> str:
        """Maps rectangle id to the device name.

        Args:
            id (int): Rectangle id.

        Returns:
            str: Name of the corresponding device.
        """
        return self._rectangle_device_map[id]