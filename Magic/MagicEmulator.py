# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 08:59:21 2023

@author: jakob
"""

import pygame

GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (0,144,255)

class MagicEmulator:
    def __init__(self, circuit):
        self._circuit = circuit
        self._pygame_init = False
        self._placed_devices = {}
        self._devices = {}
        self.screen = None
    
    def init_pygame(self):
        self._pygame_init = True
        # pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode(self._win_size)
        
    def gen_NMOS(self, name, W, L, rotation):
        if rotation % 2: #90 or 270 degree rotation
            nwell = pygame.Rect(0, 0, W, L+60)
            poly = pygame.Rect(0,0, W+58, L)
        else: #0 or 180 degree rotation
            nwell = pygame.Rect(0, 0,  L+60, W)
            poly = pygame.Rect(0,0, L, W+58)
            
        coordinate = (0,0)
        nwell.center = coordinate
        poly.center = (coordinate[0], coordinate[1])
        if rotation == 0:
            poly.center = (coordinate[0], coordinate[1]+15)
        elif rotation == 1:
            poly.center = (coordinate[0]+15, coordinate[1])
        elif rotation == 2:
            poly.center = (coordinate[0], coordinate[1]-15)
        elif rotation == 3:
            poly.center = (coordinate[0]-15, coordinate[1])
            
        nmos = pygame.Rect.union(nwell, poly)
        
        self._devices[name] = [(nmos, BLUE, 1), (nwell, YELLOW, 0),(poly, RED, 0)]
        
        return (nmos.width, nmos.height)
    
    def gen_PMOS(self, name, W, L, rotation):
        coordinate = (0,0)
        if rotation % 2: #90 or 270 degree rotation
            pwell = pygame.Rect(0, 0, W, L+60)
            nwell = pygame.Rect(0, 0, W+80, L+94)
            poly = pygame.Rect(0,0, W+58, L)
        else: #0 or 180 degree rotation
            pwell = pygame.Rect(0, 0,  L+60, W)
            nwell = pygame.Rect(0, 0,  L+94, W+80)
            poly = pygame.Rect(0,0, L, W+58)
            
            
        pwell.center = coordinate
        
        poly.center = (coordinate[0], coordinate[1])
        if rotation == 0:
            poly.center = (coordinate[0], coordinate[1]+15)
            nwell.center = (coordinate[0], coordinate[1]+15)
            
        elif rotation == 1:
            poly.center = (coordinate[0]+15, coordinate[1])
            nwell.center = (coordinate[0]+15, coordinate[1])
        elif rotation == 2:
            poly.center = (coordinate[0], coordinate[1]-15)
            nwell.center = (coordinate[0], coordinate[1]-15)
            
        elif rotation == 3:
            poly.center = (coordinate[0]-15, coordinate[1])
            nwell.center = (coordinate[0]-15, coordinate[1])
            
            
        pmos = pygame.Rect.union(pwell, poly)
        pmos = pygame.Rect.union(pmos, nwell)
        
        self._devices[name] = [(pmos, BLUE, 1), (pwell, GREEN, 0),(nwell, YELLOW, 0),(poly, RED, 0)]
        
        return (pmos.width, pmos.height)
    
    def gen_RES(self, name, W, L, rotation):
        coordinate = (0,0)
        if rotation % 2: #90 or 270 degree rotation
            c1 = pygame.Rect(0,0, 216, W)
            c2 = c1.copy()
            poly_res = pygame.Rect(0,0, L, W)
            c1.center = (coordinate[0]+L//2+108, coordinate[1])
            c2.center = (coordinate[0]-L//2-108, coordinate[1])
            
        else: #0 or 180 degree rotation
            c1 = pygame.Rect(0,0, W, 216)
            c2 = c1.copy()
            poly_res = pygame.Rect(0,0, W, L)
            c1.center = (coordinate[0], coordinate[1]+L//2+108)
            c2.center = (coordinate[0], coordinate[1]-L//2-108)
        
        poly_res.center = coordinate
        
        res = pygame.Rect.union(c1, c2)
        res = pygame.Rect.union(res, poly_res)
                
        self._devices[name] = [(res, BLUE, 1), (poly_res, RED, 0), (c1, LIGHT_BLUE, 0), (c2, LIGHT_BLUE, 0)]
        
        return (res.width, res.height)
    
    def place(self, device, coordinate):
        if device in self._devices:
            for (r, i) in zip(self._devices[device], range(len(self._devices[device]))):
                rect = r[0].move(coordinate[0], coordinate[1])
                color = r[1]
                width = r[2]
                #pygame.draw.rect(self.screen, color, rect, width = width)
                
                self._devices[device][i] = (rect, color, width)
                
            
            self._placed_devices[device] = self._devices[device]
            
        else:
            ValueError(f"Device {device} not initialized!")
    
    def draw(self):
        if self.screen:
            self.screen.fill((0,0,0))
            for d in list(self._placed_devices.values()):
                for r in d:
                    rect = r[0]
                    color = r[1]
                    width = r[2]
                    pygame.draw.rect(self.screen, color, rect, width = width)
        else:
            assert "No screen initialized!"
    
    @staticmethod
    def _get_bounding_boxes(placed_devices):
        rects = []
        for d in placed_devices:
            rects.append(d[0][0])
        return rects
    
    def DRC(self):
        rects = MagicEmulator._get_bounding_boxes(list(self._placed_devices.values()))
        for i in range(len(self._placed_devices)-1):
            for j in range(i+1, len(self._placed_devices)):
                if rects[i].colliderect(rects[j]):
                    return True
        return False
    
    
    def DRC_device(self, device_name):
        
        try:
            device = self._placed_devices[device_name]
        except:
            raise ValueError(f"Device {device_name} not placed!")
        
        bb = device[0][0]
        
        for (k,v) in self._placed_devices.items():
            if not (k == device_name):
                bb_k = v[0][0]
                if bb.colliderect(bb_k):
                    return True
        return False
    
    def reset(self):
        self._placed_devices = {}
        self._devices =  {}
        if self._pygame_init:
            self.screen.fill((0,0,0))
            
    def stop_pygame(self):
        pygame.quit()
        
    def update_screen(self):
        run = True
        # event loop
        self.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        if run:
            pygame.display.flip()
        else:
            pygame.quit()
            
        return run