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

from typing import Any
from matplotlib.patches import Rectangle as PatchRectangle

class Rectangle:
    """Class to store a rectangle.
    """
    def __init__(self, x0, y0, x1, y1):
        self._x0 = min(x0,x1)
        self._x1 = max(x1, x0)
        self._y0 = min(y0, y1)
        self._y1 = max(y1, y0)
                
    
    @property
    def height(self) -> float:
        """Height of the rectangle.

        Returns:
            float: Height of the rectangle.
        """
        return self._y1-self._y0
    
    @property
    def width(self) -> float:
        """Width of the rectangle.

        Returns:
            float: Width of the rectangle.
        """
        return self._x1-self._x0
    
    @property
    def bounding_box(self) -> tuple:
        """Get the bounding box of the rectangle.

        Returns:
            tuple: (min_x, min_y, max_x, max_y)
        """
        return (self._x0, self._y0, self._x1, self._y1)
    
    def get_coordinates(self) -> list:
        """Get the bounding box of the rectangle.

        Returns:
            list: (min_x, min_y, max_x, max_y)
        """
        return [self._x0, self._y0, self._x1, self._y1]
    
    @staticmethod
    def overlap(R1, R2, include_bound = True):
        """Checks if R1 and R2 overlap.

        Args:
            R1 (Rectangle): 1st rectangle
            R2 (Rectangle): 2nd rectangle
            include_bound (bool): If true, the boundary of the Rectangle will be a part of the Rectangle, otherwise not.
        Returns:
            bool: True if the rectangles overlap
        """
        bound1 = R1.get_coordinates()
        bound2 = R2.get_coordinates()
        EX1 = bound1[0] - bound2[2]
        EX2 = bound1[2] - bound2[0]
        EX3 = bound1[3] - bound2[1]
        EX4 = bound1[1] - bound2[3]

        if include_bound: #boundary is part of the rect
            if EX1>0 or EX2<0 or EX3<0 or EX4>0: #rects do not overlap
                return False
            else:
                return True
        else:
            if EX1>=0 or EX2<=0 or EX3<=0 or EX4>=0: #rects do not overlap
                return False
            else:
                return True


    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Rectangle) and self.bounding_box==__value.bounding_box

    def __hash__(self) -> int:
        return hash(self.bounding_box)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(b={self.bounding_box})"
    
    @staticmethod
    def touching(R1, R2) -> bool:
        """Check if the rectangles R1 and R2 are touching.

        Args:
            R1 (Rectangle): First rectangle.
            R2 (Rectangle): Second rectangle.

        Returns:
            bool: True, if touching, else False.
        """
        bound1 = R1.get_coordinates()
        bound2 = R2.get_coordinates()

        EX1 = bound1[0] - bound2[2]
        EX2 = bound1[1] - bound2[3]
        EX3 = bound1[2] - bound2[0]
        EX4 = bound1[3] - bound2[1]

        if EX1==0 or EX2==0 or EX3==0 or EX4==0:
            return True
        else:
            return False

    @staticmethod
    def is_inside(R1, R2):
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

class Rectangle3D(Rectangle):
    """Class to store a rectangle on a specific layer.
    """
    def __init__(self, x0, y0, x1, y1, layer):
        super().__init__(x0, y0, x1, y1)
        self._layer = layer

    @property
    def bounding_box(self) -> tuple:
        return (self._x0, self._y0, self._layer, self._x1, self._y1, self._layer)
    
    @property
    def layer(self):
        return self._layer
    
    def get_coordinates(self):
        return [self._x0, self._y0, self._layer, self._x1, self._y1, self._layer]
    
    def to_2d_rectangle(self) -> Rectangle:
        return Rectangle(self._x0, self._y0, self._x1, self._y1)
    
    @staticmethod
    def touching(R1, R2):
        if R1.layer == R2.layer:
            return Rectangle.touching(R1.to_2d_rectangle(), R2.to_2d_rectangle())
        else:
            return False
        
    @staticmethod
    def overlap(R1, R2, include_bound = True):
        if R1.layer == R2.layer:
            return Rectangle.overlap(R1.to_2d_rectangle(), R2.to_2d_rectangle(), include_bound=include_bound)
        else:
            return False
    
    @staticmethod
    def is_inside(R1, R2):
        if R1.layer == R2.layer:
            return Rectangle.is_inside(R1.to_2d_rectangle(), R2.to_2d_rectangle())
        else:
            return False
        
