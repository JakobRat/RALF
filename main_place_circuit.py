from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Magic.MagicDie import MagicDie

import pickle
from Magic.utils import place_circuit


CIRCUIT_NAME = "DiffAmp"  #Name of the circuit

#load the placed circuit 
file = open(f"PlacementCircuits/{CIRCUIT_NAME}_placement.pkl", 'rb')
die : MagicDie
die = pickle.load(file)
file.close()

#get the placed circuit
circuit = die.circuit

#place the circuit
place_circuit(CIRCUIT_NAME, circuit, debug=False)

