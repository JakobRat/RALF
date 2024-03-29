# ========================================================================
#   
# Collection of useful methods to perform a RL based placement.
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
from Magic.Cell import Cell
from Magic.MacroCell import MacroCell
from typing import List
import numpy as np
import copy

from SchematicCapture.Circuit import Circuit, SubCircuit
from PPO.utils import train
from Environment.Environment import Placement
from SchematicCapture.utils import get_bottom_up_topology
from SchematicCapture.Devices import SubDevice, Device
from Environment.RUDY import RUDY

import logging
logger = logging.getLogger(__name__)
from prettytable import PrettyTable
import time

def do_placement(circ : Circuit, name :str, n_placements : int, placements_per_rollout = 100, use_weights = False, show_stats = True):
    """Performs the placement of circuit <circ>.

    Args:
        circ (Circuit): Circuit to be placed.
        name (str): Name of the placement.
        n_placements (int): Number of total placements to be done.
        placements_per_rollout (int): Number of placements per iteration. optional, default: 100
        use_weights (bool): If True, network-weights of a previous run will be used.
    Returns:
        Circuit: Circuit of best placement.
    """
    assert n_placements%placements_per_rollout==0, f"Number of total placements not divisible by the number of placements per rollout!"

    placements_per_batch = placements_per_rollout
    total_placements = n_placements
    n_rollouts = total_placements/placements_per_batch

    #measure the taken time
    start = time.time()

    #setup the environment
    logger.info(f"Doing placement {name} of circuit {circ.name} for {n_rollouts} rollouts.")
    logger.debug(f"Circuit: type {type(circ)}, id {id(circ)}")

    #get maximum side-length of the placement
    side_length = 0
    for (d_name, d) in circ.devices.items():
        assert isinstance(d, Device)

        cell = d.cell
        side_length += max(cell.width, cell.height)
    side_length = int(side_length)
    
    print(f"Doing placement {name} of circuit {circ.name} for {n_rollouts} rollouts.")
    print(f"Using an environment with dimension {side_length}x{side_length}.")

    #setup a environment
    env = Placement(circ, name, (side_length, side_length), exclude_nets=[])

    logger.info(f"Set up placement environment with size {env.size}.")
    logger.debug(f"Environment: type {type(env)}, id {id(env)}")

    
    #setup the hyperparameters for the PPO algorithm
    hyperparameters = {

                        'placements_per_batch': placements_per_batch, 
                        'gamma': 0.99, 
                        'n_updates_per_iteration': 5,
                        'lr': 1e-4, 
                        'clip': 0.2,
                        'stopping_std': 1,
                        'render': False,
                        'render_every_i': 1,
                        'plot_grad_flow': False,
                        'plot_log': False
                    }
    
    actor_model = 'Network/Weights/ppo_actor.pth' if use_weights else ''
    critic_model = 'Network/Weights/ppo_critic.pth' if use_weights else ''
    
    #train the RL agent
    train(env=env, hyperparameters=hyperparameters, actor_model=actor_model, critic_model=critic_model, total_placements=total_placements)

    #get the best placement
    best_rew = env.best_reward
    best_placement = env.best_placement
    best_placement_number = env._best_placement_number

    logger.info(f"Placement of {name} done with reward {best_rew}.")
    logger.debug(f"Circuit of best placement:  type {type(best_placement)}, id {id(best_placement)}")

    print(f"Placement of {name} done with reward {best_rew}, found at placement #{best_placement_number}.")

    if show_stats:
        time_taken = int(time.time()-start)
        HPWL = 0
        rudy_congestion = RUDY(env._pdk)
        for net in best_placement.nets.values():
            HPWL += net.HPWL()
            rudy_congestion.add_net(net)
        
        congestion = rudy_congestion.congestion()

        bounding_box = [float('inf'),float('inf'),-float('inf'),-float('inf')]
        for device in best_placement.devices.values():
            bound = device.cell.get_bounding_box()
            bounding_box[0] = min(bounding_box[0], bound[0])
            bounding_box[1] = min(bounding_box[1], bound[1])
            bounding_box[2] = max(bounding_box[2], bound[2])
            bounding_box[3] = max(bounding_box[3], bound[3])

        height = bounding_box[3]-bounding_box[1]
        width = bounding_box[2]-bounding_box[0]

        area = round(height*width,2)

        table = PrettyTable(['Name', 'Value'])
        table.add_row(['Circuit', name])
        table.add_row(['Time taken [s]', time_taken])
        table.add_row(['Placements', total_placements])
        table.add_row(['Placements per batch', placements_per_batch])
        table.add_row(['Env. size', f"{side_length}x{side_length}"])
        table.add_row(['Solution placement', best_placement_number])
        table.add_row(['Total HPWL', round(HPWL,2)])
        table.add_row(['Congestion', round(congestion,2)])
        table.add_row(['Reward', round(best_rew,2)])
        table.add_row(['Total width', width])
        table.add_row(['Total height', height])
        table.add_row(['Area', area])
        
        print(table)

        try:
            print(table, file=open(f'Logs/Stats/{name}_RL_placement_stats.txt','w'))
        except:
            print(table, file=open(f'Logs/Stats/{name}_RL_placement_stats.txt','a'))

    return best_placement

