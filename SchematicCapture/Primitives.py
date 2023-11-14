
from Rules.RoutingRules import RoutingRule
from SchematicCapture.Devices import NTermDevice, SUPPORTED_DEVICES, PrimitiveDevice
from PDK.PDK import global_pdk
import Rules.PlacementRules as PlacementRules
from SchematicCapture.Ports import Pin
import abc

SUPPORTED_PRIMITIVES = {
    'DifferentialPair' : 'Circuits/Primitives/DiffPair/',
    'DifferentialLoad' : 'Circuits/Primitives/DiffLoad/',
    'CrossCoupledPair' : 'Circuits/Primitives/CrossCoupledPair/',
}

class PrimitiveDeviceComposition(PrimitiveDevice, metaclass=abc.ABCMeta):
    """Class for a primitive device composition.
        A primitive device composition is a combination of multiple primitive devices.
        E.g. a differential pair is a composition of two MOS. 
    """
    def __init__(self, devices : list[PrimitiveDevice], spice_description : str, N_Terminals : int, name_suffix='', use_dummies = False):
        """Setup a primitive device composition.

        Args:
            devices (list[PrimitiveDevice]): Devices of the composition.
            spice_description (str): Spice description of the composition.
            N_Terminals (int): Number of terminals of the composition.
            name_suffix (str, optional): Name suffix of the device. Defaults to ''.
        """

        #store the composed devices
        self._devices = devices

        #check if the devices share the same model
        model = devices[0].model
        for device in devices:
            assert device.model == model, f"Primitive device composition, with unequal models detected!"
        
        #setup a primitive device 
        super().__init__(spice_description, N_Terminals, name_suffix, use_dummies)

        #set the model of the device
        self._model = model

    @property
    def devices(self) -> list[PrimitiveDevice]:
        """Get a list of the composed devises.

        Returns:
            list[PrimitiveDevice]: List of devices.
        """
        return self._devices

class DifferentialPair(PrimitiveDeviceComposition):
    """A differential pair is the composition of two MOS which share their source-terminals.
    """
    def __init__(self, devices : list[PrimitiveDevice], use_dummies = False):
        """Setup a differential pair.

        Args:
            devices (list[PrimitiveDevice]): Devices which form the differential pair.
            use_dummies (bool, optional): If the device shall use dummies. Defaults to False.
        Raises:
            ValueError: If there are not two devices given.
            ValueError: If they don't share the same model.
            ValueError: If they haven't the same length.
            ValueError: If they haven't the same width.
            ValueError: If they haven't the same number of fingers.
            ValueError: If the multiplier of a device is > 1.
        """
        if len(devices)!=2:
            raise ValueError("Differential pair with more than two devices detected!")
        
        #store the first and second device
        self._d1 = devices[0]
        self._d2 = devices[1]

        if self._d1.model != self._d2.model:
            raise ValueError("Differential pair with unequal models detected!")
        
        #store the model
        model = self._d1.model

        if self._d1.parameters["L"] != self._d2.parameters["L"]:
            raise ValueError("Differential pair with unequal L detected!")
        
        #store the length
        L = self._d1.parameters["L"]

        if self._d1.parameters["W"] != self._d2.parameters["W"]:
            raise ValueError("Differential pair with unequal W detected!")

        #double the width, since the resulting MOS has doubled nf
        W = self._d1.parameters["W"] * 2

        if self._d1.parameters["nf"] != self._d2.parameters["nf"]:
            raise ValueError("Differential pair with unequal L detected!")
        
        #double the number of fingers
        nf = self._d1.parameters["nf"] * 2

        if self._d1.parameters['m'] != 1 or self._d2.parameters['m'] != 1:
            raise ValueError("Differential pair with m>1 detected!")
        
        
        #get the terminal nets of the MOSFETs
        nets1 = self._d1.terminal_nets
        nets2 = self._d2.terminal_nets

        N_Terminals = 6
        #generate a spice description of the differential pair.

        if use_dummies:
            #spice description with dummy fingers
            spice_description = f"XDP_{self._d1.name_without_suffix}_{self._d2.name_without_suffix} {nets1['D'].name} {nets2['D'].name} {nets1['G'].name} {nets2['G'].name} {nets1['S'].name} {nets1['B'].name} W={W} L={L} nf={nf+2} m=1"
        else:
            #spice description without dummy fingers
            spice_description = f"XDP_{self._d1.name_without_suffix}_{self._d2.name_without_suffix} {nets1['D'].name} {nets2['D'].name} {nets1['G'].name} {nets2['G'].name} {nets1['S'].name} {nets1['B'].name} W={W} L={L} nf={nf} m=1"

        #init the device
        super().__init__(devices=devices, spice_description=spice_description, 
                         N_Terminals=N_Terminals, name_suffix=self._d1._name_suffix,
                         use_dummies=use_dummies)

        #set the model
        self._model = model
        self.add_feature("model", SUPPORTED_DEVICES[self._model])
        
        #set the parameters
        self._parameters = {"L" : None, "W" : None, "nf" : None, "m" : None}
        self._set_params()
        
        #add features
        self.add_feature("L", self._parameters["L"])
        self.add_feature("W", self._parameters["W"])
        self.add_feature("m", self._parameters["m"])
        self.add_feature("nf", self._parameters["nf"])
        
        
    def _setup_terminals(self):
        """ Setup the terminal pins of the device.
            D1 : Drain of first MOS
            D2 : Drain of second MOS
            G1 : Gate of first MOS
            G2 : Gate of second MOS
            S : Source 
            B : Bulk
        """
        for terminal in ["D1","D2","G1","G2","S","B"]:
            self._terminals[terminal] = Pin(terminal, self)

    def _gen_placement_rules(self):
        """Generate placement rules for the differential pair.

        Raises:
            ValueError: If the model isn't a nfet or pfet.
        """
        if 'nfet' in self.model:
            pass
        elif 'pfet' in self.model:
            rule = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("nwell"), net=self.terminal_nets['B'])
            self._placement_rules = PlacementRules.PlacementRules(cell=self.cell, rules=[rule])
        else:
            raise ValueError("No valid model for placement-rule given!")
        
        super()._gen_placement_rules()

    def _generate_routing_rules(self) -> list[RoutingRule]:
        return super()._generate_routing_rules()

