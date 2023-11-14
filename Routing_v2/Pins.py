from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Magic.MagicTerminal import MagicPin
    from Magic.MagicDie import MagicDiePin
    from SchematicCapture.Net import Net

from Routing_v2.Grid import global_grid

class GlobalPins:
    """Class to store pins of multiple routes.
    """
    def __init__(self) -> None:
        self._pins = {}

    def add_pin(self, pin : MagicPin|MagicDiePin, net : Net):
        """Add a pin to the global pins.

        Args:
            pin (MagicPin | MagicDiePin): Pin to be added.
            net (Net): Net to which the pin belongs.
        """

        if net in self._pins:
            self._pins[net].append(pin)
        else:
            self._pins[net] = [pin]

        #update grid lines for the pins
        global_grid.setup_grid_for_pins(self.get_all_pins())

    def get_all_pins(self) -> list[MagicPin|MagicDiePin]:
        """Get a list of all pins.

        Returns:
            list[MagicPin|MagicDiePin]: List of pins.
        """
        pins = []
        for net, pin_list in self._pins.items():
            pins.extend(pin_list)
        
        return pins
    
global_pins = GlobalPins()