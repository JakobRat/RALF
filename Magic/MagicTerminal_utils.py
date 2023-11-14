"""
    
    Collection of methods to generate physical terminals for primitive devices.

"""


from __future__ import annotations
from typing import TYPE_CHECKING
from Magic.MagicLayer import Rectangle
from Magic.MagicTerminal import MagicTerminal, MagicPin
from SchematicCapture.Net import Net
from SchematicCapture.Devices import PrimitiveDevice, MOS, Capacitor, ThreeTermResistor
from SchematicCapture.Primitives import DifferentialLoad, CrossCoupledPair, DifferentialPair
from SchematicCapture.RString import RString

import networkx as nx

if TYPE_CHECKING:
    from Magic.Cell import Cell

from PDK.PDK import global_pdk
import copy
import math

def get_terminals_MOS(cell : Cell) -> MagicTerminal:
    """Get the physical terminals of a MOS.

    Args:
        cell (Cell): Cell-view of a MOS.

    Raises:
        ValueError: If the rotation of the cell isn't 0.
        
    Returns:
        MagicTerminal: Physical terminal of the device.
    """
    
    device = cell.device
    assert type(device)==MOS, f"Device isn't a MOS!"
    assert device.parameters['m']==1, f"Device isn't build up by a single MOS!"

    #get the rotation of the cell
    rot = cell.rotation

    if rot != 0:
        raise ValueError(f"Rotation angle of cell other than 0 not supported! ({cell})")
    
    if 'botc' in device.cell_parameters:
        if device.cell_parameters['botc']:
            raise ValueError("Bottom gate-contact for a single MOS not supported!")
        
    #get the rectangles which form the gate
    gate_rects = cell.get_overlapping_rectangles('polycont', 'poly')
    gate_rects = merge_rects2(gate_rects)
    
    assert len(gate_rects) == device.parameters['nf'], "Number of devices gates, and found gates don't match!"
    
    #if rot ==0 or rot == 180:
    #    gate_rects = merge_rects(gate_rects, direction=1)
    #else:
    #    gate_rects = merge_rects(gate_rects, direction=0)

    #get the drain/source and bulk rectangles
    if 'pmos' in cell._layer_stack:
        drain_source_rects = cell.get_overlapping_rectangles('pdiffc', 'pdiff')
        bulk_rects = cell.get_overlapping_rectangles('nsubdiffcont', 'locali')
    else:
        drain_source_rects = cell.get_overlapping_rectangles('ndiffc', 'ndiff')
        bulk_rects = cell.get_overlapping_rectangles('psubdiffcont', 'locali')

    #merge and sort the drain/source and bulk rectangles
    if rot == 0 or rot==180:
        #drain_source_rects = merge_rects(drain_source_rects, direction=1)
        drain_source_rects = merge_rects2(drain_source_rects)
        drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : rectangles.bounding_box[0])
        #bulk_rects = merge_rects(bulk_rects, direction=1)
        bulk_rects = merge_rects2(bulk_rects)
    else:
        #drain_source_rects = merge_rects(drain_source_rects, direction=0)
        drain_source_rects = merge_rects2(drain_source_rects)
        drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : rectangles.bounding_box[1])
        #bulk_rects = merge_rects(bulk_rects, direction=0)
        bulk_rects = merge_rects2(bulk_rects)

    assert len(drain_source_rects) == (device.parameters['nf']+1), f"Devices number of drain/source and found drain/source contacts don't match!"
    assert len(bulk_rects)==1, f"More than one bulk contact found!"

    #split the drain/source rectangles
    if device.use_dummies:
        # D|D|S|D|S|S
        # 0 1 2 3 4 5
        # D|D|S|D|S|D|D
        # 0 1 2 3 4 5 6
        drain_rects = drain_source_rects[1:-1:2]
        source_rects = drain_source_rects[2:-1:2]

        if device.parameters['nf']%2: #odd number of fingers
            # D|D|S|D|S|S
            # add the dummies
            drain_rects.insert(0, drain_source_rects[0])
            source_rects.append(drain_source_rects[-1])
        else: #even number of fingers
            # D|D|S|D|S|D|D
            drain_rects.insert(0, drain_source_rects[0])
            drain_rects.append(drain_source_rects[-1])
    else:
        drain_rects = drain_source_rects[::2]
        source_rects = drain_source_rects[1::2]
    
    #check if the source and bulk are connected
    device_terminal_nets = device.terminal_nets
    source_bulk_connected = False
    if device_terminal_nets["B"]==device_terminal_nets["S"]:
        source_bulk_connected = True

    if source_bulk_connected: #if source and bulk are connected
        if (device.parameters['nf'] %2)==0: #if the number of fingers is even
            # nf even, nf/2 even
            # D|S|D|S|D -> source not in middle
            # nf even, nf/2 odd, uses dummies
            # D|D|S|D|S|D|D -> source not in middle
            # nf even, nf/2 odd
            # D|S|D|S|D|S|D -> source in middle
            # nf even, nf/2 even, uses dummies
            # D|D|S|D|S|D|S|D|D -> source in middle

            if (((device.parameters['nf']//2)%2==0 and not device.use_dummies) or 
                ((device.parameters['nf']//2)%2==1 and device.use_dummies)): #if a drain-node is at the center of the device
                drain_rects, source_rects = source_rects, drain_rects #change drain and source

    terminal_rects = {}
    terminal_rects["G"] = gate_rects
    terminal_rects["D"] = drain_rects
    terminal_rects["S"] = source_rects
    terminal_rects["B"] = bulk_rects

    terminal_layers = {}
    terminal_layers["G"] = 'li'
    terminal_layers["D"] = 'li'
    terminal_layers["S"] = 'li'
    terminal_layers["B"] = 'li'
    
    terminal_location = {}
    terminal_location["G"] = 'mm'
    terminal_location["D"] = 'mm'
    terminal_location["S"] = 'lm'
    
    if source_bulk_connected:
        terminal_location["B"] = 'mm'
    else:
        terminal_location["B"] = 'ml'

    
    terminals = generate_terminals(terminal_rects, terminal_layers, terminal_location, cell)
    return terminals

def get_terminals_ThreeTermResistor(cell : Cell) -> dict[str, MagicTerminal]:
    """Maps the terminals D,S,B to terminals/pins of the devices cell,
    for a three-terminal-resistor.

    Args:
        cell (Cell): Cell of the resistor.

    Returns:
        dict[str, MagicTerminal]: key: Terminal name, value: Terminal instance.
    """

    device = cell.device
    assert type(device)==ThreeTermResistor, f"Device isn't a ThreeTermResistor!"
    assert device.parameters['m']==1, f"Device isn't build up by a single resistor!"
    assert device.use_dummies==False, f"Dummy-Resistors aren't supported!"

    rot = cell.rotation
    assert rot==0, f"Rotation different, than 0deg detected!"
    
    #get the drain/source and bulk contacts
    drain_source_rects = cell.get_overlapping_rectangles('xpolycontact', 'pwell')
    bulk_rects = cell.get_overlapping_rectangles('psubdiffcont', 'locali')

    drain_source_rects = merge_rects2(drain_source_rects)
    drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : (rectangles.bounding_box[1], rectangles.bounding_box[0]))
    bulk_rects = merge_rects2(bulk_rects)
    
    assert len(bulk_rects)==1, f"More than one bulk-contact detected!"
    assert len(drain_source_rects)==2, f"More than two drain-source contact for a single resistor detected!"

    #if rot ==0 or rot == 180:
    #    drain_source_rects = merge_rects(drain_source_rects, direction=1)
    #    bulk_rects = merge_rects(bulk_rects, direction=0)
    #else:
    #    drain_source_rects = merge_rects(drain_source_rects, direction=0)
    #    bulk_rects = merge_rects(bulk_rects, direction=1)

    drain_rects = drain_source_rects[1]
    source_rects = drain_source_rects[0]

    terminal_rects = {}
    terminal_rects["D"] = [drain_rects]
    terminal_rects["S"] = [source_rects]
    terminal_rects["B"] = bulk_rects

    terminal_layers = {}
    terminal_layers["D"] = 'li'
    terminal_layers["S"] = 'li'
    terminal_layers["B"] = 'li'

    terminal_location = {}
    terminal_location["D"] = 'mm'
    terminal_location["S"] = 'mm'
    terminal_location["B"] = 'mm'

    terminals = generate_terminals(terminal_rects, terminal_layers, terminal_location, cell)
    return terminals

def get_terminals_Capacitor(cell : Cell) -> dict[str, MagicTerminal]:
    """Maps the terminals D,S to terminals/pins of the devices cell,
    for a capacitor.

    Args:
        cell (Cell): Cell of the capacitor.

    Returns:
        dict[str, MagicTerminal]: key: Terminal name, value: Terminal instance
    """

    device = cell.device
    assert type(device)==Capacitor, f"Device isn't a Capacitor!"
    assert device.parameters['m']==1, f"Device isn't build up by one Capacitor!"
    assert device.use_dummies==False, f"Dummy-Capacitors aren't supported!"
    rot = cell.rotation
    assert rot==0, f"Rotation different, than 0deg detected!"
    
    top_layer = 'm4'

    if device.model == "sky130_fd_pr__cap_mim_m3_1":
        drain_source_rects = cell.get_overlapping_rectangles('metal4', 'metal3')
        top_layer = 'm4'
    elif device.model == "sky130_fd_pr__cap_mim_m3_2":
        drain_source_rects = cell.get_overlapping_rectangles('metal5', 'metal4')
        top_layer = 'm5'
    else:
        raise ValueError(f"Device model {device.model} not supported!")
    
    #get the drain-source rects
    drain_source_rects = merge_rects2(drain_source_rects)
    
    #if rot ==0 or rot == 180:
    #    drain_source_rects = merge_rects(drain_source_rects, direction=1)
    #else:
    #    drain_source_rects = merge_rects(drain_source_rects, direction=0)

    assert len(drain_source_rects)==2
    
    drain_rects = drain_source_rects[0]
    source_rects = drain_source_rects[1]

    terminal_rects = {}
    terminal_rects["D"] = [drain_rects]
    terminal_rects["S"] = [source_rects]

    terminal_layers = {}
    terminal_layers["D"] = top_layer
    terminal_layers["S"] = top_layer

    terminal_location = {}
    terminal_location["D"] = 'mm'
    terminal_location["S"] = 'lm'

    terminals = generate_terminals(terminal_rects, terminal_layers, terminal_location, cell)
    return terminals

def get_terminals_DifferentialPair(cell : Cell) -> dict[str, MagicTerminal]:
    """Maps the terminals G1, G2, D1, D2, S, B to terminals/pins of the devices cell.

    Args:
        cell (Cell): Cell of the differential pair.

    Returns:
        dict[str, MagicTerminal]: key: Terminal name, value: Terminal instance
    """

    device = cell.device

    assert type(device)==DifferentialPair
    assert device.parameters['m']==1, f"Device isn't build up by one MOS!"

    rot = cell.rotation

    assert rot == 0, f"Rotation {rot} not supported for terminal generation!"
    
    #get the gate rectangles
    gate_rects = cell.get_overlapping_rectangles('polycont', 'poly')
    
    #merge and sort the rectangles
    if rot ==0 or rot == 180:
        #gate_rects = merge_rects(gate_rects, direction=1)
        gate_rects = merge_rects2(gate_rects)
        gate_rects = sorted(gate_rects, key = lambda rectangles : rectangles.bounding_box[0])
    else:
        #gate_rects = merge_rects(gate_rects, direction=0)
        gate_rects = merge_rects2(gate_rects)
        gate_rects = sorted(gate_rects, key = lambda rectangles : rectangles.bounding_box[1])


    #check if the device uses a bottom-gate-contact
    botc = 0
    try:
        botc = device.cell_parameters['botc']
    except:
        botc = 0
        
    if botc==0:
        #device don't uses bottom-gate contacts
        assert len(gate_rects)==(device.parameters['nf']), "Number of devices gates, and found gates don't match!"
    else:
        #device uses bottom-gate contacts
        assert len(gate_rects)==2*(device.parameters['nf']), "Number of devices gates, and found gates don't match!"
    

    #get the drain/source and bulk contacts
    if 'pmos' in cell._layer_stack:
        drain_source_rects = cell.get_overlapping_rectangles('pdiffc', 'pdiff')
        bulk_rects = cell.get_overlapping_rectangles('nsubdiffcont', 'locali')
    else:
        drain_source_rects = cell.get_overlapping_rectangles('ndiffc', 'ndiff')
        bulk_rects = cell.get_overlapping_rectangles('psubdiffcont', 'locali')
    
    
    #merge and sort the rectangles
    if rot == 0 or rot==180:
        #drain_source_rects = merge_rects(drain_source_rects, direction=1)
        drain_source_rects = merge_rects2(drain_source_rects)
        drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : rectangles.bounding_box[0])
        #bulk_rects = merge_rects(bulk_rects, direction=1)
        bulk_rects = merge_rects2(bulk_rects)
    else:
        #drain_source_rects = merge_rects(drain_source_rects, direction=0)
        drain_source_rects = merge_rects2(drain_source_rects)
        drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : rectangles.bounding_box[1])
        #bulk_rects = merge_rects(bulk_rects, direction=0)
        bulk_rects = merge_rects2(bulk_rects)

    assert len(bulk_rects)==1, f"More than one bulk contact detected!"
    assert len(drain_source_rects)==(device.parameters['nf']+1), "Number of devices drain/source contacts and found don't match!"


    index_half = len(gate_rects)//2
    if index_half % 2 == 0: #nf per device even
        if device.use_dummies:
            #source rects with dummy fingers
            source_rects = drain_source_rects[2:-2:2]
            #-> first and last two rects are drain rects
        else:
            #source rects without dummy fingers
            source_rects = drain_source_rects[::2]

        drain_rects = list(set(drain_source_rects)-set(source_rects))

        if rot == 0 or rot==180:
            drain_rects = sorted(drain_rects, key = lambda rectangles : rectangles.bounding_box[0])
        else:
            drain_rects = sorted(drain_rects, key = lambda rectangles : rectangles.bounding_box[1])

        #split the drain-rectangles for the left and right FET
        n_rects = len(drain_rects)
        drain1_rects = drain_rects[:n_rects//2]
        drain2_rects = drain_rects[n_rects//2:]
    else: #nf odd
        if device.use_dummies:
            #source rects with dummy fingers
            source_rects = drain_source_rects[1:-1:2]
            source_rects.append(drain_source_rects[0])
            source_rects.append(drain_source_rects[-1])
        else:
            #source rects without dummy fingers
            source_rects = drain_source_rects[1:-1:2]

        drain_rects = list(set(drain_source_rects)-set(source_rects))
        
        if rot == 0 or rot==180:
            drain_rects = sorted(drain_rects, key = lambda rectangles : rectangles.bounding_box[0])
        else:
            drain_rects = sorted(drain_rects, key = lambda rectangles : rectangles.bounding_box[1])
        
        #split the drain-rectangles for the left and right FET
        n_rects = len(drain_rects)
        drain1_rects = drain_rects[:n_rects//2]
        drain2_rects = drain_rects[n_rects//2:]
        

    #drain_rects = drain_source_rects[::2]
    #source_rects = drain_source_rects[1::2]

    terminal_rects = {}
    terminal_rects["G1"] = gate_rects[:len(gate_rects)//2]
    terminal_rects["G2"] = gate_rects[len(gate_rects)//2:]
    
    terminal_rects["D1"] = drain1_rects
    terminal_rects["D2"] = drain2_rects

    terminal_rects["S"] = source_rects
    terminal_rects["B"] = bulk_rects

    terminal_layers = {}
    terminal_layers["G1"] = 'li'
    terminal_layers["G2"] = 'li'
    terminal_layers["D1"] = 'li'
    terminal_layers["D2"] = 'li'
    terminal_layers["S"] = 'li'
    terminal_layers["B"] = 'li'

    terminal_location = {}
    terminal_location["G1"] = 'mm'
    terminal_location["G2"] = 'mm'
    terminal_location["D1"] = 'mm'
    terminal_location["D2"] = 'mm'
    terminal_location["S"] = 'lm'
    terminal_location["B"] = 'ml'

    terminals = generate_terminals(terminal_rects, terminal_layers, terminal_location, cell)
    return terminals

def get_terminals_DifferentialLoad(cell : Cell) -> dict[str, MagicTerminal]:
    """Maps the terminals D1,D2,S1,S2,G,B to terminals/pins of the devices cell,
    for a differential load. 

    Args:
        cell (Cell): Cell of the differential load.

    Returns:
        dict[str, MagicTerminal]: key: Name of the terminal, value: Terminal instance
    """

    device = cell.device

    assert type(device)==DifferentialLoad
    assert device.parameters['m']==2, f"Device isn't build up by two MOS!"

    rot = cell.rotation

    assert rot == 0, f"Rotation {rot} not supported for terminal generation!"
    
    #get the gate rectangles
    gate_rects = cell.get_overlapping_rectangles('polycont', 'poly')

    #merge and sort the rectangles
    if rot ==0 or rot == 180:
        #gate_rects = merge_rects(gate_rects, direction=1)
        gate_rects = merge_rects2(gate_rects)
        gate_rects = sorted(gate_rects, key = lambda rectangles : (rectangles.bounding_box[1], rectangles.bounding_box[0]))
    else:
        #gate_rects = merge_rects(gate_rects, direction=0)
        gate_rects = merge_rects2(gate_rects)
        gate_rects = sorted(gate_rects, key = lambda rectangles : (rectangles.bounding_box[0], rectangles.bounding_box[1]))

    #check if the device uses a bottom-gate-contact
    botc = 0
    try:
        botc = device.cell_parameters['botc']
    except:
        botc = 0

    if botc==0:
        #device don't uses bottom-gate contacts
        assert len(gate_rects)==(device.parameters['nf']*2), "Number of devices gates, and found gates don't match!"
    else:
        #device uses bottom-gate contacts
        assert len(gate_rects)==2*(device.parameters['nf']*2), "Number of devices gates, and found gates don't match!"
    
    #get the drain/source and bulk rectangle
    if 'pmos' in cell._layer_stack:
        drain_source_rects = cell.get_overlapping_rectangles('pdiffc', 'pdiff')
        bulk_rects = cell.get_overlapping_rectangles('nsubdiffcont', 'locali')
    else:
        drain_source_rects = cell.get_overlapping_rectangles('ndiffc', 'ndiff')
        bulk_rects = cell.get_overlapping_rectangles('psubdiffcont', 'locali')

    #merge and sort the rectangles
    if rot == 0 or rot==180:
        #drain_source_rects = merge_rects(drain_source_rects, direction=1)
        drain_source_rects = merge_rects2(drain_source_rects)
        drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : (rectangles.bounding_box[1], rectangles.bounding_box[0]))
        #bulk_rects = merge_rects(bulk_rects, direction=1)
        bulk_rects = merge_rects2(bulk_rects)
    else:
        #drain_source_rects = merge_rects(drain_source_rects, direction=0)
        drain_source_rects = merge_rects2(drain_source_rects)
        drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : (rectangles.bounding_box[0], rectangles.bounding_box[1]))
        #bulk_rects = merge_rects(bulk_rects, direction=0)
        bulk_rects = merge_rects2(bulk_rects)
    
    assert len(bulk_rects)==1, f"More than one bulk contact detected!"
    assert len(drain_source_rects)==2*(device.parameters['nf']+1), "Number of devices drain/source contacts and found don't match!"

    #split the drain-source rectangles of the two devices
    drain_source_rects1 = drain_source_rects[:len(drain_source_rects)//2]
    drain_source_rects2 = drain_source_rects[len(drain_source_rects)//2:]
    

    #split the drain/source rectangles for the first FET
    if device.use_dummies:
        #the device uses dummies
        #get the left and right dummies
        dummy_left = drain_source_rects1[0]
        dummy_right = drain_source_rects1[-1]

        source1_rects = drain_source_rects1[2:-1:2]
        drain1_rects = drain_source_rects1[1:-1:2]
        
        #add the left dummy to the drain
        drain1_rects.insert(0, dummy_left)

        #if the number of fingers is odd
        #add the right dummy to the source
        if device.parameters['nf']%2:
            source1_rects.append(dummy_right)
        else:
            drain1_rects.append(dummy_right)
    else:
        source1_rects = drain_source_rects1[1::2]
        drain1_rects = drain_source_rects1[::2]
    
    #split the drain/source rectangles for the second FET
    if device.use_dummies:
        #the device uses dummies
        #get the left and right dummies
        dummy_left = drain_source_rects2[0]
        dummy_right = drain_source_rects2[-1]

        source2_rects = drain_source_rects2[2:-1:2]
        drain2_rects = drain_source_rects2[1:-1:2]
        
        #add the left dummy to the drain
        drain2_rects.insert(0, dummy_left)

        #if the number of fingers is odd
        #add the right dummy to the source
        if device.parameters['nf']%2:
            source2_rects.append(dummy_right)
        else:
            drain2_rects.append(dummy_right)
    else:
        source2_rects = drain_source_rects2[1::2]
        drain2_rects = drain_source_rects2[::2]

    #check if the source and bulk terminals are connected
    device = cell._device
    assert type(device)==DifferentialLoad
    nets = device.terminal_nets
    sources_bulk_connected = False
    if nets['B']==nets['S1'] and nets['B'] == nets['S2']:
        sources_bulk_connected = True

    #check if the drain/source shall be switched
    if sources_bulk_connected:
        nf = device.parameters['nf']
        if (nf %2)==0: #if the number of fingers is even
            if (nf//2)%2==0: #if a drain-node is at the center of the device
                drain_rects, source_rects = source_rects, drain_rects #change drain and source
    
    gates_in_middle = False #Holds if the gates of the device are in the middle
    if 'botc' in device.cell_parameters:
        if device.cell_parameters['botc']: #gate has a bottom contact
            nf = device.parameters['nf']
            gate_rects = gate_rects[nf:-nf] #take the gate-contacts in the middle
            gates_in_middle = True

    terminal_rects = {}
    terminal_rects["G"] = gate_rects

    terminal_rects["D1"] = drain1_rects
    terminal_rects["D2"] = drain2_rects

    terminal_rects["S1"] = source1_rects
    terminal_rects["S2"] = source2_rects
    terminal_rects["B"] = bulk_rects

    terminal_layers = {}
    terminal_layers["G"] = 'li'
    terminal_layers["D1"] = 'li'
    terminal_layers["D2"] = 'li'
    terminal_layers["S1"] = 'li'
    terminal_layers["S2"] = 'li'
    terminal_layers["B"] = 'li'

    terminal_location = {}
    terminal_location["G"] = 'mm'
    terminal_location["D1"] = 'mm'
    terminal_location["D2"] = 'mm'
    terminal_location["S1"] = 'lm'
    if gates_in_middle:
        terminal_location["S2"] = 'um'
    else:
        terminal_location["S2"] = 'lm'
    if sources_bulk_connected:
        terminal_location["B"] = 'mm'
    else:
        terminal_location["B"] = 'ml'

    terminals = generate_terminals(terminal_rects, terminal_layers, terminal_location, cell)
    return terminals

def get_terminals_CrossCoupledPair(cell : Cell) -> dict[str,MagicTerminal]:
    """Maps the terminals D1,D2,S1,S2,B to terminals/pins of the devices cell,
    for a CrossCoupledPair.

    Args:
        cell (Cell): Cell of the cross-coupled pair.

    Returns:
        dict[str, MagicTerminal]: key: Name of the terminal, value: Terminal instance
    """

    device = cell.device
    assert type(device)==CrossCoupledPair, f"Device isn't a cross-coupled-pair!"
    assert device.parameters['m']==2, f"Device isn't build up by two MOS!"
    rot = cell.rotation
    assert rot==0, f"Rotation different, than 0deg detected!"

    #get the rectangles of the gate-contacts
    gate_rects = cell.get_overlapping_rectangles('polycont', 'poly')

    #merge the rectangles and sort them
    if rot ==0 or rot == 180:
        #gate_rects = merge_rects(gate_rects, direction=1)
        gate_rects = merge_rects2(gate_rects)
        gate_rects = sorted(gate_rects, key = lambda rectangles : (rectangles.bounding_box[1], rectangles.bounding_box[0]))
    else:
        #gate_rects = merge_rects(gate_rects, direction=0)
        gate_rects = merge_rects2(gate_rects)
        gate_rects = sorted(gate_rects, key = lambda rectangles : (rectangles.bounding_box[0], rectangles.bounding_box[1]))
    
    botc = 0
    try:
        botc = device.cell_parameters['botc']
    except:
        botc = 0

    if botc==0:
        #device don't uses bottom-gate contacts
        assert len(gate_rects)==(device.parameters['nf']*2), "Number of devices gates, and found gates don't match!"
    else:
        #device uses bottom-gate contacts
        assert len(gate_rects)==2*(device.parameters['nf']*2), "Number of devices gates, and found gates don't match!"
    
    #get the drain/source and bulk rectangles
    if 'pmos' in cell._layer_stack:
        drain_source_rects = cell.get_overlapping_rectangles('pdiffc', 'pdiff')
        bulk_rects = cell.get_overlapping_rectangles('nsubdiffcont', 'locali')
    else:
        drain_source_rects = cell.get_overlapping_rectangles('ndiffc', 'ndiff')
        bulk_rects = cell.get_overlapping_rectangles('psubdiffcont', 'locali')


    #merge and sort the rectangles
    if rot == 0 or rot==180:
        #drain_source_rects = merge_rects(drain_source_rects, direction=1)
        drain_source_rects = merge_rects2(drain_source_rects)
        drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : (rectangles.bounding_box[1], rectangles.bounding_box[0]))
        
        #bulk_rects = merge_rects(bulk_rects, direction=1)
        bulk_rects = merge_rects2(bulk_rects)
    else:
        #drain_source_rects = merge_rects(drain_source_rects, direction=0)
        drain_source_rects = merge_rects2(drain_source_rects)
        drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : (rectangles.bounding_box[0], rectangles.bounding_box[1]))
        #bulk_rects = merge_rects(bulk_rects, direction=0)
        bulk_rects = merge_rects2(bulk_rects)

    assert len(bulk_rects)==1, f"More than one bulk contact detected!"
    assert len(drain_source_rects)==2*(device.parameters['nf']+1), "Number of devices drain/source contacts, and found don't match!"
    
    #split the gate-rectangles of the two FETs
    if botc==0:
        index_half = len(gate_rects)//2
        gate1_rects = gate_rects[:index_half]
        gate2_rects = gate_rects[index_half:]
    else:
        #device uses bottom-contacts
        index_quarter = len(gate_rects)//4
        #set the first gate rectangles as the bottom-most
        gate1_rects = gate_rects[:index_quarter]
        #set the second gate rectangles as the top-most
        gate2_rects = gate_rects[-index_quarter:]

    #split the drain/source rectangles of the two FETs
    drain_source_rects1 = drain_source_rects[:len(drain_source_rects)//2]
    drain_source_rects2 = drain_source_rects[len(drain_source_rects)//2:]
    
    #split the drain/source rectangles for the first FET
    if device.use_dummies:
        #the device uses dummies
        #get the left and right dummies
        dummy_left = drain_source_rects1[0]
        dummy_right = drain_source_rects1[-1]

        source1_rects = drain_source_rects1[2:-1:2]
        drain1_rects = drain_source_rects1[1:-1:2]
        
        #add the left dummy to the drain
        drain1_rects.insert(0, dummy_left)

        #if the number of fingers is odd
        #add the right dummy to the source
        if device.parameters['nf']%2:
            source1_rects.append(dummy_right)
        else:
            drain1_rects.append(dummy_right)
    else:
        source1_rects = drain_source_rects1[1::2]
        drain1_rects = drain_source_rects1[::2]
    
    #split the drain/source rectangles for the second FET
    if device.use_dummies:
        #the device uses dummies
        #get the left and right dummies
        dummy_left = drain_source_rects2[0]
        dummy_right = drain_source_rects2[-1]

        source2_rects = drain_source_rects2[2:-1:2]
        drain2_rects = drain_source_rects2[1:-1:2]
        
        #add the left dummy to the drain
        drain2_rects.insert(0, dummy_left)

        #if the number of fingers is odd
        #add the right dummy to the source
        if device.parameters['nf']%2:
            source2_rects.append(dummy_right)
        else:
            drain2_rects.append(dummy_right)
    else:
        source2_rects = drain_source_rects2[1::2]
        drain2_rects = drain_source_rects2[::2]

    #setup the terminals
    terminal_rects = {}

    #add the gate rects to the drain rects
    # since for a CCP G1 is connected to D2
    # and G2 to D1
    drain1_rects.extend(gate2_rects)
    drain2_rects.extend(gate1_rects)

    terminal_rects["D1"] = drain1_rects
    terminal_rects["D2"] = drain2_rects

    terminal_rects["S1"] = source1_rects
    terminal_rects["S2"] = source2_rects
    terminal_rects["B"] = bulk_rects

    terminal_layers = {}
    terminal_layers["D1"] = 'li'
    terminal_layers["D2"] = 'li'
    terminal_layers["S1"] = 'li'
    terminal_layers["S2"] = 'li'
    terminal_layers["B"] = 'li'

    terminal_location = {}
    terminal_location["D1"] = 'mm'
    terminal_location["D2"] = 'mm'
    if botc:
        terminal_location["S1"] = 'um'
    else:
        terminal_location["S1"] = 'lm'
    
    terminal_location["S2"] = 'lm'
    terminal_location["B"] = 'ml'

    terminals = generate_terminals(terminal_rects, terminal_layers, terminal_location, cell)
    return terminals

def get_terminals_RString(cell : Cell) -> dict[str, MagicTerminal]:
    """Maps the terminals of the RString to terminals/pins of the devices cell.

    Args:
        cell (Cell): Cell for which the physical terminals shall be generated.

    Returns:
        dict[str, MagicTerminal]: key: Terminal name, value: Terminal instance
    """
    rstring_device : RString
    rstring_device = cell.device

    assert type(rstring_device)==RString, f"Cells device isn't a RString! ({cell})"
    
    #check if the device uses dummies
    uses_dummies = rstring_device.uses_dummies

    #get the cells rotation
    rot = cell.rotation

    assert rot == 0, f"Rotation {rot} not supported for terminal generation!"
    
    #get the resistor contact rectangles, by finding overlapping rectangles on
    #different layers
    drain_source_rects = cell.get_overlapping_rectangles('xpolycontact', 'pwell')
    bulk_rects = cell.get_overlapping_rectangles('psubdiffcont', 'locali')

    #merge the rectangles, since the rectangles can be build up
    #by multiple smaller ones

    #drain_source_rects = merge_rects(drain_source_rects, direction=1)
    #use the new merging - function
    drain_source_rects = merge_rects2(drain_source_rects)
    assert len(drain_source_rects)==rstring_device.parameters['m']*2, f"Number of devices and pin-areas don't match!"
    
    #sort the rectangles according their lower-left corner, in x-direction
    drain_source_rects = sorted(drain_source_rects, key = lambda rectangles : (rectangles.bounding_box[0], rectangles.bounding_box[1]))
    
    #bulk_rects = merge_rects(bulk_rects, direction=0)
    bulk_rects = merge_rects2(bulk_rects)
        
    assert len(bulk_rects)==1, f"More than one Bulk-rectangle generated for a RString"
    assert len(drain_source_rects)==(2*rstring_device.parameters['m']), f"Number of drain/source rectangles don't match with number of resistors!"
    
    # drain-source rects
    #
    #   1   3   5
    #   |   |   |
    #   |   |   |
    #   |   |   |
    #   0   2   4

    #change the drain/source for each second resistor, to match the terminals
    for i in range(1,len(drain_source_rects)//2, 2):
        drain_source_rects[i*2], drain_source_rects[i*2+1] = drain_source_rects[i*2+1], drain_source_rects[i*2]

    # drain-source rects
    #
    #   1   2   5
    #   |   |   |
    #   |   |   |
    #   |   |   |
    #   0   3   4

    #if the device uses dummies, drop the not used pin areas of the first and last resistor
    if uses_dummies:
        # drain-source rects:
        #   Odd number of resistors
        #       1   
        #   |   |   |
        #   |   |   |
        #   |   |   |
        #   0   2   3
        #
        #   Even number of resistors
        #       1   4   
        #   |   |   |   |
        #   |   |   |   |
        #   |   |   |   |
        #   0   2   3   5

        #get the number of resistors
        n_Rs = len(drain_source_rects)//2

        # drop the drain/source rect which is further away from the bulk
        # for the first dummy
        drain_source_rects.pop(1)
        #drain_source_rects.pop(0)

        # drop the drain/source rect which is further away from the bulk
        # for the second dummy
        #if the number of Rs is odd
        if n_Rs%2: 
            # the last drain/source rect is further away
            drain_source_rects.pop(-1)
        else:
            # the next-to-last drain/source rect is further away
            drain_source_rects.pop(-2)
    
    #setup dicts to generate the terminals
    terminal_rects = {}
    terminal_layers = {}
    terminal_location = {}
    terminal_rects["B"] = bulk_rects
    terminal_layers["B"] = 'li'
    terminal_location["B"] = 'mm'

    for terminal, rect in zip(cell.device.terminals.keys(), drain_source_rects):
        terminal_rects[str(terminal)] = [rect]
        terminal_layers[str(terminal)] = 'li'
        terminal_location[str(terminal)] = 'mm'
    
    terminals = generate_terminals(terminal_rects, terminal_layers, terminal_location, cell)
    return terminals

def generate_terminals(terminal_rects : dict[str, list[Rectangle]], terminal_layers : dict[str, str], terminal_location : dict[str, str], cell : Cell) -> dict[str, MagicTerminal]:
    """Generate physical terminals.

    Args:
        terminal_rects (dict[str, list[Rectangle]]): Pin rectangles of the terminal. key: Terminal name, value: list of pin-rectangles
        terminal_layers (dict[str, str]): key: Name of the terminal, value: Name of the terminals PDK layer
        terminal_location (dict[str, str]): key: Name of the terminal, value: Location of the pins. One of 'um','ml','mr','lm'.
                ```   
                    ---um---
                    |       |
                    ml--mm--mr
                    |       |
                    ---lm---
                ```
        cell (Cell): Cell, to which the terminals belong.

    Returns:
        dict[str, MagicTerminal]: key: Name of the terminal, value: Terminal instance
    """
    terminals = {}
    for (terminal, rects) in terminal_rects.items():
        
        device = cell.device
        assert isinstance(device, PrimitiveDevice), f"A physical terminal, can only be generated for a primitive device."

        #get the net which is connected to the terminal
        net = cell.device.nets[device.terminal_nets[terminal].name]
        
        #enlarge the rects, such they lay on the lambda grid
        rects = transform_rects_to_lambda(rects)

        #get the pin-location/coordinates
        pin_locations = map_rects_to_terminal_location(rects, terminal_location[terminal], cell.rotation)
        #get the PDK layer
        layer = global_pdk.get_layer(terminal_layers[terminal])
        
        #generate the terminal
        terminals[terminal] = MagicTerminal(terminal, cell, net) 

        #generate the pins of the terminal
        for pin, rect in zip(pin_locations, rects):
            MagicPin(*pin, cell.rotation, layer, net, cell, terminals[terminal], copy.deepcopy(rect))
               
    return terminals

def transform_rects_to_lambda(rects : list[Rectangle]) -> list[Rectangle]:
    """Transform the coordinates of the rectangles given in rects, such that they lay on the lambda grid and are divisible by 2.

    Args:
        rects (list[Rectangle]): List of rectangles

    Returns:
        list[Rectangle]: List of rectangles laying on the lambda grid.
    """

    new_rects = []
    for rect in rects:
        #calc the new coordinates
        x_min = math.floor(rect.bounding_box[0]/2.)*2
        y_min = math.floor(rect.bounding_box[1]/2.)*2

        x_max = math.ceil(rect.bounding_box[2]/2.)*2
        y_max = math.ceil(rect.bounding_box[3]/2.)*2
        
        #add a new rectangle
        new_rects.append(Rectangle(x_min, y_min, x_max, y_max))
    
    return new_rects

def map_rects_to_terminal_location(terminal_rects : list[Rectangle], terminal_location : str, rotation : int) -> list[tuple[int,int]]:
    """Maps the rectangular-pin area to the x-y coordinate of a pin.
                ```   
                    ---um---
                    |       |
                    ml--mm--mr
                    |       |
                    ---lm---
                ```
    Args:
        terminal_rects (list[Rectangles]): Rectangles defining the pin-area of the terminal.
        terminal_location (str): One of {um, ml, mm, mr, lm}
        rotation (int): Multiples of 90deg., defining the rotation of the terminal.

    Raises:
        ValueError: If the terminal location isn't supported.

    Returns:
        list[tuples]: List of (x,y)-coordinates of the pins.
    """
    
    terminal_pins = []
    #iterate over the rectangles
    for r in terminal_rects:
        r = r.bounding_box
        #set the pin-locations according the given
        #terminal_location flag
        if terminal_location == 'mm':
            #set the pin location as the center-point
            pin_x = int(r[0]+r[2])//2
            pin_y = int(r[1]+r[3])//2
            terminal_pins.append((pin_x, pin_y))
        elif terminal_location == 'lm':
            if rotation == 0:
                pin_x = int(r[0]+r[2])//2
                pin_y = r[1]
                terminal_pins.append((pin_x, pin_y))
            elif rotation == 180:
                pin_x = int(r[0]+r[2])//2
                pin_y = r[3]
                terminal_pins.append((pin_x, pin_y))
            elif rotation == 90:
                pin_x = r[0]
                pin_y = int(r[1]+r[3])//2
                terminal_pins.append((pin_x, pin_y))
            else:
                pin_x = r[2]
                pin_y = int(r[1]+r[3])//2
                terminal_pins.append((pin_x, pin_y))

        elif terminal_location == 'um':
            if rotation == 0:
                pin_x = int(r[0]+r[2])//2
                pin_y = r[3]
                terminal_pins.append((pin_x, pin_y))
            elif rotation == 180:
                pin_x = int(r[0]+r[2])//2
                pin_y = r[1]
                terminal_pins.append((pin_x, pin_y))
            elif rotation == 90:
                pin_x = r[2]
                pin_y = int(r[1]+r[3])//2
                terminal_pins.append((pin_x, pin_y))
            else:
                pin_x = r[0]
                pin_y = int(r[1]+r[3])//2
                terminal_pins.append((pin_x, pin_y))
        elif terminal_location == 'ml':
            if rotation == 0:
                pin_x = r[0]
                pin_y = int(r[1]+r[3])//2
                terminal_pins.append((pin_x, pin_y))
            elif rotation == 180:
                pin_x = r[2]
                pin_y = int(r[1]+r[3])//2
                terminal_pins.append((pin_x, pin_y))
            elif rotation == 90:
                pin_x = int(r[0]+r[2])//2
                pin_y = r[3]
                terminal_pins.append((pin_x, pin_y))
            else:
                pin_x = int(r[0]+r[2])//2
                pin_y = r[1]
                terminal_pins.append((pin_x, pin_y))
        elif terminal_location == 'mr':
            if rotation == 0:
                pin_x = r[2]
                pin_y = int(r[1]+r[3])//2
                terminal_pins.append((pin_x, pin_y))
            elif rotation == 180:
                pin_x = r[0]
                pin_y = int(r[1]+r[3])//2
                terminal_pins.append((pin_x, pin_y))
            elif rotation == 90:
                pin_x = int(r[0]+r[2])//2
                pin_y = r[1]
                terminal_pins.append((pin_x, pin_y))
            else:
                pin_x = int(r[0]+r[2])//2
                pin_y = r[3]
                terminal_pins.append((pin_x, pin_y))
        else:
            raise ValueError(f"Terminal location {terminal_location} not supported!")
    
    return terminal_pins

def merge_rects(rects : list[Rectangle], direction = 0) -> list[Rectangle]:
    """Merge rectangles which touch each other.

    Args:
        rects (list[Rectangle]): List of rectangles.
        direction (int, optional): _description_. Defaults to 0.

    Returns:
        list[Rectangle]: _description_
    """
    #sort the rectangles by the x (0) / y (1) coordinate
    rects = sorted(rects, key=lambda x: x.bounding_box[direction])
    
    merged_rects = [rects[0]]
    unmerged_rects = rects[1:]
    
    #iterate over the unmerged rectangles
    for r1 in unmerged_rects:
        
        overlap = False
        #check if the rectangle overlaps with one of the merged or touches a merged
        for (r2, r_i) in zip(merged_rects, range(len(merged_rects))):
            if Rectangle.overlap(r1, r2) or Rectangle.touching(r1, r2):
                # if they overlap generate a new rectangle
                # which includes r1 and r2
                bound1 = r1.bounding_box
                bound2 = r2.bounding_box

                bound = bound1
                for i in range(2):
                    bound[i] = min(bound1[i], bound2[i])
                    bound[i+2] = max(bound1[i+2], bound2[i+2])

                merged_rects[r_i] = Rectangle(bound[0], bound[1], bound[2], bound[3])
                overlap = True
                break
        
        if not overlap:
            merged_rects.append(r1)

    return merged_rects

def merge_rects2(rects : list[Rectangle]) -> list[Rectangle]:
    """Merge rectangles which touch each other.

    Args:
        rects (list[Rectangle]): List of rectangles.

    Returns:
        list[Rectangle]: List of merged rectangles. 
    """

    #setup a graph to track connected rectangles
    graph = nx.Graph()

    graph.add_nodes_from(rects)
    
    edges = []
    #iterate over each rectangle tuple
    for i in range(len(rects)-1):
        for j in range(i+1, len(rects)):
            rect_i = rects[i]
            rect_j = rects[j]
            #check if the rectangles overlap or are touching
            if Rectangle.overlap(rect_i, rect_j) or Rectangle.touching(rect_i, rect_j):
                #add a edge, indicating the rectangles are connected
                edges.append((rect_i, rect_j))
    
    graph.add_edges_from(edges)

    #get the connected rectangles
    connected_rectangles = [list(g) for g in nx.connected_components(graph)]

    merged = []
    #merge the rectangles
    for rectangles in connected_rectangles:
        #find the rectangle which contains each rectangle of rectangles
        bound = [float('inf'), float('inf'), -float('inf'), -float('inf')]
        rectangle : Rectangle
        for rectangle in rectangles:
            r_bound = rectangle.bounding_box
            bound[0] = min(bound[0], r_bound[0])
            bound[1] = min(bound[1], r_bound[1])
            bound[2] = max(bound[2], r_bound[2])
            bound[3] = max(bound[3], r_bound[3])
        
        #add the merged rectangle
        merged.append(Rectangle(*bound))
    
    return merged
            
            