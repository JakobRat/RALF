# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 18:37:30 2023

@author: jakob
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SchematicCapture.Circuit import Circuit
    from SchematicCapture.Primitives import DifferentialPair
    from SchematicCapture.Devices import MOS, ThreeTermResistor, Capacitor

from SchematicCapture.Devices import SubDevice, PrimitiveDevice


import os

class Magic:
    """Class to generate Magic commands.
    """
    def __init__(self, circuit : Circuit):
        """Setup the Magic class, to generate commands for the circuit.

        Args:
            circuit (Circuit): Circuit for which commands shall be generated.
        """
        self._circuit = circuit
        
    @staticmethod
    def gen_sky130_fd_pr__nfet_01v8(d : MOS) -> str:
        """ 
            Generate a nfet.

        Args:
            d (MOS): MOS which shall be generated.
        
        Returns:
            str: Command to generate a sky130_fd_pr__nfet_01v8 in Magic.
        """
        #check the model
        if not (d.model=="sky130_fd_pr__nfet_01v8"):
            raise ValueError("Model not supported!")
        
        #get the parameters
        W = d.parameters["W"]
        L = d.parameters["L"]
        nf = d.parameters["nf"]
        m = d.parameters["m"]
        
        #try to get cell parameters
        try:
            guard = int(d.cell_parameters["guard"])
        except:
            guard = 1

        try:
            glc = int(d.cell_parameters["glc"])
        except:
            glc = 0

        try:
            grc = int(d.cell_parameters["grc"])
        except:
            grc = 0        
        
        try:
            gtc = int(d.cell_parameters["gtc"])
        except:
            gtc = 0

        try:
            gbc = int(d.cell_parameters["gbc"])
        except:
            gbc = 1
        
        try:
            topc = int(d.cell_parameters["topc"])
        except:
            topc = 1
        
        try:
            botc = int(d.cell_parameters["botc"])
        except:
            botc = 0

        #calculate the width per finger
        w_per_finger = round(W/nf,2)            

        #generate the command
        command = (
            '::sky130::sky130_fd_pr__nfet_01v8_draw {'
            f'w {str(w_per_finger)} l {str(L)} m {str(m)} nf {str(nf)}'
            f' diffcov 100 polycov 100'
            f' guard {str(guard)} glc {str(glc)} grc {str(grc)} gtc {str(gtc)} gbc {str(gbc)}'
            ' tbcov 100 rlcov 100'
            f' topc {str(topc)} botc {str(botc)}'
            ' poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 full_metal 1 viasrc 0 viadrn 0 viagate 0'
            ' viagb 0 viagr 0 viagl 0 viagt 0}'
        )
        return command
    
    @staticmethod
    def gen_sky130_fd_pr__pfet_01v8(d : MOS) -> str:
        """ 
            Generate a pfet.

        Args:
            d (MOS): MOS which shall be generated.
        
        Returns:
            str: Command to generate a sky130_fd_pr__pfet_01v8 in Magic.
        """
        
        #check the model
        if not (d.model == "sky130_fd_pr__pfet_01v8"):
            raise ValueError("Model not supported!")

        #get the parameters
        W = d.parameters["W"]
        L = d.parameters["L"]
        nf = d.parameters["nf"]
        m = d.parameters["m"]

        #calc the width per finger
        w_per_finger = round(W/nf,2)

        #try to get the cell parameters
        try:
            guard = int(d.cell_parameters["guard"])
        except:
            guard = 1

        try:
            glc = int(d.cell_parameters["glc"])
        except:
            glc = 0

        try:
            grc = int(d.cell_parameters["grc"])
        except:
            grc = 0        
        
        try:
            gtc = int(d.cell_parameters["gtc"])
        except:
            gtc = 0

        try:
            gbc = int(d.cell_parameters["gbc"])
        except:
            gbc = 1
        
        try:
            topc = int(d.cell_parameters["topc"])
        except:
            topc = 1
        
        try:
            botc = int(d.cell_parameters["botc"])
        except:
            botc = 0

        #generate the command
        command = (
            '::sky130::sky130_fd_pr__pfet_01v8_draw {'
            f'w {str(w_per_finger)} l {str(L)} m {str(m)} nf {str(nf)}'
            f' diffcov 100 polycov 100'
            f' guard {str(guard)} glc {str(glc)} grc {str(grc)} gtc {str(gtc)} gbc {str(gbc)}'
            ' tbcov 100 rlcov 100'
            f' topc {str(topc)} botc {str(botc)}'
            ' poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 full_metal 1 viasrc 0 viadrn 0 viagate 0'
            ' viagb 0 viagr 0 viagl 0 viagt 0}'
        )
        return command
    
    @staticmethod
    def gen_sky130_fd_pr__res_xhigh_po_0p35(d : ThreeTermResistor) -> str:
        """ 
            Generate a poly-resistor.

        Args:
            d (ThreeTermResistor): Poly-resistor which shall be generated.
        
        Returns:
            str: Command to generate a sky130_fd_pr__res_xhigh_po_0p35 in Magic.
        """
        
        #check the model
        if not(d.model == "sky130_fd_pr__res_xhigh_po_0p35"):
            raise ValueError("Model not supported!")
        
        #set the width
        W = 0.35
        L = d.parameters["L"]
        m = d.parameters["m"]
        
        #try to get the cell parameters
        try:
            guard = int(d.cell_parameters["guard"])
        except:
            guard = 1

        try:
            glc = int(d.cell_parameters["glc"])
        except:
            glc = 0

        try:
            grc = int(d.cell_parameters["grc"])
        except:
            grc = 0        
        
        try:
            gtc = int(d.cell_parameters["gtc"])
        except:
            gtc = 0

        try:
            gbc = int(d.cell_parameters["gbc"])
        except:
            gbc = 1

        #command = """::sky130::sky130_fd_pr__res_xhigh_po_0p35_draw {w """ + str(W) +\
        #    " l " + str(L) + " m 1 nx " + str(m) +\
        #    """ wmin 0.350 lmin 0.50  rho 2000 val 2875.143 dummy 0 """+\
        #    """dw 0.0 term 188.2  sterm 0.0 caplen 0 wmax 0.350  guard 1 glc 0 grc 0 gtc 0 gbc 1  """+\
        #    """compatible {sky130_fd_pr__res_xhigh_po_0p35  sky130_fd_pr__res_xhigh_po_0p69 sky130_fd_pr__res_xhigh_po_1p41  """+\
        #    """sky130_fd_pr__res_xhigh_po_2p85 sky130_fd_pr__res_xhigh_po_5p73}  """+\
        #    """snake 0 full_metal 0 n_guard 0 hv_guard 0 vias 0  viagb 0 viagt 0 viagl 0 viagr 0} """
        
        #generate the command
        command = (
            '::sky130::sky130_fd_pr__res_xhigh_po_0p35_draw {'
            f'w {str(W)} l {str(L)} m 1 nx {str(m)} '
            'wmin 0.350 lmin 0.50  rho 2000 val 2875.143 dummy 0 dw 0.0 term 188.2  sterm 0.0 caplen 0 wmax 0.350 '
            f'guard {guard} glc {glc} grc {grc} gtc {gtc} gbc {gbc} '
            'compatible {sky130_fd_pr__res_xhigh_po_0p35  sky130_fd_pr__res_xhigh_po_0p69 sky130_fd_pr__res_xhigh_po_1p41 '
            'sky130_fd_pr__res_xhigh_po_2p85 sky130_fd_pr__res_xhigh_po_5p73}  '
            'snake 0 full_metal 0 n_guard 0 hv_guard 0 vias 0  viagb 0 viagt 0 viagl 0 viagr 0} '
        )
        return command
    
    @staticmethod
    def gen_sky130_fd_pr__cap_mim_m3_1(d : Capacitor) -> str:
        """Generate a capacitor.

        Args:
            d (Capacitor): Device which shall be generated.

        Raises:
            ValueError: If the model isn't 'sky130_fd_pr__cap_mim_m3_1'

        Returns:
            str: Command to generate a 'sky130_fd_pr__cap_mim_m3_1'.
        """
        
        #check the model
        if not(d.model == "sky130_fd_pr__cap_mim_m3_1"):
            raise ValueError("Model not supported!")
        
        W = d.parameters["W"]
        L = d.parameters["L"]
        m = d.parameters["m"]
        
        #generate the command
        command = "::sky130::sky130_fd_pr__cap_mim_m3_1_draw { w " + str(W) + " l " + str(L) + " nx " + str(m) + " ny 1 }" 

        return command
    
    @staticmethod
    def gen_sky130_fd_pr__cap_mim_m3_2(d : Capacitor) -> str:
        """Generate a capacitor.

        Args:
            d (Capacitor): Device which shall be generated.

        Raises:
            ValueError: If the model isn't 'sky130_fd_pr__cap_mim_m3_2'

        Returns:
            str: Command to generate a 'sky130_fd_pr__cap_mim_m3_2'.
        """
        #check the model
        if not(d.model == "sky130_fd_pr__cap_mim_m3_2"):
            raise ValueError("Model not supported!")
        
        W = d.parameters["W"]
        L = d.parameters["L"]
        m = d.parameters["m"]
        
        #generate the command
        command = "::sky130::sky130_fd_pr__cap_mim_m3_2_draw { w " + str(W) + " l " + str(L) + " nx " + str(m) + " ny 1 }" 

        return command
    
    @staticmethod
    def magic_gen_device(d : PrimitiveDevice) -> str:
        """Generate a device in Magic.

        Args:
            d (PrimitiveDevice): Primitive device which shall be generated.

        Raises:
            ValueError: If the device isn't supported.

        Returns:
            str: Command to generate the device in magic.
        """
        
        if d.model == "sky130_fd_pr__nfet_01v8":
            return Magic.gen_sky130_fd_pr__nfet_01v8(d)
        elif d.model == "sky130_fd_pr__pfet_01v8":
            return Magic.gen_sky130_fd_pr__pfet_01v8(d)
        elif d.model == "sky130_fd_pr__res_xhigh_po_0p35":
            return Magic.gen_sky130_fd_pr__res_xhigh_po_0p35(d)
        elif d.model == "sky130_fd_pr__cap_mim_m3_1":
            return Magic.gen_sky130_fd_pr__cap_mim_m3_1(d)
        elif d.model == "sky130_fd_pr__cap_mim_m3_2":
            return Magic.gen_sky130_fd_pr__cap_mim_m3_2(d)
        elif type(d) is SubDevice:
            return ""
        else:
            raise ValueError("Device not supported!")
    
    
    @staticmethod
    def place_device(d : PrimitiveDevice) -> str:
        """
            Place the device in magic.

        Args:
            d (PrimitiveDevice): Device which shall be placed.
        
        Raises:
            ValueError: If the device has no cell-view.
            ValueError: If the magic path of the cell can't be found.
            ValueError: If the cell has a rotation other than [0,90,180,270].
        
        Returns:
            str: Command to place the devices cell.
        """
        #check if the device has a cell-view
        if d.cell is None:
            raise ValueError(f"Cell view of device {d.name} not available!")
        
        cell = d.cell
        
        if cell.path:
            #if os.path.isfile(cell.path):
            #    pass
            #else:
            #    raise FileNotFoundError(f"Cell for device {d.name} not found under {cell.path}!")
            pass
        else:
            raise ValueError(f"Cell for device {d.name} has no magic-cell!")
        
        #get the coordinates of the cell
        center = cell.center_point
        rotation = cell.rotation
        if rotation not in [0, 90, 180, 270]:
            raise ValueError("Not a manhatten rotation.")

        #generate the command
        command = []
        
        """command.append(f"box {center[0]} {center[1]} {center[0]} {center[1]}")
        if isinstance(d, SubDevice):
            if rotation == 0:
                command.append(f"getcell {cell.path} child 0 0")
            else:
                command.append(f"getcell {cell.path} {rotation} 0 0 child 0 0")
        else:
            if rotation == 0:
                command.append(f"getcell {cell.path} child 0 0")
                #command.append(f"flatten -doinplace")
            else:
                command.append(f"getcell {cell.path} {rotation} 0 0 child 0 0")
                #command.append(f"flatten -doinplace")"""
        
        #add the path of the cell to the search path
        command.append(f"path search +{cell.path}")
        
        #get the cell at position (0,0)
        command.append(f"box 0 0 0 0")
        command.append(f"getcell {d.name} child 0 0")
        
        #rotatet the cell around (0,0)
        if not rotation == 0:
            command.append(f"rotate {rotation} -origin")
        
        #move the cell
        command.append(f"move {center[0]} {center[1]}")
        
        #if the device is a primitive device, flatten the cell
        #if isinstance(d,PrimitiveDevice): 
        #    command.append(f"flatten -doinplace")
        return command
    
    def place_circuit(self, name : str, path='Magic/Placement/') -> list[str]:
        """Generates the commands to place the placed cells of the circuit.

        Args:
            name (str): Name of the top-cell and .mag file.
            path (str): Path of the resulting placement.
        Returns:
            list[str]: Commands to place devices.
        """
        commands = []
        commands.append(f"save {path}{name}")

        #for (d_name, d) in self._circuit.devices.items():
        #    if d.cell.placed:
        #        commands.extend(Magic.place_device(d))
        
        commands.extend(Magic._place_all_cells(self._circuit))
        commands.append("select top cell")
        commands.append("save")
        commands.append("quit -noprompt")
        
        return commands

    @staticmethod
    def _place_all_cells(circ : Circuit) -> list[str]:
        """Place all cells of Circuit <circ>.

        Args:
            circ (Circuit): Circuit which shall be placed.

        Returns:
            list[str]: Commands to place the circuit.
        """
        commands = []
        #iterate over the devices
        for (d_name, d) in circ.devices.items():
            if type(d) is SubDevice:
                try:
                    #try to place the subdevice as a macrocell
                    commands.extend(Magic.place_device(d))
                except:
                    #flat the cell and place all devices separate
                    commands.extend(Magic._place_all_cells(d._circuit))
            else:
                commands.extend(Magic.place_device(d))
        return commands
    
    def gen_devices(self) -> str:
        """Generate the devices for the circuit.

        Returns:
            str: Commands to generate devices for the circuit.
        """
        commands = []
        
        for (d_name, d) in self._circuit.devices.items():
            if type(d) != SubDevice:
                commands.append(f"load {d_name} -silent -quiet")
                commands.append("box 0 0 0 0")
                commands.append(Magic.magic_gen_device(d))
                commands.append(f"select cell {d_name}")
                commands.append(f"save {d_name}")
                #commands.append("writeall force")
        
        commands.append("quit -noprompt")
            
        return commands
    
         