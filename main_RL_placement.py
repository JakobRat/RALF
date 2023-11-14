import faulthandler
faulthandler.enable()

from SchematicCapture.utils import setup_circuit, include_primitives_hierarchical
from Magic.utils import instantiate_circuit, add_cells
from Environment.utils import do_bottom_up_placement
from SchematicCapture.RString import include_RStrings_hierarchical
from Magic.MagicDie import MagicDie
import pickle

import logging
from logging.handlers import RotatingFileHandler

#global variables to control the placement 
USE_LOGGER = False                  #If True, debug information will be logged under "Logs/{CIRCUIT_NAME}_placement.log".
INSTANTIATE_CELLS_IN_MAGIC = True   #If True, the devices cell-view will be instantiated in Magic
N_ITERATIONS = 1                 #Number of RL-training iterations
CIRCUIT_FILE = "Circuits/Example/DiffAmp.spice"    #Input spice-netlist
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

    #do the placement by training a RL-agent
    do_bottom_up_placement(C, N_ITERATIONS, use_weights=False)

    #save the placed circuit
    file = open(f"PlacementCircuits/{CIRCUIT_NAME}_placement.pkl", 'wb')
    pickle.dump(die, file)
    file.close()
    

if __name__ == '__main__':
    main()
