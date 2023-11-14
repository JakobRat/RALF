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
    from SchematicCapture.Devices import ThreeTermResistor
    from SchematicCapture.Circuit import Circuit
    from SchematicCapture.Net import Net

from Rules.RoutingRules import RoutingRule
from SchematicCapture.Devices import NTermDevice, SUPPORTED_DEVICES, PrimitiveDevice, ThreeTermResistor
from SchematicCapture.Primitives import PrimitiveDeviceComposition
from PDK.PDK import global_pdk
import Rules.PlacementRules as PlacementRules
from SchematicCapture.Ports import Pin
import itertools

from SchematicCapture.utils import setup_circuit, get_bottom_up_topology

import networkx as nx
import networkx.algorithms.isomorphism as isomorphism

RSTRING_PATHS = ["Circuits/Primitives/RString/RString1.spice",
              "Circuits/Primitives/RString/RString2.spice",
              "Circuits/Primitives/RString/RString3.spice",
              "Circuits/Primitives/RString/RString4.spice"]


def include_RStrings_hierarchical(circ : Circuit):
    """Finds and includes RStrings into a hierarchical circuit.

    Args:
        circ (Circuit): Circuit to include primitives.
    """
    
    #get the topology of the circuit
    topology = get_bottom_up_topology(circ)

    for (t, circ) in topology:
        #find RStrings for each circuit
        #and include them into the circuit
        rStrings = get_RStrings(circ, exclude_nets=[])
        circ.include_primitives(rStrings)

def node_match(n1, n2) -> bool:
    """Checks if two nodes match.
        Nodes match if they have the same label.
        If nodes are devices, they only match if they have the same type.
    Args:
        n1 (dict): Features-dict. of node n1. 
        n2 (dict): Features-dict. of node n2.

    Returns:
        bool: True if two nodes match, otherwise False.
    """
    #check if they have the same label
    if n1['label'] == n2['label']:
        #check if the label is 'Device'.
        if n1['label'] == 'Device':
            #check if both have the same device-type.
            if type(n1['Device']) == type(n2['Device']):
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def edge_match(e1, e2) -> bool:
    """Checks if two edges match.
        Two edges match if they originate from the same terminals.

    Args:
        e1 (dict): Feature-dict. of edge e1.
        e2 (dict): Feature-dict. of edge e2.

    Returns:
        bool: True, if the edges match, otherwise False.
    """
    return e1[0]["Terminal"] == e2[0]["Terminal"]

def get_RStrings(circ : Circuit, exclude_nets : list[Net]= []) -> dict[str, list[RString]]:
    """Find all RStrings in the circuit and make RString devices out of them.

    Args:
        circ (Circuit): Circuit which shall be analyzed.
        exclude_nets (list[Net], optional): Nets which shall be excluded for RString finding (e.g. Vdd, Vss, ...). Defaults to [].

    Returns:
        dict[str, list[RString]]: key: RString, value: list of RString devices.
    """
    
    all_edges = [] #store all edges which form a RString
    
    #iterate over all RString - circuits
    for path in RSTRING_PATHS:
        
        #setup a primitive circuit for the RString
        primitive_circuit = setup_circuit(path, "RString", [], net_rules_file=None)
        
        #get the graphs
        G1 = circ.get_bipartite_graph(exclude_nets=exclude_nets)
        G2 = primitive_circuit.get_bipartite_graph(exclude_nets=["Vl","Vh", "VB"])
        
        #find the RStrings in the circuit
        GM = isomorphism.GraphMatcher(G1, G2, node_match=node_match, edge_match=edge_match)
        
        #get the edges which form a RString
        rstring_edges = []
        #iterate over common edges
        for gm in GM.subgraph_isomorphisms_iter():
            #gm : dict
            # key : Name of matching device in circ
            # value : Name of matching device in primitive_circuit
            #change key and value
            gm2 = {v:k for k,v in gm.items()}

            #add a edge formed by the devices in circ, which form a RString
            rstring_edges.append(tuple(sorted([gm2[k] for k in primitive_circuit.devices])))


        #filter the edges which can't form a RString
        # A edge can't form a RString, if the devices haven't the same length
        # and if they not share a common bulk net
        rstring_edges = list(filter(lambda x: circ.devices[x[0]].parameters["L"]==circ.devices[x[1]].parameters["L"] 
                                    and circ.devices[x[0]].terminal_nets['B']==circ.devices[x[1]].terminal_nets['B'], rstring_edges))

        all_edges.extend(rstring_edges)
    
    #setup a graph which contains all RStrings
    rstring_graph = nx.from_edgelist(all_edges)

    #get a list of all rstrings
    rstrings = []

    #find all rstrings in the graph
    components = [rstring_graph.subgraph(c).copy() for c in nx.connected_components(rstring_graph)]
    for comp in components:
        #traverse the nodes starting by a node with only one edge (=start of the RString)
        starting_nodes = list(filter(lambda x : x[1]==1, tuple(comp.degree)))
        T = nx.dfs_tree(comp, source=starting_nodes[0][0])
        rstrings.append(list(T))

    rstring_devices = []
    #generate the rstrings
    for rstring in rstrings:
        devices = [circ.devices[dev] for dev in rstring]
        new_rstring = RString(devices=devices)
        rstring_devices.append(new_rstring)
    
    return {"RString" : rstring_devices}

