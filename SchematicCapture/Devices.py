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

SUPPORTED_DEVICES = {
    "sky130_fd_pr__nfet_01v8" : 0,
    "sky130_fd_pr__pfet_01v8" : 1,
    "sky130_fd_pr__res_xhigh_po_0p35" : 2,
    "sky130_fd_pr__cap_mim_m3_1" : 3,
    "sky130_fd_pr__cap_mim_m3_2" : 4,
    }

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Magic.Cell import Cell
    from SchematicCapture.Net import Net
    from Rules.RoutingRules import RoutingRule
    from SchematicCapture.Circuit import Circuit, SubCircuit

import abc
import Rules.PlacementRules as PlacementRules
from PDK.PDK import global_pdk
from SchematicCapture.Ports import SubDevicePin, Pin
from collections import OrderedDict
from Rules.RoutingRules import ObstacleRule, RoutingRule

class Device(metaclass = abc.ABCMeta):
    def __init__(self, spice_description : str, name_suffix = ''):
        """Generate a device.

        Args:
            spice_description (str): Spice description of the device.
            name_suffix (str, optional): Suffix to extend the spice-name of the device. Defaults to ''.
                                            E.g. if the spice description starts with XM1 and the name_suffix is x1,
                                            the name of the device will be XM1_x1.
        
        """
        self._spice = spice_description
        #split the line by ' '
        self._spice_splitted = self._spice.split()

        self._nets : OrderedDict[str, Net]
        self._nets = OrderedDict() #nets connected to the device, ordered according the spice-description
        
        self._terminal_nets : list[str]
        self._terminal_nets = [] #name of the nets connected to the terminals of the device
        
        self._terminals : OrderedDict[str, Pin]
        self._terminals = OrderedDict() #terminals of the device, ordered according the spice-description
        
        self._parameters : dict[str, int|float]
        self._parameters = {} #parameters of the device
        
        self._name_suffix = name_suffix
        self._name = self._spice_splitted[0]+'_'+name_suffix if name_suffix != '' else self._spice_splitted[0]
        
        self._model : str
        self._model = None #model of the device
        
        self._cell : Cell
        self._cell = None #stores the cell of the device
        
        self._placement_rules : PlacementRules
        self._placement_rules = None #stores the placement rules of the device
        
        self._features : dict[str, int|float]
        self._features = {} #dict to store the features of an device
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name})"
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Device) and
                (self.name == other.name))
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    @property
    def nets(self) -> dict[str, Net]:
        """Get the nets of the device.

        Returns:
            dict: key: Name of the net, value: Net instance.
        """
        return self._nets
    
    @property
    def name(self) -> str:
        """Get the name of the device.

        Returns:
            str: Name of the device.
        """
        return self._name
    
    @property
    def model(self) -> str:
        """Get the model of the device.

        Returns:
            str: Model of the device.
        """
        return self._model
    
    @property
    def parameters(self) -> dict[str, int|float]:
        """Get the parameters of the device.

        Returns:
            dict: key: Parameter name, value: Parameter value.
        """
        return self._parameters
        
    @property
    def name_suffix(self) -> str:
        """Get the name suffix of the device.

        Returns:
            str: Suffix of the device name.
        """
        return self._name_suffix
    
    @property
    def name_without_suffix(self) -> str:
        """Get the name of the device without suffix.
            (Name as in the netlist.)

        Returns:
            str: Name of the device.
        """
        return self._spice_splitted[0]

    @property
    def terminals(self) -> dict[str, Pin]:
        """Get the terminals of the device.

        Returns:
            dict: key: Name of the terminal value: Terminal instance.
        """
        return self._terminals
    
    def get_nets(self) -> OrderedDict[str, Net]:
        """Get the nets connected to the device.
            Ordered as in the spice line.
        Returns:
            dict: key: Net name, value: Net object
        """
        return self._nets
    
    def set_net_class(self, net : Net):
        """Add the net-object to the devices nets.

        Args:
            net (Net): Net which shall be added.
        """
        assert net.name in self._nets, f"Netname {net.name}, not registered in the devices nets!"
        self._nets[net.name] = net

    def get_nets_and_terminals(self) -> dict[str, tuple[Net, Pin]]:
        """Get the nets and according terminals of the device.

        Returns:
            dict: key: Net name, value: (Net instance, Pin instance)
        """
        temp = {}
        for (net_name, net, terminal) in zip(self._nets.keys(), self._nets.values(), self._terminals.values()):
            temp[net_name] = (net, terminal)
        
        return temp
    
    def add_feature(self, feature : str, value : int|float):
        """Add features to the device.

        Args:
            feature (str): Feature identifier.
            value (int/float): Feature value. 
        """
        assert type(value)==int or type(value)==float
        self._features[feature] = value
    
    def update_feature(self, feature : str, value : int|float) -> bool:
        """Update a feature.

        Args:
            feature (str): Feature identifier.
            value (int/float): Feature value.

        Returns:
            bool: True if the feature where updated. 
        """
        if feature in self._features:
            self._features.update({feature : value})
            return True
        else:
            return False
        
    @property
    def feature(self) -> dict[str, float|int]:
        """Get the features of the device.

        Returns:
            dict: key: Feature identifier value: Feature value.
        """
        return self._features
    
    @property
    def feature_list(self) -> list[int|float]:
        """Returns the feature values of the device as a list.
            Including the cells features, if the device has a cell.
        Returns:
            list : List of feature values
        """
        device_features = list(self._features.values())
        
        if self._cell:
            #if the device has also a cell, extend the features of the cell.
            device_features.extend(self._cell.feature_list)
                
        return device_features
    
    @property
    def cell(self) -> Cell:
        """Get the cell of the device.

        Returns:
            Cell: Cell of the device.
        """
        return self._cell

    def set_cell(self, cell : Cell):
        """Set the cell of the device.

        Args:
            cell (Cell): Cell of the device.
        """
        self._cell = cell
        #register the device at the cell
        self._cell.set_device(self)
        
        #add terminals to the cell 
        self._cell.add_terminals()

        #generate placement rules, induced from the device and cell
        self._gen_placement_rules()

    def _set_params(self):
        """Set the parameters of the device.
        """
        #get the parameters of the device from the spice line
        params = self._get_params(self._spice)
        
        #iterate over the parameters
        for p in params:
            #split the parameter by '='
            p_splitted = p.split("=")
            #check if the parameter were registered
            if p_splitted[0] in self._parameters:
                #print(p_splitted)
                #print(self._parameters)
                temp = self._parameters.copy()
                
                #transform the str into a int|float
                evald = eval(p_splitted[1])
                
                if type(evald)==str:
                    #if the str can't be evaluated
                    #try to provide values from the parameters
                    evald = eval(evald, temp)
                
                self._parameters[p_splitted[0]] = evald

    @abc.abstractmethod
    def _gen_placement_rules(self):
        """Generate placement rules for the device.
        """
        self._cell.set_placement_rules(self._placement_rules)
                               
    @staticmethod   
    def _get_params(line : str) -> list[str]:
        """
        Parameters
        ----------
        line : str
            spice description of a device

        Returns
        -------
        params : list (str)
            list of the parameters of a spice device

        """
        params = []
        last_space = 0
        param = False
        ignore_space = False
        #iterate over the line
        for n in range(len(line)):
            l = line[n]

            #find the spaces between parameters
            if l == " " and not param:
                last_space = n
                continue
            
            #if there is a '=' and actual not in an parameter
            if l == "=" and not param:
                param = True
                continue
            
            #if in param, and a math statement starts
            if l=="'" and not ignore_space and param:
                ignore_space = True
                continue
            
            #if in param and a math statement ends
            if l=="'" and ignore_space and param:
                #add the parameter to the parameter list
                params.append(line[last_space+1:n+1])
                ignore_space = False
                param = False
                continue
            
            #if in param and param ends
            if l==" " and not ignore_space and param:
                #add the parameter to the parameter list
                params.append(line[last_space+1:n])
                last_space = n
                ignore_space = False
                param = False
                continue
        
        if param:
            params.append(line[last_space+1:])
        
        return params
    

  
