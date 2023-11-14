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

import pygame
import copy
import numpy as np
from PDK.Layers import Layer
from PDK.PDK import PDK
from matplotlib.patches import Rectangle as PatchRectangle

class Rectangle:
    """Class to store a rectangle.
    """
    def __init__(self, x0 : int|float, y0 : int|float, x1 : int|float, y1 : int|float) -> None:
        """Setup a rectangle.
            ```
                -------------(x1,y1)  
                |               |     
                |               |     
                |               |
             (x0,y0)------------   
            
            ```
        Args:
            x0 (int | float): Min. x coordinate.
            y0 (int | float): Min. y coordinate.
            x1 (int | float): Max. x coordinate.
            y1 (int | float): Max. y coordinate.
        """ 
        self._x0 = min(x0,x1)
        self._x1 = max(x1, x0)
        self._y0 = min(y0, y1)
        self._y1 = max(y1, y0)
                
    
    @property
    def height(self) -> int|float:
        """Get the height of the rectangle.

        Returns:
            int|float: Height of the rectangle.
        """
        return self._y1-self._y0
    
    @property
    def width(self) -> int|float:
        """Get the width of the rectangle.

        Returns:
            int|float: Width of the rectangle.
        """
        return self._x1-self._x0
    
    @property
    def bounding_box(self) -> list[float|int]:
        """Get the coordinates of the bounding box.

                -------------(x1,y1)
                |               |
                |               |
                |               |
             (x0,y0)------------

        Returns:
            list[float|int]: (x0, y0, x1, y1)
        """
        return [self._x0, self._y0, self._x1, self._y1]
    
    def to_pygame(self) -> pygame.Rect:
        """Generate the rectangle in pygame.

        Returns:
            pygame.Rect: Pygame rectangle.
        """
        return pygame.Rect(self._x0, self._y0, self.width, self.height) 
    
    def get_coordinates(self) -> list[float|int]:
        """Get the coordinates of the bounding box.

                -------------(x1,y1)
                |               |
                |               |
                |               |
             (x0,y0)------------

        Returns:
            list[float|int]: (x0, y0, x1, y1)
        """
        return [self._x0, self._y0, self._x1, self._y1]
    
    def move(self, coordinate : tuple[int|float, int|float]):
        """Move the rectangle by the amount of <coordinate>.
            
            coordinate = (c0, c1)
            
            Resulting coordinates: \n
            ```
                ------------------(x1+c0,y1+c1)
                |                       |
                |                       |
                |                       |
             (x0+c0,y0+c1)---------------
            ```
        Args:
            coordinate (tuple): Amount the rectangle should be moved.
        """
        self._x0 += coordinate[0]
        self._x1 += coordinate[0]
        self._y0 += coordinate[1]
        self._y1 += coordinate[1]
    
    def rotate(self, mean_coordinate : tuple[int|float, int|float], angle : int):
        """Rotate the rectangle around <mean_coordinate> counter-clockwise,
            by the amount of <angle>.

        Args:
            mean_coordinate (tuple ): center-point of the rotation
            angle (int): rotation angle, multiples of 90deg

        Raises:
            ValueError: If the angle isn't multiple of 90deg.
        """
        #check the angle
        if angle%90 == 0:
            
            #setup the coordinates
            mean = np.array(mean_coordinate)
            c0 = np.array([self._x0, self._y0])
            c1 = np.array([self._x1, self._y1])
            
            #transform the angle in rad
            angle = angle * np.pi/180

            #setup a rotation matrix
            rot_mat = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
            
            #           --------(c1)
            #           |       / |
            #           |     /   |
            #           (c0)------
            #       v0 /   / v1
            #         /  /  
            #   (mean)  

            #get a vector from the rotation-center to the rectangle coordinates
            v0 = c0-mean
            v1 = c1-mean
            
            #do the rotation
            v0 = np.round(rot_mat.dot(v0),2)
            v1 = np.round(rot_mat.dot(v1),2)
            
            #retrieve the new bounding-box coordinates
            x_min = min(v0[0], v1[0])
            y_min = min(v0[1], v1[1])
            x_max = max(v0[0], v1[0])
            y_max = max(v0[1], v1[1])
            
            c0 = np.array((x_min, y_min))+mean
            c1 = np.array((x_max, y_max))+mean
            
            self._x0 = c0[0]
            self._y0 = c0[1]
            self._x1 = c1[0]
            self._y1 = c1[1]
        
        else:
            raise ValueError("Only angles multiple of 90deg are supported!")
    
    @staticmethod
    def overlap(R1 : Rectangle, R2 : Rectangle) -> bool:
        """Checks if R1 and R2 overlap.

        Args:
            R1 (Rectangle): 1st rectangle
            R2 (Rectangle): 2nd rectangle

        Returns:
            bool: True if the rectangles overlap
        """
        bound1 = R1.get_coordinates()
        bound2 = R2.get_coordinates()
        EX1 = bound1[0] - bound2[2]
        EX2 = bound1[2] - bound2[0]
        EX3 = bound1[3] - bound2[1]
        EX4 = bound1[1] - bound2[3]

        if EX1>0 or EX2<0 or EX3<0 or EX4>0: #rects do not overlap
            return False
        else:
            return True

    @staticmethod
    def touching(R1 : Rectangle, R2 : Rectangle) -> bool:
        """Check if two rectangles touch each other, at their boarders.

        Args:
            R1 (Rectangle): 1st rectangle.
            R2 (Rectangle): 2nd rectangle.

        Returns:
            bool: True, if they touch, else False.
        """
        bound1 = R1.get_coordinates()
        bound2 = R2.get_coordinates()

        EX1 = bound1[0] - bound2[2]
        EX2 = bound1[1] - bound2[3]
        EX3 = bound1[2] - bound2[0]
        EX4 = bound1[3] - bound2[1]

        #check if they touch at the E or W edge
        if (EX1 == 0 or EX3==0) and EX4>=0 and EX2<=0:
            return True
        
        #check if they touch at the S or N edge
        elif (EX2 == 0 or EX4==0) and EX3>=0 and EX1<=0:
            return True
        else:
            return False

    @staticmethod
    def is_inside(R1 : Rectangle, R2 : Rectangle) -> bool:
        """Checks if R1 is inside R2.

        Args:
            R1 (Rectangle): 1st rectangle
            R2 (Rectangle): 2nd rectangle

        Returns:
            bool: True if R1 is inside R2 (including edges).
        """
        bound1 = R1.get_coordinates()
        bound2 = R2.get_coordinates()

        EX1 = bound1[0] - bound2[0]
        EX2 = bound1[2] - bound2[2]
        EX3 = bound1[1] - bound2[1]
        EX4 = bound1[3] - bound2[3]

        if EX1>=0 and EX2<=0 and EX3>=0 and EX4<=0:
            return True
        else:
            return False

    def plot(self, ax, color = None, hatch=None):
        """Plot the rectangle on axis <ax> with color <color> and hatch <hatch>.

        Args:
            ax (axis): Axis on which the rectangle shall be plotted.
            color (str, optional): Color of the rectangle. Defaults to None.
            hatch (str, optional): Pattern of the rectangle. Defaults to None.
        """
        patch = PatchRectangle((self.bounding_box[0], self.bounding_box[1]),
                               width=self.width,
                               height=self.height,
                               fill= False if color is None else True,
                               hatch=hatch,
                               facecolor=color,
                               edgecolor='k',
                               alpha=0.7)
        ax.add_patch(patch)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(b={tuple(self.bounding_box)}, w={self.width}, h={self.height})"
    
    def __eq__(self, __value: object) -> bool:
        return (type(__value)==Rectangle and self.bounding_box == __value.bounding_box)

    def __hash__(self) -> int:
        return hash(tuple(self.bounding_box))
    
