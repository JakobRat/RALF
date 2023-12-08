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
    from Magic.MagicDie import MagicDie

from rectangle_packing_placement.placement_problem import PlacementProblem
from rectangle_packing_placement.placement_solver import PlacementSolver
from rectangle_packing_placement.placement_visualizer import PlacementVisualizer

from SchematicCapture.utils import get_bottom_up_topology

import copy

from SchematicCapture.Circuit import SubCircuit
from Magic.MacroCell import MacroCell
from SchematicCapture.Devices import SubDevice

from rectangle_packing_solver.cell_sliding import cell_slide3
from prettytable import PrettyTable
import time

def do_placement(circuit : Circuit, width_limit = None, height_limit = None, simanneal_minutes = 0.1, simanneal_steps = 200, fig_path = None, show_stats = True) -> Circuit:
    """Perfom a placement of circuit <circuit> by using a sequence-pair representation of the placement and performing
    optimization per simulated annealing.

    Args:
        circuit (Circuit): Circuit which shall be placed.
        width_limit (_type_, optional): Maximum width of the placement. Defaults to None.
        height_limit (_type_, optional): Maximum height of the placement. Defaults to None.
        simanneal_minutes (float, optional): Set the maximum duration of the annealing. Defaults to 0.1.
        simanneal_steps (int, optional): Set the maximum steps which will be performed by the annealing. Defaults to 200.
        fig_path (_type_, optional): Path to store a figure of the placement. Defaults to None.

    Returns:
        Circuit: Circuit with placed cells.
    """
    #measure the taken time
    start = time.time()

    #setup a placement problem
    problem = PlacementProblem(circuit=circuit)
    #find a solution for the problem
    print(f"Finding placement for circuit {circuit.name}.")
    solution = PlacementSolver().solve(problem=problem, height_limit=height_limit, width_limit=width_limit, 
                              simanneal_minutes=simanneal_minutes, simanneal_steps=simanneal_steps, show_progress=True)

    if fig_path:
        #save a figure of the placement
        PlacementVisualizer().visualize(solution=solution, path=f"{fig_path}/{circuit.name}.png")
    
    #slide the cells, such that there are no violated placement-rules
    cell_list = [device.cell for device in solution.problem.circuit.devices.values()]
    cell_slide3(cells=cell_list)
    
    if show_stats:
        name = solution.problem.circuit.name
        HPWL = solution.floorplan.HPWL()
        congestion = solution.floorplan.rudy_congestion()
        taken_time = int(time.time() - start)
        n_placements = simanneal_steps
        
        bounding_box = [float('inf'),float('inf'),-float('inf'),-float('inf')]
        for cell in cell_list:
            bound = cell.get_bounding_box()
            bounding_box[0] = min(bounding_box[0], bound[0])
            bounding_box[1] = min(bounding_box[1], bound[1])
            bounding_box[2] = max(bounding_box[2], bound[2])
            bounding_box[3] = max(bounding_box[3], bound[3])

        height = bounding_box[3]-bounding_box[1]
        width = bounding_box[2]-bounding_box[0]

        area = round(height*width,2)

        table = PrettyTable(['Name', 'Value'])
        table.add_row(['Circuit', name])
        table.add_row(['Time taken [s]', taken_time])
        table.add_row(['Placements', n_placements])
        table.add_row(['Total HPWL', round(HPWL,2)])
        table.add_row(['Congestion', round(congestion,2)])
        table.add_row(['Total width', width])
        table.add_row(['Total height', height])
        table.add_row(['Area', area])
        
        print(table)
        

    return solution.problem.circuit

def do_bottom_up_placement(die : MagicDie, simanneal_minutes = 0.1, simanneal_steps = 200, fig_path = None, show_stats=True) -> Circuit:
    """ Perform a placement in a bottom-up fashion on the circuit defined in <die>.

    Args:
        die (MagicDie): Die for which a placement shall be found.
        simanneal_minutes (float, optional): Set the maximum duration of the annealing. Defaults to 0.1.
        simanneal_steps (int, optional): Set the maximum steps which will be performed by the annealing. Defaults to 200.
        fig_path (_type_, optional): Path to store a figure of the placement. Defaults to None.
    """
    #get the circuit
    circuit = die._circuit

    #determine the max. width and height of the placement
    die_bound = die.bounding_box
    if not (die_bound is None):
        max_width = die_bound.width
        max_height = die_bound.height
    else:
        max_width = None
        max_height = None

    #determine the placement order
    placement_order = get_bottom_up_topology(circuit)
    
    #setup a dict to store the best circuits
    circ_dict = {}

    #do a placement for each circuit
    for (t, c) in placement_order:
        c : Circuit
        if c.name in circ_dict:
            #if the circuit were already placed
            #retrieve the cells position
            circuit_mapped = c.map_devices_to_netlist()
            for device_name, device_location in circ_dict[c.name].items():
                
                circuit_mapped[device_name].cell.reset_place()
                circuit_mapped[device_name].cell.place(device_location[0], device_location[1])

        else:
            #place the circuit
            if len(c.devices)>1:
                best_circuit = do_placement(c, height_limit=max_height, width_limit=max_width, 
                                            simanneal_minutes=simanneal_minutes, simanneal_steps=simanneal_steps, fig_path=fig_path, show_stats=show_stats)
                circ_dict[c.name] = get_cell_locations(best_circuit)
            else:
                #if there is only one device, do no placing
                best_circuit = c
                circ_dict[c.name] = get_cell_locations(best_circuit)

        if type(c) is SubCircuit:
            #if circuit was a sub-circuit, make a macro cell out of the placed cells
            cells = [circ.cell for circ in list(c.devices.values())]
            macro = MacroCell(c.name, cells)
            c.sub_device.set_cell(macro)


    #placement done
    #move the devices inside a macro-cell 
    #such that they match with the bounding box of the macro
    for (t, c) in reversed(placement_order):
        for d in list(c.devices.values()):
            if type(d) is SubDevice:
                d.cell._move_cells_to_bound()

def get_cell_locations(circuit : Circuit) -> dict[str, tuple]:
    """Get the locations of the cells of the circuit.

    Args:
        circuit (Circuit): Circuit

    Returns:
        dict[str, tuple]: key: Name of the device (as in the netlist), (center_point, rotation)
    """
    map = {}
    for device_name, device in circuit.map_devices_to_netlist().items():
        map[device_name] = (device.cell.center_point, device.cell.rotation)
    
    return map