class NTermDevice(Device, metaclass=abc.ABCMeta):
    """Class for a n-terminal device.
        A n-terminal device is a device which has n-terminals.
        E.g. MOS is a 4-term device.
    """
    def __init__(self, spice_description : str, N_Terminals : int, name_suffix=''):
        """Setup a N-terminal device.

        Args:
            spice_description (str): Spice description of the device.
            N_Terminals (int): Number of terminals.
            name_suffix (str, optional): Suffix to extend the spice-name of the device. Defaults to ''.
        """
        super().__init__(spice_description, name_suffix)
        self._N_Terminals = N_Terminals
        
        #setup the nets of the device
        self._set_nets()

        #setup the terminals
        self._setup_terminals()

        assert len(self._terminal_nets)==len(self._terminals), f"Number of nets and terminals don't match for device {self.name}!"

    def _set_nets(self):
        """Setup the nets dict, with the names of the nets connected to the device.
        """

        splitted = self._spice_splitted
        #iterate over the terminal names
        for i in range(self._N_Terminals):
            #register the net name in the nets dict
            self._nets[splitted[i+1]]=None
            #register the net-name in the terminals net names
            self._terminal_nets.append(splitted[i+1])

    @abc.abstractmethod
    def _setup_terminals(self):
        """Setup the terminals of the device.

        Raises:
            NotImplementedError: If not implemented.
        """
        raise NotImplementedError

    @property
    def terminal_nets(self) -> dict[str, Net]:
        """Maps the terminals of the device, to the nets connected to the terminals.

        Returns:
            dict: key: terminal name of the device. Value: Net connected to the terminal.
        """
        #self.terminals : dict, key: terminal name, value: pin instance
        #self._terminal_nets : list of the terminal net names
        return { terminal_name : self._nets[self._terminal_nets[i]] for (terminal_name, i) in zip(self.terminals.keys(), range(len(self.terminals)))}


    def map_nets_to_terminals(self) -> dict[str, Pin]:
        """Get a dict, with net-name as key and terminal instance as value.

        Returns:
            dict: key: Net-name, value: Terminal connected to net.
        """
        return {k : v for (k,v) in zip(self._terminal_nets, self._terminals.values())}
    
    def map_nets_to_terminal_names(self, net : Net) -> list[str]:
        """Get a str description of the terminals, which are connected to the net <net>.

        Args:
            net (Net): Net which is connected to terminals.

        Returns:
            list[str]: Names of terminals, connected to the net.
        
        Example:
            Device: XM1 net1 net2 vss vss ...
            map_nets_to_terminal_names(Net(net1)) = [['D']
            map_nets_to_terminal_names(Net(net2)) = ['G']
            map_nets_to_terminal_names(Net(vss)) = ['S','B']
        """
        terminal_names = []
        #iterate over the terminals of the device
        for (terminal_name, terminal) in self.terminals.items():
            if net == terminal.net:
                #if the net is connected to the terminal 
                #append the terminal name to the terminal_names list
                terminal_names.append(terminal_name)
        
        return terminal_names
        
    def get_terminals_connected_to_net(self, net : Net) -> list[Pin]:
        """Get a list, which contains all terminals of the device 
            connected to the net <net>.

        Args:
            net (Net): Net connected to terminals of the device.

        Returns:
            list[Pin]: List of the terminals (pins) which are connected to the net.
        """
        terminals = []
        #iterate over the terminals
        for (terminal_name, terminal) in self.terminals.items():
            if net == terminal.net:
                #if the net is connected to the terminal 
                #add it to the list
                terminals.append(terminal)
        
        return terminals
    
