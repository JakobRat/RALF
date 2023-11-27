# Copyright 2022 Kotaro Terada
#
# Copyright 2023 Jakob Ratschenberger
#
# Modifications:
# - Modified __init__() to get the floorplan of a placed circuit
# - Modified __repr__() to show the HPWL
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
from typing import Dict, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from SchematicCapture.Devices import Device
    from SchematicCapture.Net import Net

from .cell_sliding import cell_slide3
from .problem import Problem

class Floorplan:
    """
    A class to represent a rectangle packing floorplan.
    """

    def __init__(self, positions: List[Dict], bounding_box: Tuple, problem : Problem, area: Union[int, float] = -1.0) -> None:
        self.positions = positions
        self.problem = problem
        
        circuit = problem.circuit
        rudy = problem.rudy

        #place the devices of the circuit
        for pos in positions:
            device_name = self.problem.id_to_device(pos['id'])
            device : Device
            device = circuit.devices[device_name]
            x = pos['x']
            y = pos['y']
            w = pos["width"]
            h = pos["height"]
            r = pos["rotation"]
            device.cell.reset_place()
            device.cell.place((x+w//2, y+h//2), (r%4)*90)
            
        #slide the cells, such that there are no violated placement-rules
        cell_list = [device.cell for device in circuit.devices.values()]
        cell_slide3(cells=cell_list)

        self.bounding_box = bounding_box
        if 0 < area:
            self.area = area
        else:
            self.area = bounding_box[0] * bounding_box[1]
        
        #calculate the HPWL of the placement
        self.HPWL = 0
        for net_name, net in circuit._nets.items():
            net : Net
            self.HPWL += net.HPWL()
        
        #calculate the estimated congestion of the placement
        self.congestion = 0
        rudy.clear_nets()
        for net in circuit._nets.values():
            rudy.add_net(net)

        self.congestion = rudy.congestion()

    def __repr__(self) -> str:
        s = "Floorplan({"
        s += "'positions': " + str(self.positions) + ", "
        s += "'bounding_box': " + str(self.bounding_box) + ", "
        s += "'area': " + str(self.area) + ", " 
        s += "'HPWL: '" + str(round(self.HPWL,2)) + ", "
        s += "'congestion: '" + str(round(self.congestion,2)) + "})"

        return s