class DifferentialLoad(PrimitiveDeviceComposition):
    """A differential load is a composition of two MOS which share a common gate.
    """
    def __init__(self, devices : list[PrimitiveDevice], use_dummies = False):
        """Setup a differential load.

        Args:
            devices (list[PrimitiveDevice]): Devices which form the differential load.
            use_dummies (bool, optional): If the device shall use dummies. Defaults to False.
        Raises:
            ValueError: If there are not two devices given.
            ValueError: If they don't share the same model.
            ValueError: If they haven't the same length.
            ValueError: If they haven't the same width.
            ValueError: If they haven't the same number of fingers.
            ValueError: If the multiplier of a device is > 1.
        """
        if len(devices)!=2:
            raise ValueError("Differential load with more than two devices detected!")
        
        self._d1 = devices[0]
        self._d2 = devices[1]

        if self._d1.model != self._d2.model:
            raise ValueError("Differential load with unequal models detected!")
        
        model = self._d1.model

        if self._d1.parameters["L"] != self._d2.parameters["L"]:
            raise ValueError("Differential load with unequal L detected!")
        
        L = self._d1.parameters["L"]

        if self._d1.parameters["W"] != self._d2.parameters["W"]:
            raise ValueError("Differential load with unequal W detected!")

        W = self._d1.parameters["W"]

        if self._d1.parameters["nf"] != self._d2.parameters["nf"]:
            raise ValueError("Differential load with unequal L detected!")
        
        nf = self._d1.parameters["nf"]

        if self._d1.parameters['m'] != 1 or self._d2.parameters['m'] != 1:
            raise ValueError("Differential load with m>1 detected!")
        
        nets1 = self._d1.terminal_nets
        nets2 = self._d2.terminal_nets

        N_Terminals = 6

        if use_dummies:
            #if dummies shall be used,
            # add dummy fingers
            spice_description = f"XDL_{self._d1.name_without_suffix}_{self._d2.name_without_suffix} {nets1['D'].name} {nets2['D'].name} {nets1['S'].name} {nets2['S'].name} {nets1['G'].name} {nets1['B'].name} W={W} L={L} nf={nf+2} m={2}"
        else:
            spice_description = f"XDL_{self._d1.name_without_suffix}_{self._d2.name_without_suffix} {nets1['D'].name} {nets2['D'].name} {nets1['S'].name} {nets2['S'].name} {nets1['G'].name} {nets1['B'].name} W={W} L={L} nf={nf} m={2}"
        
        super().__init__(devices, spice_description, N_Terminals, name_suffix=self._d1._name_suffix, use_dummies=use_dummies)

        self._model = model
        self.add_feature("model", SUPPORTED_DEVICES[self._model])
        
        self._parameters = {"L" : None, "W" : None, "nf" : None, "m" : None}
        self._set_params()
        
        self.add_feature("L", self._parameters["L"])
        self.add_feature("W", self._parameters["W"])
        self.add_feature("m", self._parameters["m"])
        self.add_feature("nf", self._parameters["nf"])
        
        #set the cell-parameter, that a bottom gate contact shall be generated
        self.set_cell_parameter("botc", 1)
          
    def _setup_terminals(self):
        """ Setup the terminals of the differential load.
            D1 : Drain of first MOS
            D2 : Drain of second MOS
            S1 : Source of first MOS
            S2 : Source of second MOS
            G : Gate 
            B : Bulk
        """
        for terminal in ["D1","D2","S1","S2","G","B"]:
            self._terminals[terminal] = Pin(terminal, self)

    def _gen_placement_rules(self):
        if 'nfet' in self.model:
            pass
        elif 'pfet' in self.model:
            rule = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("nwell"), net=self.terminal_nets['B'])
            self._placement_rules = PlacementRules.PlacementRules(cell=self.cell, rules=[rule])
        else:
            raise ValueError("No valid model for placement-rule given!")
        
        super()._gen_placement_rules()

    def _generate_routing_rules(self) -> list[RoutingRule]:
        return super()._generate_routing_rules()
    
