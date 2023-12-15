# ========================================================================
#
#   Script to calculate statistics of a placement.
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
    from Magic.MagicDie import MagicDie
    from SchematicCapture.Circuit import Circuit

import pickle
from Routing_v2.utils import  get_nets_and_pins
from Environment.RUDY import RUDY
from SchematicCapture.Net import SubNet
from PDK.PDK import global_pdk
from SchematicCapture.Devices import SubDevice
from prettytable import PrettyTable

###################################################################


CIRCUIT_NAME = "InvAmp_RPP"  #Name of the circuit


###################################################################
#load the placed circuit 
file = open(f"PlacementCircuits/{CIRCUIT_NAME}_placement.pkl", 'rb')
die : MagicDie
die = pickle.load(file)
file.close()

#get the placed circuit
circuit = die.circuit

#get all nets of the circuit - including subnets
nets_and_pins = get_nets_and_pins(circuit)

#setup RUDY for congestion estimation
rudy = RUDY(global_pdk)

#setup a dict to store the HPWLs
HPWL = {}

#get the HPWLs
for net in nets_and_pins.keys():
    
    rudy.add_net(net)

    if type(net)==SubNet:
        net_name = net.name + '_' + net.parent_device.name_suffix
    else:
        net_name = net.name
    
    HPWL[net_name] = net.HPWL()

#get the congestion
congestion = round(rudy.congestion(),2)

#calculate the bounding box of the placement
bounding_box = [float('inf'),float('inf'),-float('inf'),-float('inf')]
for device in circuit.devices.values():
    device_bound = device.cell.get_bounding_box()
    bounding_box[0] = min(bounding_box[0],device_bound[0])
    bounding_box[1] = min(bounding_box[1],device_bound[1])
    bounding_box[2] = max(bounding_box[2],device_bound[2])
    bounding_box[3] = max(bounding_box[3],device_bound[3])
    
w = round((bounding_box[2]-bounding_box[0])*global_pdk.scale_factor/1e3,2)
h = round((bounding_box[3]-bounding_box[1])*global_pdk.scale_factor/1e3,2)

def get_number_of_cells(circuit : Circuit):
    #get the total number of cells of an circuit
    n_cells = 0
    #iterate over the devices
    for device in circuit.devices.values():
        if type(device)==SubDevice:
            #if device is a SubDevice -> find the number of cells for the subcircuit
            subcircuit = device._circuit
            n_cells += get_number_of_cells(subcircuit)
        else:
            #device is primitive -> has a cell
            n_cells += 1

    return n_cells

#calculate the total HPWL and setup a table
table = PrettyTable(['Parameter', 'Value', 'Unit'])
total_HPWL = 0
for net, hpwl in HPWL.items():
    table.add_row([f"HPWL({net})", round(hpwl*global_pdk.scale_factor/1e3,2), 'um'])
    total_HPWL += hpwl

#add the data
table.add_row(['Total HPWL', round(total_HPWL*global_pdk.scale_factor/1e3,2), 'um'])
table.add_row(['Congestion', congestion, '-'])
table.add_row(['Width', w, 'um'])
table.add_row(['Height', h, 'um'])
table.add_row(['Area', round(w*h,2), 'um2'])
table.add_row(['#Cells', get_number_of_cells(circuit), '-'])

print(table)

#log the table
try:
    print(table, file=open(f'Logs/Stats/{circuit.name}_placement_stats.txt','w'))
except:
    print(table, file=open(f'Logs/Stats/{circuit.name}_placement_stats.txt','a'))
