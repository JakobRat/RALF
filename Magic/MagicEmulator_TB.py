# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 09:51:54 2023

@author: jakob
"""

from MagicEmulator import MagicEmulator

Emulator = MagicEmulator((1028, 1028))

Emulator.gen_NMOS("XM1", 100, 35, 0)

Emulator.draw("XM1", (500,500))

# Emulator.draw_NMOS(100, 35, 1, (400, 200))
# Emulator.draw_NMOS(100, 35, 2, (600, 200))
# Emulator.draw_NMOS(100, 35, 3, (800, 200))

#Emulator.draw_PMOS(100, 35, 0, (200, 500))
#Emulator.draw_PMOS(100, 35, 1, (400, 500))
#Emulator.draw_PMOS(100, 35, 2, (600, 500))
#Emulator.draw_PMOS(100, 35, 3, (800, 500))

# Emulator.draw_RES(35, 70, 0, (100, 500))
# #Emulator.draw_RES(35, 70, 1, (400, 1000))
# #Emulator.draw_RES(35, 70, 2, (600, 1000))
# Emulator.draw_RES(35, 70, 3, (500, 500))


print(Emulator.DRC())
while Emulator.update_screen():
    pass