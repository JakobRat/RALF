# ========================================================================
#
#   Script to evaluate the circuit capturing process.
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

from SchematicCapture.utils import setup_circuit, include_primitives_hierarchical, get_top_down_topology
from SchematicCapture.RString import include_RStrings_hierarchical

import matplotlib.pyplot as plt
import networkx as nx


#global variables to control the placement 
CIRCUIT_FILE = "Circuits/Examples/CCLatch.spice"    #Input spice-netlist
CIRCUIT_NAME = "CCLatch"            #Name of the circuit
NET_RULES_FILE = None#"NetRules/net_rules.json"               #Net-rules definition file


#setup the circuit
C = setup_circuit(CIRCUIT_FILE, CIRCUIT_NAME, [], net_rules_file=NET_RULES_FILE)

topology = get_top_down_topology(C)

#topology = [(1, C)]
circuit_graphs = [(c, c.get_bipartite_graph()) for t,c in topology]

#include primitive compositions into the circuit
include_primitives_hierarchical(C)
include_RStrings_hierarchical(C)

prim_graphs = [(c, c.get_bipartite_graph()) for t,c in topology]

mygreen = (80/255,160/255,80/255)
myblue = (80/255,80/255,160/255)

for (circuit, graph) in circuit_graphs:
    node_colors = []
    for node_name, node in graph.nodes.items():
        if 'Device' in node:
            node_colors.append(myblue)
        else:
            node_colors.append(mygreen)

    top = nx.bipartite.sets(graph)[0]
    pos = nx.bipartite_layout(graph, top, align="horizontal", scale=-0.5)
    nx.draw(graph, pos, with_labels=True, node_size=1000, node_color=node_colors, linewidths=5, font_size=10)
    plt.savefig(f"{circuit.name}_circ_graph.svg")
    plt.show()

for (circuit, graph) in prim_graphs:
    node_colors = []
    for node_name, node in graph.nodes.items():
        if 'Device' in node:
            node_colors.append(myblue)
        else:
            node_colors.append(mygreen)

    top = nx.bipartite.sets(graph)[0]
    pos = nx.bipartite_layout(graph, top, align="horizontal", scale=-0.5)
    nx.draw(graph, pos, with_labels=True, node_size=1000, node_color=node_colors, linewidths=5, font_size=10)
    plt.savefig(f"{circuit.name}_prim_graph.svg")
    plt.show()

