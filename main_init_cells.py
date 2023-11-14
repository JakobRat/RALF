from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Magic.MagicDie import MagicDie


from Magic.utils import instantiate_circuit
import pickle

CIRCUIT_NAME = "DiffAmp"  #Name of the circuit

#load the placed circuit 
file = open(f"PlacementCircuits/{CIRCUIT_NAME}_placement.pkl", 'rb')
die : MagicDie
die = pickle.load(file)
file.close()

#get the placed circuit
circuit = die.circuit

#instantiate the circuit cells in magic
instantiate_circuit(circuit,"Magic/Devices")