class PrimitiveDevice(NTermDevice, metaclass=abc.ABCMeta):
    """Class for a primitive device.
        A primitive device is a n-terminal-device which isn't a composition of devices.
        E.g. MOSFET, Resistor, Capacitor, ... 
    """
    def __init__(self, spice_description : str, N_Terminals : int, name_suffix='', use_dummies = False):
        """Setup a primitive device.

        Args:
            spice_description (str): Spice description of the device.
            N_Terminals (int): Number of terminals.
            name_suffix (str, optional): Name suffix of the device. Defaults to ''.
            use_dummies (bool, optional): If the device uses dummies. Defaults to False.
        """
        super().__init__(spice_description, N_Terminals, name_suffix)

        #a primitive device can be directly instantiated in magic
        #store parameters for the instantiation in a dict.
        self._cell_parameters = {}
        self._use_dummies = use_dummies

    @abc.abstractmethod
    def _generate_routing_rules(self) -> list[RoutingRule]:
        """Method to generate the routing rules for a primitive device.

        Raises:
            TypeError: If the device has no cell-view.

        Returns:
            list[RoutingRule]: List of routing rules.
        """
        if self.cell:
            return []
        else:
            raise TypeError("Devices cell isn't instantiated!")

    def get_routing_rules(self) -> list[RoutingRule]:
        """Get the routing rules of the device.

        Returns:
            list[RoutingRule]: List of routing rules.
        """
        return self._generate_routing_rules()

    @property
    def cell_parameters(self) -> dict[str, int]:
        """Get the parameters for cell instantiation.

        Returns:
            dict: key: Name of the parameter, value: Value of the parameter
        """
        return self._cell_parameters
    
    @property
    def use_dummies(self) -> bool:
        """Check if the device uses dummies.

        Returns:
            bool: True, if the device uses dummies, else False.
        """
        return self._use_dummies
    
    def set_cell_parameter(self, name : str, value : int):
        """Set a parameter for cell instantiation.

        Args:
            name (str): Name of the parameter.
            value (int): Value of the parameter.
        """
        self._cell_parameters[name] = value

