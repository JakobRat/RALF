from SchematicCapture.utils import setup_circuit, include_primitives_hierarchical, get_top_down_topology
from Magic.utils import instantiate_circuit, add_cells
from Environment.utils import do_bottom_up_placement
from SchematicCapture.RString import include_RStrings_hierarchical
from SchematicCapture.Devices import Device

import matplotlib.pyplot as plt
import networkx as nx

import tikzplotlib

#global variables to control the placement 
CIRCUIT_FILE = "Circuits/Examples/InvAmp.spice"    #Input spice-netlist
CIRCUIT_NAME = "InvAmp"            #Name of the circuit
NET_RULES_FILE = None#"NetRules/net_rules.json"               #Net-rules definition file


#setup the circuit
C = setup_circuit(CIRCUIT_FILE, CIRCUIT_NAME, [], net_rules_file=NET_RULES_FILE)

#topology = get_top_down_topology(C)

topology = [(1, C)]
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