class Color:
    """Class to store a color.
    """
    def __init__(self, rgb : tuple):
        self._rgb = rgb
    
    @property
    def rgb(self) -> tuple:
        """Get the rgb value of the color.

        Returns:
            tuple: (R,G,B) RGB value of the color
        """
        return self._rgb
    
class MagicLayer:
    """Class to store a magic layer, with rectangles on it.
    """
    def __init__(self, name : str, color : Color):
        """Setup a magic layer.

        Args:
            name (str): Name of the layer.
            color (Color): Color of the layer.
        """
        self._name = name
        self._rects : list[Rectangle]
        self._rects = []
        self._color = color
        self._fill = True

        #track the rotation of the layer
        self._rotation = 0
    
    def __eq__(self, __value: object) -> bool:
        return (isinstance(__value, MagicLayer)) and (self._name == __value._name)

    def __hash__(self) -> int:
        return hash(self._name)
    
    @property
    def name(self) -> str:
        """Get the name of the layer.

        Returns:
            str: Name of the layer.
        """
        return self._name
    
    @property
    def fill(self) -> bool:
        """Check if the rectangles of the layer shall be filled.

        Returns:
            bool: True, if they shall be filled, otherwise False.
        """
        return self._fill
    
    @property
    def rotation(self) -> int:
        """Get the rotation of the layer in deg.

        Returns:
            int: Rotation of the layer between 0 and 359.
        """
        return self._rotation%360

    @property
    def rectangles(self) -> list[Rectangle]:
        """Get the rectangles of the layer.

        Returns:
            list[Rectangle]: List of rectangles.
        """
        return self._rects
    
    def dont_fill(self):
        """Set the fill-attribute to False.
        """
        self._fill = False
        
    def add_rect(self, rect : Rectangle):
        """Add a rectangle to the layer.

        Args:
            rect (Rectangle): Rectangle which shall be added.
        """
        self._rects.append(rect)
    
    def move(self, coordinate : tuple[float|int, float|int]):
        """Move the rectangles of the layer by the amount given 
        in <coordinate>.

        Args:
            coordinate (tuple[float | int, float | int]): (dx, dy) Defines the movement in x and y direction.
        """
        for r in self._rects:
            r.move(coordinate)
        
    def draw(self, surface : pygame.Surface):
        """Draw the layer on an pygame surface.

        Args:
            surface (pygame.Surface): Surface in which the layer shall be drawn.
        """
        for r in self._rects:
            pygame.draw.rect(surface, self._color.rgb, copy.copy(r.to_pygame()), 0 if self._fill else 5)
    
    def get_bounding_box(self) -> list[int|float]:
        """Get the bounding box of the layer.
            ```
                -------------(x1,y1)  
                |               |     
                |               |     
                |               |
             (x0,y0)------------   
            
            ```
        Returns:
            list[int|float]: (x0, y0, x1, y1)
        """
        bounding = self._rects[0].get_coordinates()
        for r in self._rects:
            r_bound = r.get_coordinates()
            for i in range(2):
                bounding[i] = min(bounding[i], r_bound[i])
            
            for i in range(2,4):
                bounding[i] = max(bounding[i], r_bound[i])
        return bounding
    
    def rotate(self, mean_coordinate : tuple[float|int], angle : int):
        """Rotate the layer clock-wise by the angle <angle>, around <mean_coordinate>.

        Args:
            mean_coordinate (tuple): mean-coordinate of the rotation
            angle (int): Rotation angle, multiple of 90deg
        """
        for r in self._rects:
            #rotate each rectangle around the mean-coordinate, clock-wise 
            r.rotate(mean_coordinate, -angle)
        
        #track the rotation of the layer
        self._rotation += angle%360

    @staticmethod
    def get_overlaps(L1  : Layer, L2 : Layer) -> list[Rectangle]:
        """Get the rectangles of L1 which overlap with rectangles of L2.

        Args:
            L1 (Layer): Layer 1
            L2 (Layer): Layer 2

        Returns:
            list[Rectangles]: List of Rectangles (of Layer 1) which overlap with Rectangles of Layer 2.
        """
        overlaying_rects = set()
        rects_L1 = L1.rectangles
        rects_L2 = L2.rectangles

        for ri in rects_L1:
            for rj in rects_L2:
                if Rectangle.overlap(ri, rj):
                    overlaying_rects.add(ri)
        
        return list(overlaying_rects)
