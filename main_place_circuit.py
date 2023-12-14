# ========================================================================
#
#   Script to place a already placed circuit in Magic.
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


CIRCUIT_NAME = "InvAmp_RPP"  #Name of the circuit

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