class Resistor(PrimitiveDevice):
    """Class for a resistor.
    """
    def __init__(self, spice_description, name_suffix=''):
        raise NotImplementedError
        super().__init__(spice_description,2, name_suffix)
        

class ThreeTermResistor(PrimitiveDevice):
    """Class for a three terminal resistor, like a poly-resistor.

            D    -------------    S
           -----|     R       |-----
                 -------------
                      |
                      B
    """
    def __init__(self, spice_description : str, name_suffix=''):
        """Setup a three-terminal resistor.

        Args:
            spice_description (str): Spice description of the resistor.
            name_suffix (str, optional): Name suffix of the device. Defaults to ''.

        Raises:
            ValueError: If the device uses a not supported model.
        """
        super().__init__(spice_description, 3, name_suffix)
        
        #check if the model of the device is supported
        if self._spice_splitted[4] not in SUPPORTED_DEVICES:
            raise ValueError(f"Device {self._spice_splitted[0]} of type {self._spice_splitted[4]} not supported!")

        #set the model of the device
        self._model = self._spice_splitted[4]
        #add the model as feature
        self.add_feature("model", SUPPORTED_DEVICES[self._model])

        #set the parameters which shall be stored
        # ToDo: Generalize for other widths  
        self._parameters = {"L":None, "mult":None, "m":None, "W": 0.35}
        self._set_params()
        
        #add features from the parameters
        # ToDo: Generalize for other widths 
        self.add_feature("L", self._parameters["L"])
        self.add_feature("W", 0.35)
        self.add_feature("m", self._parameters["m"])
        self.add_feature("nf", 0)

    
    def _setup_terminals(self):
        """Setup the terminals of the device.
            -> The terminals are the devices pins. 'D','S' & 'B'
        """
        self._terminals["D"] = Pin('D', self)
        self._terminals["S"] = Pin('S', self)
        self._terminals["B"] = Pin('B', self)
        
    def _gen_placement_rules(self):
        """Generate the placement rules for the device
        """
        #needs no spacing rule
        # since the resistor lies in p-substrate
        # ToDo: Generalize for other resistors
        super()._gen_placement_rules()
    
    def _generate_routing_rules(self) -> list[RoutingRule]:
        #needs no routing rules
        # ToDo: Generalize for other resistors
        return super()._generate_routing_rules()
    