def do_bottom_up_placement(circ : Circuit, n_placements : int, placements_per_rollout : int = 100, use_weights = False, show_stats=True):
    """Perform a placement in a bottom-up fashion on circuit <circ>.

    Args:
        circ (Circuit): Circuit which shall be placed.
        n_placements (int): Number of total placements per circuit/subcircuit.
        placements_per_rollout (int): Number of placements per rollout. optional, default: 100
        use_weights (bool, optional): If True, network-weights of a previous run will be used. Defaults to False.
    """
    logger.info(f"Performing bottom-up placement on circuit {circ.name} for {n_placements} placements per circuit/subcircuit.")
    logger.debug(f"Circuit: type {type(circ)}, id {id(circ)}")
 
    placement_order = get_bottom_up_topology(circ)
    logger.debug(f"Placement order: {[(c.name, id(c)) for (t, c) in placement_order]}")

    #setup a dict to store the best circuits
    circ_dict = {}

    for (t, c) in placement_order:
        
        if c.name in circ_dict:
            #if circuit was already placed, get the circuit
            best_circuit = circ_dict[c.name]
        else:
            #place circuit
            if len(c.devices)>1:
                best_circuit = do_placement(c, c.name, n_placements=n_placements, placements_per_rollout=placements_per_rollout, use_weights=use_weights, show_stats=show_stats)
                circ_dict[c.name] = copy.deepcopy(best_circuit)
                logger.debug(f"Best-circuit: type {type(best_circuit)}, id {id(best_circuit)}")
            else:
                #if there is only one device, do no placing
                best_circuit = c
                circ_dict[c.name] = copy.deepcopy(best_circuit)

        best_circuit_mapped = best_circuit.map_devices_to_netlist()
        circuit_mapped = c.map_devices_to_netlist()

        for (k,v) in best_circuit_mapped.items():

            logger.debug(f"Updating cell of device {k}.")
            logger.debug(f"Best-location {v.cell.center_point}, Best-rotation {v.cell.rotation}.")
            circuit_mapped[k].cell.reset_place()
            circuit_mapped[k].cell.place(v.cell.center_point, v.cell.rotation)
            logger.debug(f"Updated cell to location {circuit_mapped[k].cell.center_point} and rotation {circuit_mapped[k].cell.rotation}.")
            

        #c.devices = best_circuit.devices

        if type(c) is SubCircuit:
            #if circuit was a subcircuit, make a macro cell out of the placed cells
            logger.debug(f"Adding macrocell to subcircuit {c.name}.")
            cells = [circ.cell for circ in list(c.devices.values())]
            logger.debug(f"Adding cells: {[(c._name, id(c))  for c in cells]}")
            macro = MacroCell(c.name, cells)
            logger.debug(f"Created macrocell {macro._name}, type {type(macro)}, id {id(macro)}.")

            c.sub_device.set_cell(macro)


    for (t, c) in reversed(placement_order):
        for d in list(c.devices.values()):
            if type(d) is SubDevice:
                d.cell._move_cells_to_bound()


def valid_move(p_cell, current_cell) -> bool:
    """Check if two cells overlap.

    Args:
        p_cell (Cell): Placed cell.
        current_cell (Cell): Current cell.

    Returns:
        bool: True, if they don't overlap, else False.
    """
    bound_p = p_cell.get_bounding_box()
    bound_c = current_cell.get_bounding_box()
    
    EX1 = bound_c[0] - bound_p[2] #Rightward slide dist.
    EX2 = bound_c[2] - bound_p[0] #Leftward slide dist.
    EX3 = bound_c[3] - bound_p[1] #Downward slide dist.
    EX4 = bound_c[1] - bound_p[3] #Upward slide dist.
    
    if EX1>=0 or EX2<=0 or EX3<=0 or EX4>=0: #cells do not overlap
        return True
    else:
        return False
