# ========================================================================
#
#   Script to place and route a circuit in Magic.
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

import pickle
from Magic.utils import place_circuit, instantiate_circuit
import os

###############################################################

CIRCUIT_NAME = "DiffAmp"  #Name of the circuit

###############################################################

#load the placed circuit 
file = open(f"PlacementCircuits/{CIRCUIT_NAME}_placement.pkl", 'rb')
die : MagicDie
die = pickle.load(file)
file.close()

#get the placed circuit
circuit = die.circuit

#instantiate the circuit-devices in Magic
instantiate_circuit(circuit, path='Magic/Devices')

#place the circuit
place_circuit(CIRCUIT_NAME, circuit, debug=False)

#open the routing file
if os.path.isfile(f'Magic/Routing/{CIRCUIT_NAME}_routing.tcl'):
    routing_file = open(f'Magic/Routing/{CIRCUIT_NAME}_routing.tcl', 'r')
    commands = [line for line in routing_file]
    routing_file.close()
    commands.insert(0, f"load Magic/Placement/{CIRCUIT_NAME}.mag\n")
    routing_file = open(f'Magic/Routing/{CIRCUIT_NAME}_routing_temp.tcl', 'w')
    for l in commands:
        routing_file.write(l)
    routing_file.close()
else:
    raise FileNotFoundError("Routing file not found!")

os.system(f'magic -nowrapper Magic/Routing/{CIRCUIT_NAME}_routing_temp.tcl')
os.remove(f'Magic/Routing/{CIRCUIT_NAME}_routing_temp.tcl')
