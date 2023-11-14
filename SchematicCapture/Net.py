# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 11:44:03 2023

@author: jakob
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SchematicCapture.Devices import Device
    from SchematicCapture.Circuit import Circuit, SubCircuit
    from Rules.NetRules import NetRule
    from SchematicCapture.Ports import SubDevicePin
    from Magic.MagicTerminal import MagicTerminal
    from Magic.MagicDie import MagicDiePin

from SchematicCapture.Devices import SubDevice, PrimitiveDevice

class Net:
    """Class to store a net.
        A net connects multiple devices terminals/pins in a circuit.
    """
    def __init__(self, name : str, circuit : Circuit):
        """Setup a net.

        Args:
            name (str): Name of the net.
            circuit (Circuit): Circuit to which the net belongs.

        Raises:
            ValueError: If the name, isn't a str.
        """
        if not type(name)==str:
            raise ValueError
        
        self._name = name
        self._circuit = circuit
        
        #store the child-nets
        self._child_nets : list[SubNet]
        self._child_nets = []

        #store the devices connected to the net
        self._devices : dict[str, Device]
        self._devices = {}

        #store the die-pins connected to the net
        self._die_pins = []

        #setup a dict for net-features
        self._features = {
            "HPWL" : None,
            "N_devices": None,
        }

        #setup a set for net-rules
        self._rules = set()
        
    def add_device(self, device : Device):
        """Add a device to the net.

        Args:
            device (Device): Device to be added.
        """
        #add the device to the devices dict
        self._devices[device._name] = device

        #check if the device is a SubDevice
        if isinstance(device, SubDevice):
            # If the device is a SubDevice
            # there are internal nets which are
            # connected to this net, through
            # the devices terminal.
            
            # Try to get the internal net.
            try:
                sub_net = device.internal_nets[self.name]
            except:
                sub_net = None
            
            if sub_net:
                # If there are internal nets, which are 
                # connected to this net, through the devices terminals.
                # Add them as child-nets too this net
                for net in sub_net:
                    self.add_child_net(sub_net)
                
    def add_child_net(self, sub_net : SubNet|list[SubNet]):
        """Add a child net, which is connected through a SubDevice terminal with this net.

        Args:
            sub_net (SubNet|list[SubNet]): SubNet/list of Subnets connected with the net.
        """
        if type(sub_net)==list:
            #iterate over the nets in the list
            for net in sub_net:
                #set the parent of the child net as this net
                net.set_parent_net(self)
                self._child_nets.append(net) #add the net
        else:
            #set the parent of the child net as this net
            sub_net.set_parent_net(self) 
            self._child_nets.append(sub_net) #add the net

    def add_rule(self, rule : NetRule):
        """Add a net-rule to the net.

        Args:
            rule (NetRule): NetRule which shall be added.
        """
        self._rules.add(rule)
    
    def add_die_pin(self, pin : MagicDiePin):
        """Add a die-pin to the net.

        Args:
            pin (MagicDiePin): Die pin which shall be added.
        """
        if not (pin in self._die_pins):
            #if the pin is not already registered in the die-pins
            self._die_pins.append(pin)
    
    @property
    def name(self) -> str:
        """Get the name of the net.

        Returns:
            str: Name of the net.
        """
        return self._name

    @property
    def rules(self) -> list[NetRule]:
        """Get all rules which apply to the net.

        Returns:
            list[NetRule]: List containing all net-rules.
        """
        return list(self._rules)
    
    @property
    def die_pins(self) -> list[MagicDiePin]:
        """Get a list with the die-pins connected to the net.

        Returns:
            list[MagicDiePin]: List of die-pins connected to the net.
        """
        return self._die_pins

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Net) and (self._name == __value._name) and (self._circuit == __value._circuit)

    def __hash__(self) -> int:
        return hash(self._name)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(circuit={self._circuit}, name={self.name})"
    
    @property
    def devices(self) -> dict[str, Device]:
        """Get the devices connected to the net.

        Returns:
            dict[str, Device]: key: Device name, value: Device instance
        """
        return self._devices
        
    @property
    def features(self) -> dict[str, float]:
        """Get the features of the net.

        Returns:
            dict: key: Feature name, value: Feature value
        """
        self._features["HPWL"] = self.HPWL()
        self._features["N_devices"] = len(self._devices.keys())
        
        return self._features
    
    @property
    def feature_list(self) -> list[float]:
        """Get a list of the net-features.

        Returns:
            list(float): Net-features.
        """
        feature_list = list(self.features.values())
        return feature_list
    
    @property
    def child_nets(self) -> list[SubNet]:
        """Get the nets, connected to the net through SubDevices.

        Returns:
            list[SubNet]: Nets connected with this net.
        """
        return self._child_nets
    
    def set_name(self, name : str):
        """Set the name of the net.

        Args:
            name (str): Name of the net.
        """
        self._name = name

    def feature_list_between(self, device1 : Device, device2 : Device) -> list[float]:
        """Get a feature list for the net, between device1 and device2.

        Args:
            device1 (Device): First device.
            device2 (Device): Second device.

        Returns:
            list: [HPWL, Area]
                HPWL : w+h, Half-perimeter-wire-length between device1 (D1) and device2 (D2). 
                Area : w*h, Area spanned by the devices pins connected to the net.
                        
                        w
            D1   <------------->
                x---------------- 
                                |
                                |   h
                                |
                                x 
                                  D2
        """
        assert (device1.name in self.devices) and (device2.name in self.devices)

        #get the bounding-box between the devices-terminals
        bound = self.bounding_box_between(device1, device2)
        
        #calculate HPWL and Area
        w = bound[2]-bound[0]
        h = bound[3]-bound[1]
        feature_list = [w+h, w*h]
        return feature_list

    def get_MagicTerminals(self, only_primitive = False) -> dict[str, MagicTerminal]:
        """Get all MagicTerminals connected to the net.

        Args:
            only_primitive (bool): If True, only the terminals of primitive devices will be returned. Otherwise all.

        Returns:
            dict: key: device_name.terminal_name, value: MagicTerminal object
        """
        terminals = {}

        #iterate over each device
        for d in self._devices.values():
            if only_primitive:
                if not isinstance(d, PrimitiveDevice):
                    #if the device isn't a PrimitiveDevice,
                    #skip this device
                    continue

            #iterate over the terminals which are connected with this net
            for term in d.cell.terminals_connected_to_net(self):
                #add the terminal to the terminals dict
                terminals[f"{d.name}.{term.name}"] = term

        return terminals
    
    def bounding_box_between(self, device1 : Device, device2 : Device) -> tuple[float, float, float, float]:
        """Get the bounding box of the terminals of device1 and device2 connected to the net.

        Args:
            device1 (Device): First device
            device2 (Device): Second device

        Raises:
            ValueError: If at least one of the device isn't connected to the net.

        Returns:
            tuple: (min_x, min_y, max_x, max_y)
        """
        assert (device1.name in self.devices) and (device2.name in self.devices)
        
        min_x = 0
        max_x = 0
        min_y = 0
        max_y = 0
        init = False

        #iterate over the devices
        for d in [device1, device2]:
            #iterate over the terminals connected to the net
            for term in d.cell.terminals_connected_to_net(self):
                #get the bounding box of the terminal
                try:
                    bound = term.bounding_box
                except:
                    raise ValueError("Device has no cell!")
                
                #track the minimum and maximum values of the bounding box
                #to get a bounding box, which includes each terminals 
                #bounding box
                if init:
                    min_x = min(min_x, bound[0])
                    max_x = max(max_x,  bound[2])
                    
                    min_y = min(min_y, bound[1])
                    max_y = max(max_y,  bound[3])
                else:
                    min_x = bound[0]
                    max_x = bound[2]

                    min_y = bound[1]
                    max_y = bound[3]
                    init = True

        return (min_x, min_y, max_x, max_y)
    
    def bounding_box(self) -> tuple[float, float, float, float]:
        """Get the bounding box of the net, defined by the outermost
            pins.

        Raises:
            ValueError: If a device has no cell-view.

        Returns:
            tuple: (xmin, ymin, xmax, ymax)
        """
        min_x = 0
        max_x = 0
        min_y = 0
        max_y = 0
        init = False

        #if there are more then one devices
        if len(self._devices.keys())>1:
            #iterate over the devices
            for d in list(self._devices.values()):
                #iterate over the terminals connected to the net
                for term in d.cell.terminals_connected_to_net(self):
                    #get the bounding box of the terminal
                    try:
                        bound = term.bounding_box
                    except:
                        raise ValueError("Device has no cell!")
                    
                    #track the minimum and maximum values of the bounding box
                    #to get a bounding box, which includes each terminals 
                    #bounding box
                    if init:
                        min_x = min(min_x, bound[0])
                        max_x = max(max_x,  bound[2])
                        
                        min_y = min(min_y, bound[1])
                        max_y = max(max_y,  bound[3])
                    else:
                        min_x = bound[0]
                        max_x = bound[2]

                        min_y = bound[1]
                        max_y = bound[3]
                        init = True
        elif len(self._devices)==1:

            device = list(self._devices.values())[0]
            #iterate over the terminals connected to the net
            for term in device.cell.terminals_connected_to_net(self):
                #try to get the bounding box
                try:
                    bound = term.bounding_box
                except:
                    raise ValueError("Device has no cell!")
                
                #track the minimum and maximum values of the bounding box
                #to get a bounding box, which includes each terminals 
                #bounding box
                if init:
                    min_x = min(min_x, bound[0])
                    max_x = max(max_x,  bound[2])
                    
                    min_y = min(min_y, bound[1])
                    max_y = max(max_y,  bound[3])
                else:
                    min_x = bound[0]
                    max_x = bound[2]

                    min_y = bound[1]
                    max_y = bound[3]
                    init = True
        
        return (min_x, min_y, max_x, max_y)

    def HPWL(self) -> float:
        """Get the HPWL of the net, defined by the outermost pins.

        Raises:
            ValueError: If a device has no cell-view.

        Returns:
            float: HPWL
        """
        #get the bounding box of the net
        min_x, min_y, max_x, max_y = self.bounding_box()

        #calculate the HPWL
        hpwl = (max_x-min_x) + (max_y-min_y)

        #add distances to die-pins
        pin : MagicDiePin
        for pin in self._die_pins:
            c = pin.coordinate
            #add the minimum distance, between
            #the lower-left or upper-right corner of the bounding box
            #and the pin, to the HPWL
            l = min(abs(c[0]-min_x)+abs(c[1]-min_y),
                    abs(c[0]-max_x)+abs(c[1]-max_y))
            hpwl += l        
        
        return hpwl

