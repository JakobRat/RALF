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
from typing import Dict, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from SchematicCapture.Devices import Device
    from SchematicCapture.Net import Net
    from rectangle_packing_placement.placement_problem import PlacementProblem

from rectangle_packing_placement.rectangle_packing_solver.floorplan import Floorplan
from rectangle_packing_placement.cell_sliding import cell_slide3


class PlacementFloorplan(Floorplan):
    """Class to setup a floorplan for a placement.
    """
    def __init__(self, positions: List[Dict], bounding_box: Tuple, problem : PlacementProblem, area: int | float = -1) -> None:
        """Initialize the floorplan.

        Args:
            positions (List[Dict]): Positions of the rectangles.
            bounding_box (Tuple): Bounding box of the rectangles.
            problem (PlacementProblem): Placement problem.
            area (int | float, optional): Area of the placement. Defaults to -1.
        """
        super().__init__(positions, bounding_box, area)

        self.problem = problem
        self.circuit = problem.circuit

        #place the devices of the circuit
        for pos in positions:
            device_name = self.problem.id_to_device(pos['id'])
            device : Device
            device = self.circuit.devices[device_name]
            x = pos['x']
            y = pos['y']
            w = pos["width"]
            h = pos["height"]
            r = pos["rotation"]
            device.cell.reset_place()
            device.cell.place((x+w//2, y+h//2), (r%4)*90)
        
        #slide the cells, such that there are no violated placement-rules
        cell_list = [device.cell for device in self.circuit.devices.values()]
        cell_slide3(cells=cell_list)

    
    def HPWL(self) -> float:
        """Get the HPWL of the placement.

        Returns:
            float: HPWL of the placement.
        """
        HPWL = 0
        for net_name, net in self.circuit.nets.items():
            net : Net
            HPWL += net.HPWL()
        return HPWL
    

    def rudy_congestion(self)->float:
        """Get the estimated congestion of the placement.

        Returns:
            float: Estimated congestion of the placement.
        """
        self.problem.rudy.clear_nets()
        for net in self.circuit.nets.values():
            self.problem.rudy.add_net(net)
        
        return self.problem.rudy.congestion()
    
    def __repr__(self) -> str:
        s = "PlacementFloorplan({"
        s += "'positions': " + str(self.positions) + ", "
        s += "'bounding_box': " + str(self.bounding_box) + ", "
        s += "'area': " + str(self.area) + ", " 
        s += "'HPWL: '" + str(round(self.HPWL(),2)) + ", "
        s += "'congestion: '" + str(round(self.rudy_congestion(),2)) + "})"

        return s