def get_free_space(boundary : Rectangle, obstacles : list[Rectangle]) -> list[Rectangle]:
    """Get a list of rectangles which describe the free space within the boundary between the obstacles.

    Args:
        boundary (Rectangle): Boundary-rectangle which describes the area for which the space is searched.
        obstacles (list[Rectangle]): List of obstacle rectangles.

    Returns:
        list[Rectangle]: List of rectangles describing the free-space.
    """
    x_list = []
    y_list = []

    #setup lists with coordinates of the rectangles
    x_list.append(boundary.bounding_box[0])
    x_list.append(boundary.bounding_box[2])

    y_list.append(boundary.bounding_box[1])
    y_list.append(boundary.bounding_box[3])

    for r in obstacles:
        x_list.append(max(boundary.bounding_box[0], r.bounding_box[0]))
        x_list.append(min(boundary.bounding_box[2], r.bounding_box[2]))
        y_list.append(max(boundary.bounding_box[1], r.bounding_box[1]))
        y_list.append(min(boundary.bounding_box[3], r.bounding_box[3]))

    
    #delete duplicates and sort 
    x_list = list(set(x_list))
    y_list = list(set(y_list))
    x_list.sort()
    y_list.sort()

    #calculate the space rectangles
    space_rects = []
    for i in range(len(x_list)-1):
        for j in range(len(y_list)-1):

            #setup a rectangle for each coordinate in the 
            #coordinates list
            x1,x2 = x_list[i], x_list[i+1]
            y1,y2 = y_list[j], y_list[j+1]

            r = Rectangle(x1, y1, x2, y2)

            #check if the rectangle overlaps with one of the obstacles.
            overlapping = False
            for rect in obstacles:
                if Rectangle.overlap(r, rect, include_bound=False):
                    overlapping = True
                    break
            
            #if the rectangle does not overlap with one of the obstacles
            # add it as free space.
            if not overlapping:
                space_rects.append(r)

    return space_rects

def merge_rects(rectangles : list[Rectangle], direction : str = 'H') -> list[Rectangle]:
    """Merge rectangles along the horizontal or vertical axes.
    Horizontal: Two neighboring rectangles are merged along the y-axis if they have the same width (If they share the same N and S edge).
    Vertical: Two neighboring rectangles are merged along the x-axis if they have the same height (If they share the same W and E edge).

    Args:
        rectangles (list[Rectangle]): List of rectangles which shall be merged.
        direction (str, optional): Merge-direction, 'H' or 'V'. Defaults to 'H'.

    Returns:
        list[Rectangle]: List of the resulting merged rectangles.
    """
    assert direction in ['H', 'V'], f"Direction {direction} not supported!"
    merged_rects = []
    if direction == 'H':
        #sort the rectangles according their lower left corner
        rectangles = sorted(rectangles, key=lambda r : (r.bounding_box[0], r.bounding_box[1]))
        #store the actual merged rectangle
        act_rect = list(rectangles[0].bounding_box)
        #iterate over all rectangles
        for rect in rectangles[1:]:
            rect = list(rect.bounding_box)
            #check if the rectangles share the N and S edge
            if rect[1]==act_rect[3] and rect[0]==act_rect[0] and rect[2]==act_rect[2]:
                #merge rects along the y axis 
                act_rect[3]=rect[3]
            else:
                #if not add the act_rect to the merged, and merge the next
                merged_rects.append(Rectangle(*tuple(act_rect)))
                act_rect = rect
        
        merged_rects.append(Rectangle(*tuple(act_rect)))
    elif direction == 'V':
        #sort the rectangles according their lower left corner in y direction.
        rectangles = sorted(rectangles, key=lambda r : (r.bounding_box[1], r.bounding_box[0]))
        #store the actual merged rectangle
        act_rect = list(rectangles[0].bounding_box)
        #iterate over all rectangles
        for rect in rectangles[1:]:
            rect = list(rect.bounding_box)
            #check if the rectangles share the W and E edge
            if rect[0]==act_rect[2] and rect[1]==act_rect[1] and rect[3]==act_rect[3]: 
                #merge rects along the x axis 
                act_rect[2]=rect[2]
            else:
                #if not add the act_rect to the merged, and merge the next
                merged_rects.append(Rectangle(*tuple(act_rect)))
                act_rect = rect
        
        merged_rects.append(Rectangle(*tuple(act_rect)))
    
    return merged_rects