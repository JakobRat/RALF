# ========================================================================
#
# Collection of useful functions for circuit instantiation and manipulation. 
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

from SchematicCapture.NGSpiceParser import Parser
from SchematicCapture.Netlist import Netlist
from SchematicCapture.Circuit import Circuit, SubCircuit
from SchematicCapture.Devices import SubDevice, PrimitiveDevice

import SchematicCapture.Primitives as Primitives
from SchematicCapture.Primitives import SUPPORTED_PRIMITIVES, PrimitiveDeviceComposition
from Rules.utils import generate_net_rules_from_file


from networkx.algorithms import isomorphism
from collections import OrderedDict

import logging

import os

logger = logging.getLogger(__name__)

def setup_circuit(ngspice_netlist : str, name = "", exclude_nets : list[str] = [], net_rules_file : str = None) -> Circuit:
    """Setup a circuit.

    Args:
        ngspice_netlist (str): Spice file containing the netlist of the circuit.
        name (str, optional): Name of the circuit. Defaults to "".
        exclude_nets (list[str], optional): Nets (specified by names) to be excluded by building the circuits-graph. Defaults to [].
        net_rules_file (str, optional): Json file, which describes the net-rules of the circuit. Defaults to [].
    Returns:
        Circuit: Builded circuit.
    """

    logger.info(f"Setting up circuit {name} from netlist-file {ngspice_netlist}.")
    logger.info(f"Excluding nets {exclude_nets}, and using rules {net_rules_file}.")

    #parse the netlist
    logger.info(f"Parsing netlist.")
    P = Parser(ngspice_netlist) 
    raw_netlist = P.get_netlist()
    
    #build the netlist
    logger.info(f"Building netlist.")
    N = Netlist(raw_netlist)
    
    #build the circuit
    logger.info(f"Building circuit.")
    C = Circuit(N)

    #set the name of the circuit
    C.set_name(name)

    #generate a graph of the circuit
    C.generate_circuit_graph(exclude_nets)

    #include the net-rules into the circuit
    if net_rules_file:
        logger.info(f"Including net-rules.")
        generate_net_rules_from_file(net_rules_file, C)
    
    logger.info(f"Top-Circuit: {C} created.")
    logger.info(f"Successfully created circuit {C}.")

    return C

def get_top_down_topology(circ : Circuit) -> list[tuple[int, Circuit]]:
    """Get the topology of the circuit <circ> in a top-down fashion.

    Args:
        circ (Circuit): Circuit whose topology is to be identified.

    Returns:
        list[(int, Circuit)]: List of tuples, containing the topological layer number and the according circuit.
    
    Example:
        Top-level-circuit DBuf:    
                            x1 net1 net2 Vdd Vss inv
                            x2 net2 net3 Vdd Vss inv
                            x3 net3 net4 Vdd Vss buf
        
        Sub-circuit inv:    .subckt inv in out Vdd Vss
                            XM1 out in Vss Vss nfet
                            XM2 out in Vdd Vdd pfet
                            .ends
        
        Sub-circuit buf:    .subckt buf in out Vdd Vss
                            x1 in out1 Vdd Vss inv
                            x2 out1 out Vdd Vss inv
                            .ends
        Topology:                               Layer:
                                DBuf                    1
                               /  |  \
                              /   |   \
                            x1   x2    x3               2
                                      /  \
                                     /    \
                                  x1_x3  x2_x3          3

        Resulting list: [(1, Circuit(DBuf)), (2, Circuit(x1)), (2, Circuit(x2)), (2, Circuit(x3)), (3, Circuit(x1_x3)), (3, Circuit(x2_x3))] 
    """
    topology = []

    #add the topological layer of the circuit to the list
    topology.append((circ.topology_layer, circ))

    #check if the circuit contains sub-circuits
    for d in list(circ.devices.values()):
        if type(d) is SubDevice:
            #if the circuit contains a sub-device
            # -> the device contains a sub-circuit
            # -> add the topology of the circuit to the topology list
            topology.extend(get_top_down_topology(d._circuit))

    return topology

def get_bottom_up_topology(circ : Circuit) -> list[tuple[int, Circuit]]:
    """Get the topology of the circuit <circ> in a bottom-up fashion.

    Args:
        circ (Circuit): Circuit whose topology is to be identified.

    Returns:
        list[(int, Circuit)]: List of tuples, containing the topological layer number and the according circuit, 
                                starting with the lowest layer.
    
    Example:
        Top-level-circuit DBuf:    
                            x1 net1 net2 Vdd Vss inv
                            x2 net2 net3 Vdd Vss inv
                            x3 net3 net4 Vdd Vss buf
        
        Sub-circuit inv:    .subckt inv in out Vdd Vss
                            XM1 out in Vss Vss nfet
                            XM2 out in Vdd Vdd pfet
                            .ends
        
        Sub-circuit buf:    .subckt buf in out Vdd Vss
                            x1 in out1 Vdd Vss inv
                            x2 out1 out Vdd Vss inv
                            .ends
        Topology:                               Layer:
                                DBuf                    1
                               /  |  \
                              /   |   \
                            x1   x2    x3               2
                                      /  \
                                     /    \
                                  x1_x3  x2_x3          3

        Resulting list: [(3, Circuit(x1_x3)), (3, Circuit(x2_x3)), (2, Circuit(x1)), (2, Circuit(x2)), (2, Circuit(x3)), (1, Circuit(DBuf))] 
    """
    #get the top-down topology
    top = get_top_down_topology(circ)
    #sort the list according the topology in ascending order
    top.sort(key=lambda x : x[0])
    #reverse the list to get the bottom-up topology
    top.reverse()
    return top  
    
