import argparse
import faulthandler
faulthandler.enable()

from SchematicCapture.utils import setup_circuit, get_primitives, get_bottom_up_topology, include_primitives_hierarchical
from Magic.utils import instantiate_circuit, add_cells, place_circuit
from Environment.utils import do_bottom_up_placement
from SchematicCapture.RString import get_RStrings, include_RStrings_hierarchical
from Magic.MagicDie import MagicDie

from rectangle_packing_solver.utils import do_bottom_up_placement

import logging
from logging.handlers import RotatingFileHandler
import pickle

#global variables to control the placement 
USE_LOGGER = False                  #If True, debug information will be logged under "Logs/{CIRCUIT_NAME}_placement.log".
INSTANTIATE_CELLS_IN_MAGIC = True   #If True, the devices cell-view will be instantiated in Magic
SIM_ANNEAL_MIN = 0.1                #Maximum spend time for simulated annealing (per placement)
CIRCUIT_FILE = "Circuits/DiffAmp3.spice"    #Input spice-netlist
CIRCUIT_NAME = "DiffAmp"            #Name of the circuit
NET_RULES_FILE = None               #Net-rules definition file
DEF_FILE = None                     #Def file of the circuit

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
    do_bottom_up_placement(die, fig_path="Images", simanneal_minutes=SIM_ANNEAL_MIN)

    #save the placed circuit
    file = open(f"PlacementCircuits/{CIRCUIT_NAME}_placement.pkl", 'wb')
    pickle.dump(die, file)
    file.close()
    
if __name__=='__main__':
    main()