class RString(PrimitiveDeviceComposition):
    """Class to store a RString. 
        A RString is formed by resistors which are in series.
        
        T2-----T3       T6
        |       |       |
        |       |       |
        R1      R2      R3
        |       |       |
        |       |       |
        T1      T4-----T5
    """

    #setup a counter, to provide unique id's for RStrings.
    id_iter = itertools.count()

    def __init__(self, devices : list[ThreeTermResistor], use_dummies = True):
        """Setup a RString.

        Args:
            devices (list[ThreeTermResistor]): Resistors which form a RString, ordered according their connection.
                                                E.g. If R1<->R2<->R3 form a RString they list must be [R1, R2, R3]!

            use_dummies (bool, optional): Define if the RString shall use dummies. Defaults to True.

        Raises:
            ValueError: If the devices aren't ThreeTermResistor's
            ValueError: If the devices don't share a common model.
            ValueError: If the devices haven't the same L. 
            ValueError: If the devices haven't the same W.
            ValueError: If the devices multiplier is != 1.
        """
        self._devices = devices

        for device in self._devices:
            if type(device) != ThreeTermResistor:
                raise ValueError("RString with wrong device class detected!")
        
        for i in range(len(self._devices)-1):
            for j in range(1,len(self._devices)):
                if self._devices[i].model != self._devices[j].model:
                    raise ValueError("RString with unequal models detected!")
                
        model = self._devices[0].model
        
        for i in range(len(self._devices)-1):
            for j in range(1,len(self._devices)):
                if self._devices[i].parameters['L'] != self._devices[j].parameters['L']:
                    raise ValueError("RString with unequal L detected!")
        
        for i in range(len(self._devices)-1):
            for j in range(1,len(self._devices)):
                if self._devices[i].parameters['W'] != self._devices[j].parameters['W']:
                    raise ValueError("RString with unequal W detected!")
        
        for i in range(len(self._devices)-1):
            for j in range(1,len(self._devices)):
                if self._devices[i].parameters['m'] != 1:
                    raise ValueError("RString with m!=1 detected!")
        

        #get the bulk-net
        bulk_net = self._devices[0].terminal_nets['B']

        #get the ordered nets
        #this is needed to generate
        #a meander formed routing

        device : ThreeTermResistor
        device_net_map = {}
        
        #iterate over the devices
        for device, i in zip(self._devices, range(len(self._devices))):
            dev_nets = []
            #get the nets of the device, except the bulk-net
            for (term_name, net) in device.terminal_nets.items():
                if term_name != "B":
                    dev_nets.append(net)
            
            #if already a device were traversed
            if i>0:
                #get the last device
                last_device = self._devices[i-1]
                #get the net order of the last device
                last_net_order = device_net_map[last_device]

                #find the common net of the connected R's
                # and order them such that
                #        dev_nets[0] ------ dev_nets[1]
                #                                |
                #  last_net_order[0] ------ last_net_order[1]
                #
                # or
                #
                #        dev_nets[0] ------ dev_nets[1]
                #             |                   
                #  last_net_order[0] ------ last_net_order[1]

                if dev_nets[0] == last_net_order[1]: #if the first and second net are common, change the order
                    dev_nets[0], dev_nets[1] = dev_nets[1], dev_nets[0]
                elif dev_nets[1] == last_net_order[0]: #if the second and first net are common, change the order
                    dev_nets[0], dev_nets[1] = dev_nets[1], dev_nets[0]
            
            device_net_map[device] = dev_nets
        
        #setup the terminal nets
        #   T2-----T3       T6
        #   |       |       |
        #   |       |       |
        #   R1      R2      R3
        #   |       |       |
        #   |       |       |
        #   T1      T4-----T5
        # 
        # device_net_map = {'R1' : [net1, net2],
        #                   'R2' : [net3, net2],
        #                   'R3' : [net3, net4]}
        # Terminal nets :   T1 : net1
        #                   T2 : net2
        #                   T3 : net2
        #                   T4 : net3
        #                   T5 : net3
        #                   T6 : net4
        #  terminal_nets = [net1, net2, net2, net3, net3, net4]

        terminal_nets = []
        #iterate over the devices
        for device, i in zip(self._devices, range(len(self._devices))):
            assert len(device_net_map[device])==2
            
            nets = device_net_map[device]
            #change the order of each 2nd resistor
            #to match the terminal order
            if i%2:
                terminal_nets.append(nets[1])
                terminal_nets.append(nets[0])
            else:
                terminal_nets.extend(nets)

        #add the bulk as terminal net
        terminal_nets.append(bulk_net)

        #Setup for each R a terminal + the terminal of the bulk
        N_Terminals = 2*len(devices)+1

        #sanity check
        assert len(terminal_nets)==N_Terminals

        #get the device length
        L = self._devices[0].parameters["L"]
        
        #set the multiplier
        m = len(self._devices)
        
        self._dummies = use_dummies

        if use_dummies:
            m += 2 #add dummies
            # add a terminals for the bulk-connection 
            # of the dummies
            terminal_nets.insert(0, bulk_net)
            terminal_nets.append(bulk_net)
            N_Terminals += 2

        self._id = next(RString.id_iter) #get a unique id for a RString
        
        #setup a spice description for the RString.
        spice_description = f"XRSTR_{str(self._id)} {' '.join([net.name for net in terminal_nets])} L={L} m={m}"

        super().__init__(devices, spice_description, N_Terminals, name_suffix=self._devices[0]._name_suffix, use_dummies=use_dummies)

        self._model = model
        self.add_feature("model", SUPPORTED_DEVICES[self._model])
        
        self._parameters = {"L" : None, "m" : None, "W" : self._devices[0].parameters['W']}
        self._set_params()
        
        self.add_feature("L", self._parameters["L"])
        self.add_feature("W", self._parameters["W"])
        self.add_feature("m", self._parameters["m"])
        self.add_feature("nf", 0)

    @property
    def devices(self):
        return self._devices
    
    @property
    def uses_dummies(self) -> bool:
        """
        Check if the RString uses dummies.
        
        Returns:
            bool: True if the device uses dummies, otherwise False.
        """
        return self._dummies
    
    def _setup_terminals(self):
        #setup a terminal-pair for each resistor
        terminals = []
        for i in range(self._N_Terminals-1):
            terminals.append(f"T{str(i)}")
        
        #add the bulk terminal
        terminals.append("B")
        
        #setup device-pins for the terminals
        for terminal in terminals:
            self._terminals[terminal] = Pin(terminal, self)

    def _gen_placement_rules(self):        
        super()._gen_placement_rules()
    
    def _generate_routing_rules(self) -> list[RoutingRule]:
        return super()._generate_routing_rules()