def node_match(n1, n2) -> bool:
    """Checks if two nodes match. (For graph-isomorphism.)
        Nodes match if they have the same label.
        If nodes are devices, they only match if they have the same type.
    Args:
        n1 (dict): Features-dict. of node n1. 
        n2 (dict): Features-dict. of node n2.

    Returns:
        bool: True if two nodes match, otherwise False.
    """
    if n1['label'] == n2['label']:
        if n1['label'] == 'Device':
            if type(n1['Device']) == type(n2['Device']):
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def edge_match(e1, e2) -> bool:
    """Checks if two edges match. (For graph-isomorphism.)
        Two edges match if they originate from the same terminals.

    Args:
        e1 (dict): Feature-dict. of edge e1.
        e2 (dict): Feature-dict. of edge e2.

    Returns:
        bool: True, if they match, otherwise False.
    """
    return e1[0]["Terminal"] == e2[0]["Terminal"]

def get_primitives(circ : Circuit) -> dict[str, list[PrimitiveDeviceComposition]]:
    """Get all supported primitives found in circuit <circ>.

    Args:
        circ (Circuit): Circuit to find the primitive compositions.

    Returns:
        dict[str, list[PrimitiveDeviceComposition]]: key : Primitive type, value : List of PrimitiveDeviceComposition - devices
    """

    #setup a dict, for the primitive device compositions
    primitives = {}
    for (prim, path) in SUPPORTED_PRIMITIVES.items():
        #store all found primitives of the primitive-composition class
        all_primitives = set()
        for file in os.listdir(path):
            if file.endswith('.spice'):
                #setup the circuit of the template primitive device composition
                primitive_circuit = setup_circuit(path+file, prim)

                #get the graphs
                G1 = circ.get_bipartite_graph()
                G2 = primitive_circuit.get_bipartite_graph()

                #find the primitive in the circuit
                GM = isomorphism.GraphMatcher(G1, G2, node_match=node_match, edge_match=edge_match)

                #get the devices which form a primitive device composition
                prims = []
                for gm in GM.subgraph_isomorphisms_iter():
                    #gm : dict
                    # key : Name of matching device in circ
                    # value : Name of matching device in primitive_circuit
                    #change key and value
                    gm2 = {v:k for k,v in gm.items()}

                    #add the devices of the circuit, which form the primitive to the prims list
                    prims.append(tuple(sorted([gm2[k] for k in primitive_circuit.devices])))

                #delete duplicates
                # e.g. M1 and M2 of a DiffPair form a primitive-device composition
                # since the devices are symmetric, the algorithm finds the composition twice
                prims = list(OrderedDict.fromkeys(prims))

                all_primitives.update(prims)

        #setup a list for the primitives
        primitives[prim] = []
        
        #generate new devices from the primitives
        for d in all_primitives:
            #get the device instances
            devices = [circ.devices[dev] for dev in d]
            #get the class of the primitive device composition
            gen_prim = getattr(Primitives, prim)
            new_prim = gen_prim(devices)
            primitives[prim].append(new_prim)

    return primitives

def include_primitives_hierarchical(circ : Circuit):
    """Finds and includes primitive device compositions into a hierarchical circuit.

    Args:
        circ (Circuit): Circuit to include primitives.
    """
    
    #get the topology of the circuit
    topology = get_bottom_up_topology(circ)

    for (t, circ) in topology:
        #find primitive device compositions for each circuit
        #and include them into the circuit
        primitives = get_primitives(circ)
        circ.include_primitives(primitives)

def get_all_primitive_devices(circuit : Circuit) -> list[PrimitiveDevice]:
    """Get a list of all primitive devices of the circuit.

    Args:
        circuit (Circuit): Circuit to be analyzed.

    Returns:
        list[PrimitiveDevice]: List of all primitive devices of the circuit.
    """
    #setup a list for the primitive devices
    devices = []
    for d in circuit.devices.values():
        if isinstance(d, SubDevice):
            #if the device contains a sub-circuit
            #get the primitive devices of the sub-circuit
            sub_devices = get_all_primitive_devices(d._circuit)
            for sub_d in sub_devices:
                #add the primitive devices of the sub-device
                if isinstance(sub_d, PrimitiveDevice):
                    devices.append(sub_d)
        else:
            #add the primitive device to the devices
            if isinstance(d, PrimitiveDevice):
                devices.append(d)

    return devices