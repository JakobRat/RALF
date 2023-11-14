from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SchematicCapture.Circuit import Circuit
    from SchematicCapture.Net import Net
    from SchematicCapture.Ports import Pin
    from matplotlib.pyplot import axes
from SchematicCapture.Devices import SubDevice, NTermDevice
from Routing_v2.WirePlanning import WirePlanner
from Routing_v2.Route import Route
from Routing_v2.PlanningGraph import PlanningGraph
from PDK.PDK import global_pdk

from prettytable import PrettyTable

import sys
import os

def get_nets_and_pins(circuit : Circuit) -> dict[Net, list[Pin]]:
    """Get all pins connected to a net. 

    Args:
        circuit (Circuit): Circuit for which all nets should be analyzed.

    Returns:
        dict: key: Net, to which the pins belong. value: List of devices terminals.
    """
    nets = {}
    #iterate over each device of the circuit
    for d in circuit.devices.values():
        if isinstance(d, SubDevice):
            #if the device is a sub-device
            # -> get all nets and pins of the devices sub-circuit
            sub_nets = get_nets_and_pins(d._circuit)
            for (k,v) in sub_nets.items():
                if k.parent_net:
                    #if the net has a parent net, add the pins to the parent net
                    add_to_dict(k.parent_net, v, nets)
                else:
                    #add pins to the net
                    add_to_dict(k, v, nets)
        else:
            assert isinstance(d, NTermDevice)
            for net in d.nets.values():
                add_to_dict(net, d.get_terminals_connected_to_net(net), nets)

    return nets

def add_to_dict(net, d, nets):
    if net in nets:
        nets[net].extend(d)
    else:
        nets[net] = d


def route(circuit : Circuit, routing_name : str, plan_wires : bool = True, planning_iterations : int = 20, 
          gcell_length : int = 150, use_layers : list[str] = ['m1', 'm2'], destination_path : str = 'Magic/Routing/',
          show_stats : bool = False, ax : axes = None):
    """Route a circuit.

    Args:
        circuit (Circuit): Circuit which shall be routed.
        routing_name (str): Name of the routing (for the .tcl file)
        plan_wires (bool, optional): If True, the wires of the routing will be planned. Defaults to True.
        planning_iterations (int, optional): Number of wire-planning iterations. Defaults to 20.
        gcell_length (int, optional): Length of a gcell on the planning graph. Defaults to 150.
        use_layers (list[str], optional): Which layers shall be used for planning. Defaults to ['m1', 'm2'].
        destination_path (str, optional): Destination path of the magic-routing .tcl script. Defaults to 'Magic/Routing'.
        show_stats (bool, optional): If True, route specific data will be printed. Defaults to False.
        ax (axes, optional): If given, the route will be plotted on this axis. Defaults to None.
    """
    
    #get all nets of the circuit
    nets = list(get_nets_and_pins(circuit=circuit).keys())
    #sort the nets according their area - ascending
    nets = sorted(nets, key=lambda n : (n.bounding_box()[2]-n.bounding_box()[0])*(n.bounding_box()[3]-n.bounding_box()[1]))
    
    #setup a route for each net
    routes : dict[Net, Route]
    routes = {}
    for net in nets:
        routes[net] = Route(net, global_pdk)

    
    routes_list = list(routes.values())

    #calculate the bounding box of the circuit
    #given by the circuits cells
    circuit_bound = [float('inf'),float('inf'),-float('inf'),-float('inf')]

    for device in circuit.devices.values():
        bound = device.cell.get_bounding_box()
        circuit_bound[0] = min(circuit_bound[0], bound[0])
        circuit_bound[1] = min(circuit_bound[1], bound[1])
        circuit_bound[2] = max(circuit_bound[2], bound[2])
        circuit_bound[3] = max(circuit_bound[3], bound[3])

    if plan_wires:
        #if the wires shall be planned
        #setup a planning graph
        #and plan the routes
        planning_graph = PlanningGraph(circuit_bound, gcell_length, gcell_length, use_layers)
        wire_planner = plan_routes(routes_list, planning_graph, planning_iterations)
        route_order = wire_planner._get_route_order()
    else:
        route_order = routes_list
    
    #connect all terminal pins
    for route in route_order:
        try:
            route.route_terminals()
        except Exception as error:
            print(f"Connecting terminal pins for route {route} failed with error:\n{error}")
            print("Trying next route.")
    

    #connect all terminals and child - routes
    for route in route_order:
        try:
            route.connect_terminals()
            route.connect_with_child_routes()
        except Exception as error:
            print(f"Routing of route {route} failed with error:\n{error}")
            print("Trying next route.")

    if show_stats:
        table = PrettyTable(['Net name', 'Length', '#Vias'])
        total_length = 0
        total_vias = 0
        for route, i in zip(route_order, range(len(route_order))):
            length = route.get_route_length()
            vias = route.get_number_of_vias()
            divider = i==len(route_order)-1
            table.add_row([route.name, length, vias], divider=divider)
            total_length += length
            total_vias += vias
        
        table.add_row(['Total', total_length, total_vias])

        print(table)
    
    if ax:
        for route in route_order:
            route.plot(ax)
    #generate the tcl. script
    if not os.path.exists(destination_path):
        #generate the path
        os.makedirs(destination_path)
        print(f"Generated destination path {destination_path}")
    
    if not destination_path.endswith('/'):
        destination_path += '/'
        
    dest_file = destination_path+routing_name+'_routing.tcl'
    #write a route file
    file = open(dest_file, 'w')
    file.write("")
    file.close()


    for net in nets:
        routes[net].write_route_to_file(dest_file)

def plan_routes(routes : list[Route], planning_graph : PlanningGraph, planning_iterations : int = 20, ) -> WirePlanner:
    
    wire_planner = WirePlanner(routes, planning_graph)

    try:
        wire_planner.plan_routes(n_iterations=planning_iterations)
    except Exception as error:
        print(f"Planning routes failed with error {error}!")
        sys.exit(1)
    
    if planning_graph.get_total_crossing_nets()>0:
        print(f"Not all crossing nets eliminated! Try to increase PLANNING_ITERATIONS!")
    
    if planning_graph.get_total_overflow()>0:
        print(f"There are tiles with overflow > 0! Try to increase PLANNING_ITERATIONS!")

    return wire_planner