class CrossCoupledPair(PrimitiveDeviceComposition):
    """Class for a CrossCoupledPair.
        A cross-coupled pair is composed of two MOSFETs (M1 & M2),
        where the gate of M1 is connected with the drain of M2 and vice versa.
    """
    def __init__(self, devices : list[PrimitiveDevice], use_dummies=False):
        """Setup a cross coupled pair.

        Args:
            devices (list[PrimitiveDevice]): Devices which form the cross coupled pair.
            use_dummies (bool, optional): If the device shall use dummies. Defaults to False.
        Raises:
            ValueError: If there are not two devices given.
            ValueError: If they don't share the same model.
            ValueError: If they haven't the same length.
            ValueError: If they haven't the same width.
            ValueError: If they haven't the same number of fingers.
            ValueError: If the multiplier of a device is > 1.
        """

        if len(devices)!=2:
            raise ValueError("Cross coupled pair with more than two devices detected!")
        
        self._d1 = devices[0]
        self._d2 = devices[1]

        if self._d1.model != self._d2.model:
            raise ValueError("Cross coupled pair with unequal models detected!")
        
        model = self._d1.model

        if self._d1.parameters["L"] != self._d2.parameters["L"]:
            raise ValueError("Differential load with unequal L detected!")
        
        L = self._d1.parameters["L"]

        if self._d1.parameters["W"] != self._d2.parameters["W"]:
            raise ValueError("Cross coupled pair with unequal W detected!")

        W = self._d1.parameters["W"]

        if self._d1.parameters["nf"] != self._d2.parameters["nf"]:
            raise ValueError("Cross coupled pair with unequal nf detected!")
        
        nf = self._d1.parameters["nf"]

        if self._d1.parameters['m'] != 1 or self._d2.parameters['m'] != 1:
            raise ValueError("Cross coupled pair with m>1 detected!")
        
        nets1 = self._d1.terminal_nets
        nets2 = self._d2.terminal_nets

        N_Terminals = 5
        
        if use_dummies:
            spice_description = f"XCCP_{self._d1.name_without_suffix}_{self._d2.name_without_suffix} {nets1['D'].name} {nets2['D'].name} {nets1['S'].name} {nets2['S'].name} {nets1['B'].name} W={W} L={L} nf={nf+2} m={2}"
        else:
            spice_description = f"XCCP_{self._d1.name_without_suffix}_{self._d2.name_without_suffix} {nets1['D'].name} {nets2['D'].name} {nets1['S'].name} {nets2['S'].name} {nets1['B'].name} W={W} L={L} nf={nf} m={2}"
        
            
        super().__init__(devices, spice_description, N_Terminals, name_suffix=self._d1._name_suffix, use_dummies=use_dummies)

        self._model = model
        self.add_feature("model", SUPPORTED_DEVICES[self._model])
        
        self._parameters = {"L" : None, "W" : None, "nf" : None, "m" : None}
        self._set_params()
        
        self.add_feature("L", self._parameters["L"])
        self.add_feature("W", self._parameters["W"])
        self.add_feature("m", self._parameters["m"])
        self.add_feature("nf", self._parameters["nf"])
        
        #set the cell-parameter, that a bottom gate contact shall be generated
        self.set_cell_parameter("botc", 1)
        
    @property
    def devices(self):
        return self._devices
          
    def _setup_terminals(self):
        for terminal in ["D1","D2","S1","S2","B"]:
            self._terminals[terminal] = Pin(terminal, self)

    
    def _gen_placement_rules(self):
        if 'nfet' in self.model:
            pass
        elif 'pfet' in self.model:
            rule = PlacementRules.Spacing(cell=self.cell, layer=global_pdk.get_layer("nwell"), net=self.terminal_nets['B'])
            self._placement_rules = PlacementRules.PlacementRules(cell=self.cell, rules=[rule])
        else:
            raise ValueError("No valid model for placement-rule given!")
        
        super()._gen_placement_rules()
    
    def _generate_routing_rules(self) -> list[RoutingRule]:
        return super()._generate_routing_rules()
