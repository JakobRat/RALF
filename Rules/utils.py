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
    from SchematicCapture.Circuit import Circuit
    from SchematicCapture.Net import Net

import json
import os
import importlib


def generate_net_rules_from_file(file : str, circuit : Circuit):
    """Generate rules for nets, from a file.

    Args:
        file (str): Name of the file.
        circuit (Circuit): Circuit, into which the rules shall be inserted.

    Raises:
        NotImplementedError: If a rule which isn't implemented gets called.
        ValueError: If no net is specified for a net-rule.
        FileNotFoundError: If the rule-file can't be found.
    """
    if os.path.isfile(file) and file.endswith(".json"):
        #open the file and read in the json data
        file = open(file)
        data = json.load(file)
        file.close()

        #import the net rules
        module = importlib.import_module("Rules.NetRules")
        rule : str
        args : dict

        for (rule, args) in data:
            #try to get the rule
            try:
                class_ = getattr(module, rule)
            except:
                raise NotImplementedError(f"Rule {rule} isn't a valid net-rule!")
            
            if 'net' in args:
                #get the net of the rule
                net = get_net_from_str(circuit, args['net'])
                args['net'] = net
            elif 'nets' in args:
                #get the nets of the rule
                nets = []
                for net in args['nets']:
                    nets.append(get_net_from_str(circuit, net))
                
                args['nets'] = nets
            else:
                raise ValueError("No net specified for net-rule!")
            
            #setup a rule, and add it to the net.
            rule = class_(**args) #instantiate the rule
            
    else:
        raise FileNotFoundError
    
def get_net_from_str(circuit : Circuit, net_name : str) -> Net:
    """Get the net defined by net_name.

    Args:
        circuit (Circuit): Top-Circuit 
        net_name (str): Name of the net, beginning with the sub-device identifier.
                        E.g. a valid net_name in a sub-device is x1.Vdd

    Raises:
        ValueError: If the sub-device isn't in the circuit.
        ValueError: If the sub-device has no sub-circuit.
        ValueError: If the net can't be found.
    
    Returns:
        Net: Net instance.
    """
    net : Net
    name_splitted = net_name.split('.') #split the name to get the right circuit
    sub_circ = circuit
    if len(name_splitted)>1: #net is a subnet
        for sub_dev_name in name_splitted[:-1]:
            try:
                #get the sub-device in which the searched net is located 
                sub_dev = sub_circ.devices[sub_dev_name]
            except:
                raise ValueError(f"SubDevice {sub_dev_name} isn't in circuit {sub_circ.name}!")
            try:
                #get the circuit of the sub-device
                sub_circ = sub_dev._circuit
            except:
                raise ValueError(f"Device {sub_dev} has no circuit!")
    
    try:
        net = sub_circ._nets[name_splitted[-1]]
    except:
        raise ValueError(f"Net {name_splitted[-1]} isn't in circuit {sub_circ.name}!")

    return net