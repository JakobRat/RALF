# ========================================================================
#
# Script to generate a placement for a circuit, by using simulated annealing.
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

import argparse
import faulthandler
faulthandler.enable()

from SchematicCapture.utils import setup_circuit, include_primitives_hierarchical
from Magic.utils import instantiate_circuit, add_cells
from rectangle_packing_placement.utils import do_bottom_up_placement
from SchematicCapture.RString import include_RStrings_hierarchical
from Magic.MagicDie import MagicDie

from rectangle_packing_placement.utils import do_bottom_up_placement

import logging
from logging.handlers import RotatingFileHandler
import pickle

#global variables to control the placement 
USE_LOGGER = False                  #If True, debug information will be logged under "Logs/{CIRCUIT_NAME}_placement.log".
INSTANTIATE_CELLS_IN_MAGIC = True   #If True, the devices cell-view will be instantiated in Magic
SIM_ANNEAL_MIN = 0.1                #Maximum spend time for simulated annealing (per placement) when N_PLACEMENT=None
SIM_ANNEAL_STEPS = 200              #Number of steps done by the simulated annealing to find Tmax and Tmin (per placement)
N_PLACEMENTS = 50000               #Number of placements done by the simulated annealing (per placement)
CIRCUIT_FILE = "Circuits/Examples/InvAmp.spice"    #Input spice-netlist
CIRCUIT_NAME = "InvAmp_RPP"            #Name of the circuit
NET_RULES_FILE = "NetRules/net_rules_InvAmp.json"               #Net-rules definition file
DEF_FILE = None                     #Def file of the circuit
SHOW_STATS = True                   #Show statistics of the placement

def main():

    if USE_LOGGER:
        #Setup a logger
        logHandler = RotatingFileHandler(filename=f"Logs/{CIRCUIT_NAME}_placement.log", mode='w', maxBytes=100e3, backupCount=1, encoding='utf-8')
        logHandler.setLevel(logging.DEBUG)
        logging.basicConfig(handlers=[logHandler], level=logging.DEBUG, format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
    
    #setup the circuit
    C = setup_circuit(CIRCUIT_FILE, CIRCUIT_NAME, [], net_rules_file=NET_RULES_FILE)
    
    #include primitive compositions into the circuit
    include_primitives_hierarchical(C)
    include_RStrings_hierarchical(C)

    #instantiate the circuit cells in magic
    if INSTANTIATE_CELLS_IN_MAGIC:
        instantiate_circuit(C,"Magic/Devices")

    #add the cells to the devices
    add_cells(C, "Magic/Devices")

    #define a die for the circuit
    die = MagicDie(circuit=C, def_file=DEF_FILE)

    #do the placement per simulated annealing
    #and store images of the placement under "Images"
    do_bottom_up_placement(die, fig_path="Images", simanneal_minutes=SIM_ANNEAL_MIN, simanneal_steps=SIM_ANNEAL_STEPS,
                           n_placements=N_PLACEMENTS, show_stats=SHOW_STATS)

    #save the placed circuit
    file = open(f"PlacementCircuits/{CIRCUIT_NAME}_placement.pkl", 'wb')
    pickle.dump(die, file)
    file.close()
    
if __name__=='__main__':
    main()
