# Copyright 2022 Kotaro Terada
#
# Copyright 2023 Jakob Ratschenger
#
# Modifications:
# - Modified __init__() to setup a problem by a circuit.
# - Added id_to_device()
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

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SchematicCapture.Circuit import Circuit
    from SchematicCapture.Devices import Device

from typing import Dict, List, Tuple, Union


class Problem:
    """
    A class to represent a rectangle packing problem.
    """

    def __init__(self, circuit : Circuit) -> None:
        """Setup the problem.

        Args:
            circuit (Circuit): Circuit which shall be placed.
        """
        self.circuit = circuit

        #setup the rectangles of the problem
        rectangles = []
        device : Device
        for name, device in circuit.devices.items():
            cell = device.cell
            rectangles.append([cell.width, cell.height, 1, name])
        
        self.rectangles = []
        self.n = 0
        
        self._rectangle_device_map = {}
        if not isinstance(rectangles, list):
            raise TypeError("Invalid argument: 'rectangles' must be a list.")

        for r in rectangles:
            if isinstance(r, (list, tuple)):
                self.rectangles.append(
                    {
                        "id": self.n,
                        "width": r[0],
                        "height": r[1],
                        "rotatable": r[2] if len(r) >= 3 else False,
                        "device_id": r[3],
                    }
                )
                self._rectangle_device_map[self.n] = r[3]
            elif isinstance(r, dict):
                self.rectangles.append(
                    {
                        "id": self.n,
                        "width": r["width"],
                        "height": r["height"],
                        "rotatable": r["rotatable"] if "rotatable" in r else False,
                        "device_id": r["device_id"],
                    }
                )
                self._rectangle_device_map[self.n] = r["device_id"]
            else:
                raise TypeError("A rectangle must be a list, tuple, or dict.")
            
            
            self.n += 1

    def __repr__(self) -> str:
        s = "Problem({"
        s += "'n': " + str(self.n) + ", "
        s += "'rectangles': " + str(self.rectangles) + "})"

        return s
    
    def id_to_device(self, id : int):
        return self._rectangle_device_map[id]