class SubNet(Net):
    """Class to store a sub-net.
        A sub-net is a net, which is inside a sub-circuit (respectively a sub-device).
    """
    def __init__(self, name : str, circuit : SubCircuit, parent_device : SubDevice, parent_net : Net = None):
        """A SubNet is a net within a sub-circuit device.

        Args:
            name (str): Name of the net.
            circuit (SubCircuit): SubCircuit to which the net belongs.
            parent_device (SubDevice): SubDevice to which the net belongs.
            parent_net (Net, optional): Parent net to which the SubNet is connect. (E.g. through the terminals of the SubDevice.) Defaults to None.
        """

        super().__init__(name, circuit)
        
        self._parent_device = parent_device
        self._parent_net = parent_net
        
        if parent_net:
            #if a parent net were specified, register the child net at the parent net
            parent_net.add_child_net(self)


    @property
    def parent_net(self) -> Net|SubNet|None:
        """Get the net, which is connected through a sub-device terminal with the sub-net.

        Returns:
            Net|SubNet|None: Net connected with the sub-net, if there is a parenting net.
        """
        return self._parent_net
    
    @property
    def parent_device(self) -> SubDevice:
        """Get the SubDevice, to which the SubNet belongs.

        Returns:
            SubDevice: SubDevice in which the SubNet is instantiated.
        """
        return self._parent_device

    def set_parent_net(self, parent_net : Net|SubNet):
        """Set the parent-net of the SubNet.

        Args:
            parent_net (Net|SubNet): Net connected with the sub-net.
        """
        self._parent_net = parent_net

    def __eq__(self, __value: object) -> bool:
        return (super().__eq__(__value) and 
            isinstance(__value, SubNet) and 
            (self._parent_device == __value._parent_device))
    
    def __hash__(self) -> int:
        return super().__hash__()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, circuit={self._circuit},device={self.parent_device})"
    

def get_root_net(net : SubNet) -> Net:
    """Get the root net of net <net>.

    Args:
        net (SubNet): Net for which the root is searched.

    Returns:
        Net: Root net. (Net on topological highest place.)
    """
    if type(net) == SubNet: #if the net is a subnet
        if not (net.parent_net is None): #if the net has a parent
            return get_root_net(net.parent_net) #get the root net of the parent net
        else:
            #sub-net has no parent -> root net
            return net
    else: #if the net is a Net, -> there is no parent
        return net

def same_root_net(net1 : Net, net2 : Net) -> bool:
    """Check if two nets share the same root net.

    Args:
        net1 (Net): First net.
        net2 (Net): Second net.

    Returns:
        bool: True, if the nets have the same root net, otherwise False.
    """
    root1 = get_root_net(net1)
    root2 = get_root_net(net2)

    return root1 == root2