class Capacitor(PrimitiveDevice):
    """Class for a capacitor.
                 
                 C
                | |
             D  | |  S
            ----| |----
                | |
                | |

    """
    def __init__(self, spice_description : str, name_suffix=''):
        """Setup a capacitor.

        Args:
            spice_description (str): Spice description of the capacitor.
            name_suffix (str, optional): Name suffix of the device. Defaults to ''.

        Raises:
            ValueError: If the capacitor uses a not supported model.
        """
        super().__init__(spice_description, 2, name_suffix)

        #check if the model is supported
        if self._spice_splitted[3] not in SUPPORTED_DEVICES:
            raise ValueError(f"Device {self._spice_splitted[0]} of type {self._spice_splitted[3]} not supported!")
        
        #set the model
        self._model = self._spice_splitted[3]
        #add the model as feature
        self.add_feature("model", SUPPORTED_DEVICES[self._model])

        #set the parameters of the device
        self._parameters = {"L":None, "W":None, "m":None, "MF": None}
        self._set_params()
        
        #add features from the parameters
        self.add_feature("L", self._parameters["L"])
        self.add_feature("W", self._parameters["W"])
        self.add_feature("m", self._parameters["m"])
        self.add_feature("nf", 0)

    def _setup_terminals(self):
        """ Setup the terminals of the device.
            -> The terminals are the devices pins. 'D' & 'S'
        """
        self._terminals["D"] = Pin('D', self)
        self._terminals["S"] = Pin('S', self)

    
    def _gen_placement_rules(self):
        """Generate placement rules for the device.
        """
        if self.model == 'sky130_fd_pr__cap_mim_m3_1':
            #generate a spacing rules for the bottom, mim-cap and top-layer of the capacitor
            rule1 = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("m3"))
            rule2 = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("mimcap"))
            rule3 = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("m4"))
            self._placement_rules = PlacementRules.PlacementRules(cell=self.cell, rules=[rule1, rule2, rule3])
        elif self.model == 'sky130_fd_pr__cap_mim_m3_2':
            #generate a spacing rules for the bottom, mim-cap and top-layer of the capacitor
            rule1 = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("m4"))
            rule2 = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("mimcap"))
            rule3 = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("m5"))
            self._placement_rules = PlacementRules.PlacementRules(cell=self.cell, rules=[rule1, rule2, rule3])

        super()._gen_placement_rules()

    def _generate_routing_rules(self) -> list[RoutingRule]:
        super()._generate_routing_rules()
        if self.model == 'sky130_fd_pr__cap_mim_m3_1':
            #generate a obstacle rule for the bottom layer
            # -> it isn't allowed to route on the bottom layer 
            obstacle_rule = ObstacleRule(cell=self.cell, layer=global_pdk.get_layer("m3"))
        elif self.model == 'sky130_fd_pr__cap_mim_m3_2':
            #generate a obstacle rule for the bottom layer 
            # -> it isn't allowed to route on the bottom layer 
            obstacle_rule = ObstacleRule(cell=self.cell, layer=global_pdk.get_layer("m4"))
        
        return [obstacle_rule]
    
