from __future__ import annotations
from typing import TYPE_CHECKING


from Magic.Cell import Cell
from Magic.MagicLayer import MagicLayer, Rectangle, Color
from Magic.MagicTerminal_utils import Net
from SchematicCapture.Devices import Device, SubDevice
from Magic.MagicTerminal import MagicTerminal, MagicPin
import copy

class MacroCell(Cell):
    """Class to store a MacroCell.
        A MacroCell is a cell, which is build up by multiple sub-cells.
        The MacroCell encloses this sub-cells.
    """
    def __init__(self, name : str, cells : list[Cell]):
        """Class to store a macro-cell composed of cells. 

        Args:
            name (str): Name of the macro cell.
            cells (list[Cell]): List of cells, held by the macro-cell.
        """

        self._cells = cells #store the cells of the macro cell
        self._cells_center = (0,0) #store the center-point of the cells
        self._cells_rotation = 0 #store the rotation of the cells

        #get the bounding layer of the cells.
        layers = self.get_cells_bound_layer()

        # move the internal cells, such that their overall
        # center-coordinate is (0,0)
        self._reset_cells(act_bound=layers["Bounding"].get_bounding_box())

        #get the bounding layer of the MacroCells
        layers = self.get_cells_bound_layer()

        super().__init__(name, layers)

    @property
    def cells(self):
        return self._cells
    
    def get_cells_bound_layer(self) -> dict[str, MagicLayer]:
        """Get the bounding layer defined by the bounding box over all cells of the MacroCell.

        Returns:
            dict: key: 'Bounding' value: MagicLayer of the boundary
        """
        
        #find the bounding box of the internal cells
        bound = self._cells[0].get_bounding_box()

        for n in range(1,len(self._cells)):
            act_cell = self._cells[n]
            act_bound = act_cell.get_bounding_box()

            for i in range(2):
                bound[i] = min(bound[i], act_bound[i])
                bound[i+2] = max(bound[i+2], act_bound[i+2])

        #setup a MagicLayer for the bounding box
        bounding_rect = Rectangle(bound[0], bound[1], bound[2], bound[3])
        bounding_layer = MagicLayer("Bounding", Color((255,255,255)))
        bounding_layer.add_rect(bounding_rect)
        bounding_layer.dont_fill()   

        return {"Bounding" : bounding_layer}
    
    def set_device(self, device: SubDevice):
        """Set the device of the MacroCell.

        Args:
            device (SubDevice): Device of the MacroCell.
        """
        assert isinstance(device, SubDevice)
        self._device = device

    def add_terminals(self):
        """Add terminals to the macro-cell, from the internal cells terminals.
        """
        #get the terminal nets of the macros SubDevice.
        nets = self._device.nets

        #iterate over the terminal nets
        for (n_name, net) in nets.items():
            #add terminals net-wise.
            terminals : list[MagicTerminal]
            terminals = []
            #get the internal net
            internal_nets = self._device.internal_nets[n_name]
            
            # add each physical terminal of the internal cells,
            # which is connected to the net

            for cell in self._cells:
                assert isinstance(cell, Cell)
                for internal_net in internal_nets:
                    terminals.extend(cell.terminals_connected_to_net(internal_net))

            #setup a new terminal 
            self._terminals[n_name] = MagicTerminal(n_name, self, net)

            #generate and add the physical pins to the terminal
            # -> The pins have to be generated new, since they are already 
            #    registered at the internal cells terminal.
            for terminal in terminals:
                for pin in terminal.pins:
                    assert isinstance(pin, MagicPin)
                    #setup a new pin, and register the pin at the terminal
                    #of the MacroCell
                    MagicPin(*pin.coordinate, self.rotation, pin.layer, net, self, self._terminals[n_name], copy.deepcopy(pin.bounding_box))
                
    def terminals_connected_to_net(self, net: Net) -> list[MagicTerminal]:
        """Get the physical terminals which are connected to Net <net>.

        Args:
            net (Net): Net, for which the physical terminals shall be returned.

        Returns:
            list[MagicTerminal]: List of MagicTerminals.
        """
        terminals = []
        if net.name in self._terminals:
            terminals.append(self._terminals[net.name])
        return terminals
    
    def _add_bounding_layer(self):
        return super()._add_bounding_layer()
    
    def _reset_cells(self, act_bound : tuple):
        """Move the cells inside the macro cell to (0,0).

        Args:
            act_bound (tuple): Actual boundary of the internal cells.
        """

        center = ((act_bound[0]+act_bound[2])/2, (act_bound[1]+act_bound[3])/2)
        for c in self._cells:
            c._move((-center[0], -center[1]))

        self._cells_center = (0,0)

    def _move_cells_to_bound(self):
        """Move the cells inside the macro cell, to match the boundary.
        """
        
        cells_center = self._cells_center
        cells_rotation = self._cells_rotation

        #rotate the cells, 
        for c in self._cells:
            c._rotate(cells_center, self.rotation-cells_rotation)
        
        #move the cells
        move_by = (self.center_point[0]-cells_center[0], self.center_point[1]-cells_center[1])
        for c in self._cells:
            c._move(move_by)

        #store the new center-points and rotations
        self._cells_center = self.center_point
        self._cells_rotation = self.rotation
        
    def draw(self, screen):
        
        self._layer_stack["Bounding"].draw(screen)

        for c in self._cells:
            c.draw(screen)

