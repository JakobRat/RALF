from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SchematicCapture.Devices import Device, PrimitiveDevice
    from SchematicCapture.Primitives import PrimitiveDeviceComposition
    from SchematicCapture.Netlist import Netlist
import networkx as nx


from SchematicCapture.Devices import MOS, ThreeTermResistor, Capacitor, SubDevice, NTermDevice, SUPPORTED_DEVICES
from SchematicCapture.Net import Net, SubNet

import matplotlib.pyplot as plt
import math
import copy

from collections import OrderedDict

class Circuit:
    """Class to store a circuit.
    """
    def __init__(self, netlist : Netlist, topology_layer=1, name=''):
        """Setup a circuit for Netlist <netlist>.
            Only non-parametrized circuits are supported!
            Lines with .parameter will be omitted!
            
        Args:
            netlist (Netlist): Netlist of the circuit.
            topology_layer (int, optional): Topological layer of the circuit. 
                                            The top-circuit is at layer 1, a sub circuit in the top-circuit is at layer 2, and so on. 
                                            Defaults to 1.
            name (str, optional): Name of the circuit. Defaults to ''.
        """
        self._netlist = netlist
        #setup a graph for the circuit
        self._graph = nx.MultiGraph()
        #set the name of the circuit
        self._name = name
        #setup a dict, to store the devices of the circuit
        self._devices : dict[str, Device]
        self._devices = {}
        #setup a dict, to store the nets of the circuit
        self._nets : dict[str, Net]
        self._nets = {}
        #save the topological layer
        self._topology_layer = topology_layer
        
        #instantiate the devices
        self._instantiate_devices()
        #instantiate the nets, which connect the devices
        self._instantiate_nets()

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Circuit) and (self._name == __value._name)
    
    def __hash__(self) -> int:
        return hash(self._name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
    
    def generate_circuit_graph(self, excluded_nets : list[Net] =[]):
        """Generate a graph for the circuit.

        Args:
            excluded_nets (list[Net], optional): Nets, which shall be excluded in the graph. Defaults to [].
        """
        self._graph = nx.MultiGraph()    
        self._graph.add_nodes_from(self._gen_nodes_list_from_devices())
        self._graph.add_edges_from(self._gen_edge_list_from_net(excluded_nets=excluded_nets))
    
    def update_circuit_graph(self, excluded_nets : list[Net]=[]):
        """Update the graph for the circuit.

        Args:
            excluded_nets (list[Net], optional): ets, which shall be excluded in the graph.. Defaults to [].
        """
        self._graph = nx.MultiGraph()
        self._graph.add_nodes_from(self._gen_nodes_list_from_devices())
        self._graph.add_edges_from(self._gen_edge_list_from_net(excluded_nets=excluded_nets))
    
    
    def get_edge_features(self):
        """Get the edge features of the circuit graph.

        Returns:
            dict: key: (device1, device2, Net), value: Edge feature.  
        """
        return nx.get_edge_attributes(self._graph, "edge_attr")
    
    def draw_graph(self, file_name : str):
        """Draw the circuit graph and save a image of it.

        Args:
            file_name (str): Name of the resulting file.
        """
        nx.draw(self._graph, with_labels=True)
        plt.savefig(file_name)
    
    def set_name(self, name : str):
        """Set the name of the circuit.

        Args:
            name (str): Name of the circuit.
        """
        self._name = name

    @property
    def topology_layer(self) -> int:
        """Get the topological layer of the circuit.

        Returns:
            int: Topological layer of the circuit.
        """
        return self._topology_layer

    @property
    def name(self) -> str:
        """Get the name of the circuit.

        Returns:
            str: Name of the circuit.
        """
        return self._name
    
    @property
    def graph(self) -> nx.MultiGraph:
        """Get a graph representation of the circuit.

        Returns:
            nx.MultiGraph: Circuit graph.
        """
        return self._graph
    
    @property
    def feature_graph(self) -> nx.MultiGraph:
        """Get a graph representation of the circuit, with node and edge features.
            Node features: 'x': List of features of the nodes-device, 'name': Name of the device
            Edge features: 'edge_attr': List of features of the net connecting the nodes-devices, 'edge_name': Name of the net, connecting the nodes-devices. 
        
        Returns:
            nx.MultiGraph: Circuit graph with features.
        """
        #setup a list of nodes, with node features
        node_list = []
        for n, n_attr in self.graph.nodes(data=True):
            node_list.append((n, {"x": n_attr['Device'].feature_list, "name": n_attr['Device'].name}))
        
        #setup a list of edges, with edge features
        edge_list = []
        for u, v, e_attr in self.graph.edges(data=True):
            edge_list.append((u,v, {"edge_attr" : e_attr["Net"].feature_list_between(self.devices[u], self.devices[v]), "edge_name": e_attr["Net"].name}))

        #setup a graph induced from the nodes and edges
        g = nx.MultiGraph()
        g.add_nodes_from(node_list)
        g.add_edges_from(edge_list)
        return g
    
    @property
    def devices(self) -> dict[str, Device]:
        """Get the devices of the circuit.

        Returns:
            dict[str, Device]: key: Name of the device. Value: Device
        """
        return self._devices
    
    @property
    def nets(self) -> dict[str, Net]:
        """Get the nets of the circuit.

        Returns:
            dict[str, Net]: key: Name of the net. Value: Net
        """
        return self._nets
    
    def get_edge_feature(self, device1 : str, device2 : str, net : str) -> list[float]:
        """Get a list of features for the edge between <device1> and <device2>, connected through the Net <net>.

        Args:
            device1 (str): Name of the first device.
            device2 (str): Name of the second device.
            net (str): Name of the net.

        Returns:
            list[float]: List of features for the edge.
        """
        assert net in self._nets
        assert device1 in self._devices
        assert device2 in self._devices

        net_object = self._nets[net]
        device1 = self._devices[device1]
        device2 = self._devices[device2]

        return net_object.feature_list_between(device1, device2)
    
    def get_bipartite_graph(self, exclude_nets : list[Net]= []) -> nx.MultiGraph:
        """Get a bipartite graph representation of the circuit.
            First node set: Devices of the circuit.
            Second node set: Nets of the circuit.

        Args:
            exclude_nets (list[Net], optional): Nets which shall be excluded in the graph. Defaults to [].

        Returns:
            nx.MultiGraph: Bipartite graph of the circuit.
        """
        B = nx.MultiGraph()
        #generate nodes for the devices
        node_list_devices = self._gen_nodes_list_from_devices()
        #generate nodes for the nets
        node_list_nets = self._gen_nodes_list_from_nets(exclude_nets=exclude_nets)
        #generate edges between the two sets
        edge_list = self._gen_edge_list_from_devices(exclude_nets=exclude_nets)

        B.add_nodes_from(node_list_devices, bipartite=0)
        B.add_nodes_from(node_list_nets, bipartite=1)
        B.add_edges_from(edge_list)

        return B

    def include_primitives(self, primitives : dict[str, list[PrimitiveDeviceComposition]]):
        """Incorporates all primitive devices (e.g. DiffPair, DiffLoad, RString, ...) into the circuit.

        Args:
            primitives (dict): Dictionary of all primitives. key: Name of the primitive Value: List of primitives.
        """
        
        for (name, prim_list) in primitives.items():
            #loop through all primitive types
            for primitive in prim_list:
                #loop through all primitives 
                for device in primitive.devices:
                    #loop through all devices that the primitive device merges
                    for (net_name, net) in device.nets.items():
                        #reconnect the nets from the device to the primitive
                        del net.devices[device.name]
                        net.add_device(primitive)
                        primitive.set_net_class(net)
                    #delete the device from the circuit
                    del self.devices[device.name]
                
                #set the nets of the terminals
                for (k,v) in primitive.terminal_nets.items():
                    primitive.terminals[k].set_net(v)
                
                #add the primitive to the circuit
                self.devices[primitive.name] = primitive
        
        #update the modified circuit graph
        self.update_circuit_graph()

    def map_devices_to_netlist(self) -> dict[str, Device]:
        """Get the devices without their suffix.

        Returns:
            dict[str, Device]: key: Name of the device as in the netlist, value: Device.
        """
        device_map = {}
        for (d_name, d) in self.devices.items():
            d_name_without_suffix = d.name_without_suffix
            device_map[d_name_without_suffix] = d

        return device_map
          
    def _instantiate_devices(self):
        """Instantiate the devices of the circuit.
        """
        #iterate over each line in the netlist
        for l in self._netlist.get_net():
            
            device = None
            
            #setup a suffix for the device
            name_suffix = ''
            if type(self)==SubCircuit:
                # if the device will be in a sub circuit
                # set the suffix as the name of the sub-device 
                # of the sub circuit
                name_suffix = self.sub_device.name

            #generate devices
            if l.startswith("XM"): #mosfet
                device = MOS(l, name_suffix=name_suffix)
            elif l.startswith("XR"): #resistor
                device = ThreeTermResistor(l, name_suffix=name_suffix)
            elif l.startswith("XC"): #capacitor
                device = Capacitor(l, name_suffix=name_suffix)
            elif l.startswith("x"): #sub-device
                #get the model of the sub-device
                device_model = SubDevice.get_model(l)

                #set the top-netlist as the netlist of the sub-circuit
                subnet = copy.copy(self._netlist)
                subnet._net = subnet.get_subnets()[device_model]
                
                #get the names of the terminals of the sub-circuit
                terminal_names = SubCircuit.get_terminal_names(subnet._net[0])
                
                #generate a SubDevice 
                device = SubDevice(l, name_suffix=name_suffix, terminal_names = terminal_names)
                
                #generate a sub-circuit for the SubDevice
                subcirc = SubCircuit(subnet, self, device, self._topology_layer+1)
                
                #generate a circuit graph for the SubCircuit
                subcirc.generate_circuit_graph()
                
                #set the SubCircuit of the SubDevice
                device.set_circuit(subcirc)

            #add the device to the devices dict
            if device:
                self._devices[device._name] = device
                
    def _instantiate_nets(self):
        """Instantiate the nets of the circuit.
        """
        #iterate over all devices of the circuit
        for (d_name, d) in self._devices.items():
            #iterate over the nets of the device
            for (Net_name, net) in d.nets.items():
                if net is None: #if net isn't initialized
                    #check if the net is already instantiated in the circuit
                    if Net_name in self._nets:
                        #retrieve the net
                        new_Net = self._nets[Net_name]
                    else:
                        #generate a new net
                        if isinstance(self, SubCircuit):
                            #if the circuit is a SubCircuit, generate a SubNet
                            new_Net = SubNet(Net_name, self, self.sub_device)
                        else:
                            #generate a top-net
                            new_Net = Net(Net_name, self)
                        
                        #add the net to the nets dict
                        self._nets[Net_name] = new_Net
                    
                    new_Net.add_device(d) #add actual device to net
                    d.set_net_class(new_Net) #set net for device
            
            d : NTermDevice
            #set the nets of the terminals
            for (k,v) in d.terminal_nets.items():
                d.terminals[k].set_net(v)
               
    def _gen_edge_list_from_net(self, excluded_nets : list[Net]=[]) -> list[tuple]:
        """Generate the edge list from the circuits nets.

        Args:
            excluded_nets (list[Net], optional): Nets which shall be excluded. Defaults to [].

        Returns:
            list[tuple]: List of edges (tuples) between connected devices of the circuit.

        Example:
            Circuit: (Simple current mirror)
                    XM1 net1 net1 vss vss ....
                    XR1 Vdd net1 vss ....
                    XM2 net2 net1 vss vss ...

            Generated edge-list:    [('XM1', 'XR1', {'Net':net1}), ('XM1', 'XM2', {'Net':net1}),
                                     ('XM2', 'XR1', {'Net':net1}), ('XM1', 'XR1', {'Net':vss}),
                                     ('XM1', 'XM2', {'Net':vss}), ('XM2', 'XR1', {'Net':vss})]
        """
        edge_list = []
        #iterate over the nets of the circuit
        for (N_name, n) in self._nets.items():
            #if the net isn't excluded
            if N_name not in excluded_nets:
                #get the devices-names which are connected to the net
                d = list(n.devices.keys())
                #get a combinization of the devices, to introduce 
                #edges between the devices and add the net as attribute
                comb = Circuit._combinize(d, attr={'Net': n})
                #if there is a combinization, add it to the edge list
                if comb:
                    edge_list.extend(comb)
        
        return edge_list
    
    def _gen_nodes_list_from_devices(self) -> list[tuple[str, dict]]:
        """Generate a nodes-list from the circuits devices.

        Returns:
            list[tuple]: List of (device-name, attr={'Device':Device, 'label':"Device"})
        
        Example:
            Circuit: (Simple current mirror)
                    XM1 net1 net1 vss vss ....
                    XR1 Vdd net1 vss ....
                    XM2 net2 net1 vss vss ...
            Generated node list:    [('XM1', {'Device':MOS(XM1), 'label':'Device'}),
                                     ('XR1', {'Device':ThreeTermResistor(XR1), 'label':'Device'}),
                                     ('XM2', {'Device':MOS(XM2), 'label':'Device'})]
        """
        node_list = []
        #iterate over all devices of the circuit
        for (d_name, d) in self._devices.items():
            node_list.append((d_name, {'Device':d, 'label':"Device"}))
        return node_list
    
    def _gen_nodes_list_from_nets(self, exclude_nets : list[Net]= []) -> list[tuple[str, dict]]:
        """Generate a nodes-list from the circuits nets.

        Returns:
            list[tuple]: List of (net-name, attr={'Net': Net, 'label':"Net"})
        
        Example:
            Circuit: (Simple current mirror)
                    XM1 net1 net1 vss vss ....
                    XR1 Vdd net1 vss ....
                    XM2 net2 net1 vss vss ...
            Generated nodes list:   [('net1', {'Net':Net(net1), 'label':'Net'}),
                                     ('vss', {'Net':Net(vss), 'label':'Net'}),
                                     ('Vdd', {'Net':Net(Vdd), 'label':'Net'}),
                                     ('net2', {'Net':Net(net2), 'label':'Net'})]
        """ 
        node_list = []
        #iterate over all nets
        for (n_name, n) in self._nets.items():
            if n_name in exclude_nets:
                pass
            else:
                node_list.append((n_name, {'Net':n, 'label':"Net"}))
        return node_list
    
    def _gen_edge_list_from_devices(self, exclude_nets : list[Net]= []) -> list[tuple[str,str,dict]]:
        """Generate  edges from a devices, to their connected nets. 

        Args:
            exclude_nets (list[Net], optional): Nets which shall be excluded. Defaults to [].

        Returns:
            list[tuple]: List of edges (device-name, net-name, attr={'Terminal': str(Terminal-names)})
        
        Example:
            Circuit: (Simple current mirror)
                    XM1 net1 net1 vss vss ....
                    XR1 Vdd net1 vss ....
                    XM2 net2 net1 vss vss ...

            Generated edge-list:    [('XM1', 'net1', {'Terminal':'DG'}),
                                     ('XM1', 'vss', {'Terminal':'SB'}),
                                     ('XR1', 'Vdd', {'Terminal':'D'}),
                                     ('XR1', 'net1', {'Terminal':'S'}),
                                     ('XR1', 'vss', {'Terminal':'B'}),
                                     ('XM2', 'net2', {'Terminal':'D'}),
                                     ('XM2', 'net1', {'Terminal':'G'}),
                                     ('XM2', 'vss', {'Terminal':'SB'})]
        """
        edge_list = []
        #iterate over the devices of the circuit
        for (d_name, d) in self._devices.items():
            assert isinstance(d, NTermDevice)
            #iterate over the nets of the device
            for (n_name, n) in d.get_nets().items():
                if n_name in exclude_nets:
                    pass
                else:
                    edge_list.append((d_name, n_name, {'Terminal' : "".join(d.map_nets_to_terminal_names(n))}))
        return edge_list

    @staticmethod
    def _combinize(l : list, attr=None):
        """Combinize the items in the list.

        Args:
            l (list): List which items have to be combinized.
            attr (Any, optional): Attribute which shall be added to the combination. Defaults to None.

        Returns:
            list[tuple]: List of combinations.
        
        Example:
            c = _combinize(l=[1,2,3])
            c = [(1,2),(1,3),(2,3)]
            c = _combinize(l=[1,2,3], attr='example')
            c = [(1,2,'example'),(1,3,'example'),(2,3,'example')]

        """
        result = []
        #iterate over the list up to the penultimate entry
        for i in range(len(l)-1):
            #iterate up to the last entry
            for j in range(i+1,len(l)):
                #add the combination to the result
                if attr:
                    result.append((l[i], l[j], attr))
                else:
                    result.append((l[i], l[j]))
        return result
    
class SubCircuit(Circuit):
    """Class to store a sub-circuit.
        A sub-circuit is located in the top-circuit (Circuit) or in another sub-circuit. 
        This circuit is the parent-circuit of the sub-circuit.
        A sub-circuit describes the internal circuitry of a SubDevice.
    """
    def __init__(self, netlist : Netlist, parent_circuit : Circuit, sub_device : SubDevice, topology_layer=2):
        """Setup a sub-circuit. 
            Only non-parametrized sub-circuits are supported!

        Args:
            netlist (Netlist): Netlist of the SubCircuit, starting with .subckt subname N1 <N2 N3 ...>. 
            parent_circuit (Circuit): Parent circuit of the SubCircuit. (Circuit in which the SubCircuit is located.)
            sub_device (SubDevice): SubDevice to which the SubCircuit belongs.
            topology_layer (int, optional): Topological layer of the circuit. (-> parent_circuit.topology_layer +1) Defaults to 2.
        """
        self._parent_circuit = parent_circuit
        self._sub_device = sub_device
        
        #get the name of the SubCircuit from the .subckt statement
        self._name = netlist.get_net()[0].split()[1]
        
        #get the names of the terminal nets (SubCircuit ports / external nodes)
        self._terminal_net_keys = SubCircuit.get_terminal_names(netlist._net[0])
        
        #setup the circuit
        super().__init__(netlist,topology_layer, name=netlist._net[0].split()[1])
        
    @property
    def sub_device(self) -> SubDevice:
        """Get the SubDevice which is linked with the SubCircuit.

        Returns:
            SubDevice: SubDevice which is linked with the SubCircuit
        """
        return self._sub_device

    @property
    def parent_circuit(self) -> Circuit:
        """Get the parent-circuit of the SubCircuit.

        Returns:
            Circuit: Parent-circuit of the SubCircuit
        """
        return self._parent_circuit
    
    @property
    def terminal_nets(self) -> OrderedDict[str, Net]:
        """Get a map of the terminal nets, which maps the names
            of the terminal-nets to the internal net instances.

        Returns:
            OrderedDict: key: Name of the net, as in the .subckt definition, value: Net instance.
        """
        term = OrderedDict()

        for k in self._terminal_net_keys:
            term[k] = self._nets[k]
        
        return term
        
    @staticmethod
    def get_terminal_names(line : str) -> list[str]:
        """Get the names of the terminal nets of the SubCircuit.

        Args:
            line (str): Spice line starting with .subckt

        Returns:
            list[str]: Names of the terminal nets.
        """
        assert line.startswith('.subckt') or line.startswith('.SUBCKT'), f"Spice line for subckt definition don't starts with .subckt!"
        
        #split the line by ' '
        splitted = line.split()
        terminals = []
        #iterate over the terminal net names
        for i in range(2, len(splitted)):
            if "=" in splitted[i]:
                #if a '=' is included -> parameter -> stop
                break
            else:
                terminals.append(splitted[i])
        return terminals