class MOS(PrimitiveDevice):
    """ Class to store a MOSFET.
        ```        
                  D
                  |
                |-|
              | |
         G----| |<---- B 
              | |
                |-|
                  | 
                  S
        ```
    """
    def __init__(self, spice_description : str, name_suffix=''):
        """Setup a MOS.

        Args:
            spice_description (str): Spice description of the MOS.
            name_suffix (str, optional): Name suffix of the device. Defaults to ''.

        Raises:
            ValueError: If the MOS uses a not supported model.
        """
        super().__init__(spice_description, 4, name_suffix)
        
        #check if the model is supported
        if self._spice_splitted[5] not in SUPPORTED_DEVICES:
            raise ValueError(f"Device {self._spice_splitted[0]} of type {self._spice_splitted[5]} not supported!")
        
        #set the model
        self._model = self._spice_splitted[5]
        #add the model as feature
        self.add_feature("model", SUPPORTED_DEVICES[self._model])
        
        #set the parameters
        self._parameters = {"L" : None, "W" : None, "nf" : None, "mult" : None,
                            "m" : None, "ad" : None, "as" : None, "pd" : None, "ps" : None}
        self._set_params()
        
        #add parameters as features
        self.add_feature("L", self._parameters["L"])
        self.add_feature("W", self._parameters["W"])
        self.add_feature("m", self._parameters["m"])
        self.add_feature("nf", self._parameters["nf"])
        
            
    def _setup_terminals(self):
        """ Setup the terminals of the MOS.
        """
        self._terminals["D"] = Pin('D', self)
        self._terminals["G"] = Pin('G', self)
        self._terminals["S"] = Pin('S', self)
        self._terminals["B"] = Pin('B', self)
    
    def _gen_placement_rules(self):
        if 'nfet' in self.model:
            #nfet has no spacing rule
            pass
        elif 'pfet' in self.model:
            #generate a spacing rule for the nwell
            rule = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("nwell"), net=self.terminal_nets['B'])
            self._placement_rules = PlacementRules.PlacementRules(cell=self.cell, rules=[rule])
        else:
            raise ValueError("No valid model for placement-rule given!")
        
        super()._gen_placement_rules()

    def _generate_routing_rules(self) -> list[RoutingRule]:
        return super()._generate_routing_rules()
    
