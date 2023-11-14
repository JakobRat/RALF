from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SchematicCapture.Circuit import Circuit
    from Magic.MagicDie import MagicDie 

import faulthandler
faulthandler.enable()

import pickle
from Routing_v2.Obstacles import DieObstacles
from Routing_v2.utils import route

import time
import matplotlib.pyplot as plt

CIRCUIT_NAME = "DiffAmp"            #Name of the circuit
PLAN_WIRES = True                   #If True, before detail-routing, wire-planning (global-routing) will be performed
N_PLANNING_ITERATIONS = 20          #Number of wire-planning iterations
GCELL_LENGTH = 150                  #Length of a wire-planning cell (in units of lambda)
LAYERS = ['m1','m2']                #Layers which will be used for wire-planning
SHOW_STATS = True                   #If True, statistics of the routing will be printed
DESTINATION_PATH = 'Magic/Routing/' #Destination path of the routing file


#load the placed circuit 
file = open(f"PlacementCircuits/{CIRCUIT_NAME}_placement.pkl", 'rb')
die : MagicDie
die = pickle.load(file)
file.close()

#setup obstacles from the die
die_obstacles = DieObstacles(die)

#get the placed circuit
circuit = die.circuit

#route the circuit
route(circuit=circuit, routing_name=CIRCUIT_NAME, plan_wires=PLAN_WIRES, 
      planning_iterations=N_PLANNING_ITERATIONS, gcell_length=GCELL_LENGTH, use_layers=LAYERS,
      destination_path=DESTINATION_PATH, show_stats=SHOW_STATS)