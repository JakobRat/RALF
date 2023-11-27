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
    import torch_geometric
    import torch_geometric.data

from SchematicCapture.Circuit import Circuit
from Magic.DRC import DRC_collidates, DRC_collidates_all, DRC_magic_check_cell, DRC_magic_all
from Magic.utils import place_circuit
from Environment.cell_sliding import cell_slide3

import numpy as np
from torch_geometric.utils.convert import from_networkx, to_networkx 
import random

import copy


import pandas as pd


import torch
import pygame

import math
from PDK.PDK import global_pdk

import pickle
import os

import time

from Environment.RUDY import RUDY

class Placement:
    """Class for a placement environment, which is needed for RL.
    """
    def __init__(self, Circuit : Circuit, name : str, size : tuple[int, int], use_magic_DRC = False , exclude_nets : list[str] = None):
        """Setup a placement environment for a RL problem.

        Args:
            Circuit (Circuit): Circuit which shall be placed.
            name (str): Name of the placement.
            size (tuple[int, int]): Playground size.
            use_magic_DRC (bool, optional): True, if the DRC - check of magic shall be used. Defaults to False.
            exclude_nets (list[str], optional): Nets which shall be excluded for the placement - metric calculation. Defaults to None.
        """

        self._circuit = Circuit
        
        self._size = size
        self._name = name
        self._action_space = size
        
        #setup a list for the placement order
        self._placement_order = []
        #setup a list for the already placed cells
        self._placed_cells = []

        # store the number of done steps
        # a step is equivalent of placing a device
        self._n_step = 0
        
        #get the number of devices, which shall be placed
        self._n_devices = len(self._circuit.devices.keys())
        
        #store HPWLs of placements
        self.HPWLs = []

        self._exclude_nets = exclude_nets
        
        #store if pygame was already initialized
        self._pygame_init = False

        self._use_magic_DRC = use_magic_DRC 

        #Reward defs.
        self._DRC_error_rew = -(self._size[0] + self._size[1])*self._n_devices #worst possible HPWL
        self._DRC_free_rew = 0

        #store the best reward
        self._best_rew = 0
        #store the best placement
        self._best_placement = None
        #store the number of done placements
        self._total_placements = 0
        #store the number of placement, as the best placement occurred
        self._best_placement_number = 0

        #set the pdk
        self._pdk = global_pdk

        #store the data of the placement
        self._data = None

        #setup RUDY of the PDK, for 
        #wire-density estimation
        self._rudy = RUDY(self._pdk)

    @property
    def best_placement(self) -> Circuit:
        """
        Returns:
            Circuit: Circuit of the best placement
        """
        return self._best_placement
    
    @property
    def best_reward(self) -> float:
        """Get the best reward.

        Returns:
            float: Best reward.
        """
        return self._best_rew

    @property
    def name(self) -> str:
        """Name of the placement environment.

        Returns:
            str: Name of the placement environment. 
        """
        return self._name
    
    @property
    def size(self) -> tuple[int, int]:
        """Size of the Layout - grid.

        Returns:
            tuple[int, int]: Size of the Layout - grid.
        """
        return self._size
    
    @property
    def n_step_max(self) -> int:
        """Get the maximum number of steps, per placement.

        Returns:
            int: Maximum number of steps, per placement.
        """
        return self._n_devices
    
    def init_Circuit(self):
        """Initialize the circuit for the placement.
        """
        for (d_name, d) in self._circuit._devices.items():
            d.cell.reset_place()
    
    def HPWL(self) -> float:
        """Get the HPWL of the actual placement.

        Returns:
            float: HPWL of the actual placement.
        """
        d = 0
        for net in list(self._circuit._nets.values()):
            if net.name not in self._exclude_nets:
                
                d +=  net.HPWL()
            
        return d
    
        
    def rudy_congestion(self) -> float:
        """Get the estimated congestion of the placement.

        Returns:
            float: Estimated congestion of the placement.
        """
        self._rudy.clear_nets()
        for net in self._circuit._nets.values():
            self._rudy.add_net(net)

        return self._rudy.congestion()
    
    def _get_data(self, update_only = []) -> torch_geometric.data.Data:
        """Get the data of the placement.

        Args:
            update_only (list, optional): List of devices, for which the data shall be updated . Defaults to [].

        Returns:
            torch_geometric.data.Data: Updated data-tensor.
        """
        if self._data:
            #if there is already a data
            if update_only:
                #if only some devices shall be updated
                data = self._data
                #get the nodes of the edges
                nodes1 = data.edge_index[0] #first nodes
                nodes2 = data.edge_index[1] #second nodes

                edge_nets = data.edge_name #nets of the edges
                node_names = data.name #names of the nodes

                #update the data 
                for d in update_only:
                    d_name = d.name
                    #get the index of device
                    d_index = node_names.index(d_name)
                    #update the data by the new devices features
                    data.x[d_index] = torch.tensor(self._circuit.devices[d_name].feature_list , dtype=torch.float32)
                    
                    #get the edges which are connected to the device
                    mask = nodes1 == d_index
                    indices = mask.nonzero()

                    #update the data of the edges connected to the device
                    for i in indices:
                        name1 = node_names[nodes1[i]]
                        name2 = node_names[nodes2[i]]
                        net_name = edge_nets[i]
                        data.edge_attr[i] = torch.tensor(self._circuit.get_edge_feature(name1, name2, net_name), dtype=torch.float32)
            else:
                #update the whole data
                data = self._data
                #generate new data for each device
                data.x = torch.tensor([self._circuit.devices[d].feature_list for d in data.name], dtype=torch.float32)
                
                nodes1 = data.edge_index[0] #first nodes
                nodes2 = data.edge_index[1] #second nodes
                edge_nets = data.edge_name #nets of the edges
                node_names = data.name #names of the nodes
                
                #generate edge data for each edge
                data.edge_attr = torch.tensor([self._circuit.get_edge_feature(node_names[u], node_names[v], net) for (u,v,net) in zip(nodes1, nodes2, edge_nets)], dtype=torch.float32)
        else:
            #setup the data from the circuit
            graph = self._circuit.feature_graph
            data = from_networkx(graph)
            data.x = data.x.to(dtype=torch.float32)
            data.edge_attr = data.edge_attr.to(dtype=torch.float32)
            self._data = data
        
        return data
    
    def reset(self) -> tuple[torch_geometric.data.Data, str]:
        """Reset the placement environment.

        Returns:
            tuple[torch_geometric.data.Data, str]: Data of the environment, Name of the device which will be placed next
        """
        #initialize the circuit
        self.init_Circuit()
        
        #reset the placed cells
        self._placed_cells = []

        #get a random placement order
        self._placement_order = list(self._circuit.devices.keys())
        random.shuffle(self._placement_order)
        
        #get the first device which shall be placed
        device_to_place = self._circuit.devices[self._placement_order[0]]
        device_to_place.cell.place_next()
        
        #reset the number of done steps
        self._n_step = 0
        
        info = self._placement_order[0]
        return self._get_data(), info
        
    def step(self, coordinate : tuple[int, int], rotation : int) -> tuple[torch_geometric.data.Data, float, bool, bool, str]:
        """
        Performs a step in the environment.
        Places the next device at the given coordinate and rotation.
        Evaluates the placing, by performing a DRC.
        If the placement isn't DRC clean, the episode gets
        truncated.
        If all placements are valid, the epoch has to be terminated by a reset.

        Parameters
        ----------
        coordinate : Tuple (int, int)
            Mean coordinate of the device to be placed.
        
        rotation : int 
            Rotation of the device. One of (0,1,2,3) => (0,90,180,270).

        Returns
        -------
        observation : torch data
            Actual state of the circuit.
        reward : float
            Reward of the step.
        terminated : bool
            If all placements are correct terminated is true.
        truncated : bool
            If a DRC error occurs the epoch gets truncated,
        info : str
            Next device which will be placed.

        """
        
        #get the device which shall be placed
        device_to_place = self._circuit.devices[self._placement_order[0]]
        
        placed_device = device_to_place
        #clip the coordinate to the maximum
        c0 = np.clip(coordinate[0], 0, self._size[0])
        c1 = np.clip(coordinate[1], 0, self._size[1])
        
        coordinate = (c0,c1)
        rotation = (rotation*90)%360

        #place the cell
        device_to_place.cell.place(coordinate, rotation)

        #if magic is used, place the cell also in magic
        if self._use_magic_DRC:
            place_circuit(self._name, self._circuit)
        

        self._placement_order.pop(0) #Device is placed -> remove from the list
        
        #track the placed cells
        self._placed_cells.insert(0, device_to_place.cell)
        
        #print(f"Placed {device_to_place.name}, DRC - Error = {DRC_error}")
        

        ### Evaluate the placement
        reward = 0
        truncated = False
        terminated = False
        info = None
        
        reward = 0
        if len(self._placement_order)==0: #Placing finished
            
            #slide the cells, to get a feasible solution
            cell_slide3(self._placed_cells)
            self._total_placements += 1

            #get the HPWL of the placement
            Total_Wire_Length = self.HPWL()
            
            #get the congestion of the placement
            congestion = self.rudy_congestion()

            reward = -Total_Wire_Length - math.sqrt(congestion)

            if reward > self._best_rew or self._best_rew == 0:
                self._best_rew = reward
                self._best_placement = copy.deepcopy(self._circuit)
                self._best_placement_number = self._total_placements

            self.HPWLs.insert(0, Total_Wire_Length)
                
            if len(self.HPWLs)>1e3:
                self.HPWLs.pop(-1)
            
            terminated = True

        else:
            #get the next device which shall be placed
            device_to_place = self._circuit.devices[self._placement_order[0]]
            device_to_place.cell.place_next()
            
            info = self._placement_order[0]
        
        self._n_step += 1
        
        #get the new observation
        observation = self._get_data()

        return observation, reward, terminated, truncated, info

    def valid_action(self, coordinate, rotation):
        """Check if a action is valid.

            WARNING: Old function, no longer needed!
        """

        #get the device which shall be placed
        device_to_place = self._circuit.devices[self._placement_order[0]]
        
        #clip the coordinate to the maximum
        c0 = np.clip(coordinate[0], 0, self._size[0])
        c1 = np.clip(coordinate[1], 0, self._size[1])
        
        coordinate = (c0,c1)
        rotation = (rotation*90)%360

        #place the cell
        device_to_place.cell.place(coordinate, rotation)

        #check if placed device generated an DRC error
        if self._use_magic_DRC:
            try:
                DRC_error = DRC_magic_check_cell(self._name, device_to_place.cell)>0
            except:
                raise Exception("Magic-DRC not available!")
        else:
            DRC_error = DRC_collidates(device_to_place.cell, self._placed_cells)

        device_to_place.cell.reset_place()
        device_to_place.cell.place_next()

        return not DRC_error

    def init_pygame(self):
        """Initialize pygame for showing the placement process.
        """
        self._pygame_init = True
        # pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
    
    def render(self):
        """Render the actual placement.
        """
        if not self._pygame_init: #If pygame isn't running, make it run
            self.init_pygame()
        
        self._update_screen()

    def stop_pygame(self):
        """ Stop pygame.
        """
        pygame.quit()
        
    def _update_screen(self):
        """Update the screen, to show the actual placement.
        """
        run = True
        # event loop
        #Flip y-axis
        
        #calculate bounding box of all cells
        cells = self._placed_cells
        bound = cells[0].get_bounding_box()
        
        for i in range(1,len(cells)):
            bound_i = cells[i].get_bounding_box()
            
            #get min L and B
            for k in range(2):
                bound[k] = min(bound[k], bound_i[k])
            
            #get max T and R
            for k in range(2,4):
                bound[k] = max(bound[k], bound_i[k])
                
        
        surface = pygame.Surface((4*1024, 4*1024))
        surface.fill(0)
        
        for c in self._placed_cells:
            c.draw(surface)

        surface = pygame.transform.flip(surface, False, True)
        self.screen.fill(0)
        self.screen.blit(pygame.transform.scale(surface, (800, 800)), (0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        if run:
            pygame.display.flip()
        else:
            pygame.quit()
            
        return run

    def end_environment(self):
        """
        Stops the visualization.

        """
        self.stop_pygame()