class SubDevice(NTermDevice):
    """Class to store a sub-device. 
        A sub-device combines multiple devices, and is the product of a sub-circuit call.
        Each sub-device has a corresponding sub-circuit. 
    """
    def __init__(self, spice_description : str, terminal_names : list[str], name_suffix=''):
        """Setup a sub-device. 

        Args:
            spice_description (str): Spice description of the sub-device.
            terminal_names (list[str]): Name of the terminals of the sub-device, as defined in the .subckt statement.
            name_suffix (str, optional): Name suffix of the device. Defaults to ''.
        """
        #get the number of terminals from the spice description
        self._N_Terminals = SubDevice.get_N_Terminals(spice_description)
        #set the terminal names
        self._terminal_names = terminal_names
        #make sure, the number of terminal names and terminals of the device coincide
        assert len(terminal_names) == self._N_Terminals

        super().__init__(spice_description, self._N_Terminals, name_suffix)

        #get the model of the sub device == the name of the sub-circuit
        self._model = self._spice_splitted[1+self._N_Terminals]

        #holds the internal circuit of the device
        self._circuit = None 

        #add features - a sub-device has no "real" features
        self.add_feature("model", -1)
        self.add_feature("L", 0)
        self.add_feature("W", 0)
        self.add_feature("m", 0)
        self.add_feature("nf", 0)

    def set_circuit(self, circ : SubCircuit):
        """Set the internal circuit of the device.

        Args:
            circ (SubCircuit): Internal circuit of the Sub-Circuit.
        """
        #set the internal circuit
        self._circuit = circ

        #set the child (inner) nets of the terminals of the sub-device.
        # -> these are known as soon a circuit is build up 
        self._set_terminal_child_nets() 
    
    @property
    def internal_nets(self) -> dict[str, list[Net]]:
        """Maps the internal-terminal nets to the external nets connected to the device.

        ```
        Outer circuit       | SubDevice
                            |
             external Net   |  internal Net
                       o----|----
                            |
                            |
        ```
        Returns:
            dict: key: Name of the external net connected to terminal, value: Net object of the internal net

        Example:

            Sub-circuit definition:
                .subckt inverter Vdd Vss in out

                -> Terminal names == Terminal nets: Vdd, Vss, in, out

            Sub-circuit call:
                xinv VPWR VGND A Y inverter

            Resulting map:
                { 
                  'VPWR' : Net(Vdd),
                  'VGND' : Net(Vss),
                  'A'  : Net(in),
                  'Y' : Net(out)
                }
        """
        nets = {}
        
        #get a list of the internal nets, which are connected to the terminals
        terminal_nets = list(self._circuit.terminal_nets.values())

        #iterate over the terminal names, and the terminal net names
        for internal_net_name, outer_net_name in zip(self._terminal_names, self._terminal_nets):
            #the terminal names are the names of the devices pins
            #the terminal net names are the names of the external net connected to the devices pin
            
            #get the internal net
            internal_net = self._circuit.terminal_nets[internal_net_name]

            if outer_net_name in nets:
                #if the outer-net is already in the dict,
                #append the internal net
                # -> at least two device pins are connected with the same external net
                nets[outer_net_name].append(internal_net)
            else:
                #add the net to the dict.
                nets[outer_net_name] = [internal_net]

        return nets

    def internal_to_terminal_net(self, net : Net) -> Net|None:
        """Get the external terminal net connected to the internal net <net>. 

        Args:
            net (Net): Internal net.

        Returns:
            Net or None: Terminal net if internal net is connected to a terminal, else None
        """
        #iterate over the external net names and the corresponding internal nets
        for (external_net_name, internal_net) in self.internal_nets.items():
            if internal_net == net:
                #if the net is the searched internal
                #return the external net
                return self.nets[external_net_name]
        
        return None
    
    
    def _setup_terminals(self):
        """Setup terminals for the SubDevice.
            A SubDevice terminal connects the 
            external net connected to the devices pin, with the internal
            net used in the corresponding sub-circuit.
        """
        #iterate over the terminal names
        for net in self._terminal_names:
            #setup a SubDevicePin for each terminal-name
            self._terminals[net] = SubDevicePin(net, self)

    def _update_terminals_from_circuit(self):
        """Update the terminals dict, such that the name of the terminal is equal 
        to the terminal name specified in the sub-circuit definition.
        """
        new_terminal_dict = OrderedDict()
        for (new_name, terminal) in zip(self._circuit._terminal_net_keys, self._terminals):
            terminal.update_name(new_name)
            new_terminal_dict[new_name] = terminal
        
        self._terminals = new_terminal_dict

    def _set_terminal_child_nets(self):
        """Set the child (inner) nets of the terminals.
        """

        #iterate over the terminals and the inner nets connected to the them.
        for (term, inner_net) in zip(self._terminals.values(), self._circuit.terminal_nets.values()):
            assert isinstance(term, SubDevicePin)
            #set the child net of the terminal as the inner net
            term.set_child_net(inner_net)
    
    def _gen_placement_rules(self):
        rules = []
        #generate for each rule of the inner cells a new MacroSpacing-rule
        #iterate over each inner-cell of the devices macro-cell
        for cell in self.cell.cells:
            #if the cell has placement rules
            if cell.placement_rules: 
                #iterate over the rules
                for rule in cell.placement_rules.rules:
                    
                    #get the internal net, if there is one
                    try:
                        internal_net = rule.net
                    except:
                        internal_net = None 
                    
                    #map the internal net to the terminal net
                    if internal_net:
                        terminal_net = self.internal_to_terminal_net(internal_net)
                    else:
                        terminal_net = None
                    
                    #make a new rule
                    rules.append(PlacementRules.MacroSpacing(cell=self.cell, cell_spacing=rule, net=None))
        
        #generate placement rules from the rules
        if rules:
            self._placement_rules = PlacementRules.PlacementRules(cell=self.cell, rules=rules)
        
        super()._gen_placement_rules()
    
    @staticmethod
    def get_N_Terminals(spice_description : str) -> int:
        """Get the number of terminals.

        Args:
            spice_description (str): spice line of the sub-circuit device call
                                        E.g. X<name> node node .... <sub-circuit-name> <ident>=<value> <ident>=<value> ....
        Returns:
            int : number of terminals
        """
        splitted = spice_description.split()

        n_params = 0
        #get the number of parameters
        for (p) in reversed(splitted):
            if "=" in p:
                #parameter
                n_params += 1
            else:
                break
        
        #return the number of terminals
        return len(splitted)-n_params-2

    @staticmethod
    def get_model(spice_description : str) -> str:
        """Get the model/sub-circuit name of the device.

        Args:
            spice_description (str): Spice description of the device.
                                        E.g. X<name> node node .... <sub-circuit-name> <ident>=<value> <ident>=<value> ....
        Returns:
            str: model
        """

        model = spice_description.split()[1+SubDevice.get_N_Terminals(spice_description)]

        return model