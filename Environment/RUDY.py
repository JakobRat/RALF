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
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from PDK.PDK import PDK
    from SchematicCapture.Net import Net
import numpy as np
import matplotlib.pyplot as plt


class RUDY:
    """Class for estimating routing congestion from a placement.
    Based on the paper:
        P.Spindler and F.M. Johannes, "Fast and Accurate Routing Demand Estimation for Efficient Routability-driven Placement,"
        2007 Design, Automation & Test in Europe Conference & Exhibition, Nice, France, 2007, pp. 1-6, doi: 10.1109/DATE.2007.364463
    """
    def __init__(self, pdk : PDK) -> None:
        """Setup RUDY.

        Args:
            pdk (PDK): PDK which shall be used.
        """
        self._pdk = pdk
        self._p = self._calc_wire_width()
        self._nets = {} #key: net-name, value: (wire_density, bounding_box)
    
    def _calc_wire_width(self) -> float:
        """Calculate the mean-wire width of the PDK.

        Returns:
            float: Mean-wire width of the PDK.
        """
        w_sum = sum(l.minWidth+l.minSpace for l in self._pdk.metal_layers.values())
        n_layers = len(self._pdk.metal_layers)
        return w_sum/(n_layers**2)

    def _calc_wire_density(self, net : Net) -> float:
        """Calculate the wire density d of net <net>.
            d = L(net)*p/(w*h)
            p ... wire width
            w ... width of the net bounding-box 
            h ... height of the net bounding-box
        Args:
            net (Net): Net to calculate the wire density.

        Returns:
            float: Wire density.
        """
        bound = net.bounding_box()
        w = (bound[2]-bound[0])+1
        h = (bound[3]-bound[1])+1
        L = w+h
        return self._p * L/(w*h)

    def add_net(self, net : Net):
        """Add a net for congestion estimation.

        Args:
            net (Net): Net which shall be added.
        """
        self._nets[net.name] = (self._calc_wire_density(net), net.bounding_box())
    
    def clear_nets(self):
        """Delete all nets.
        """
        self._nets = {}

    def D_rout_dem(self, x : float, y : float):
        """Calculate the routing demand D at coordinate (x,y). 

        Args:
            x (float): x-coordinate
            y (float): y-coordinate

        Returns:
            float: Routing demand D.
        """
        D = 0
        for (net, (d, bound)) in self._nets.items():
            #check if point is within the net 
            if x>=bound[0] and x<=bound[2] and y>=bound[1] and y<=bound[3]: 
                D += d
        
        return D

    def D_rout_sup(self, x, y):
        """Calculate the routing supply D, at coordinate (x,y). 

        Args:
            x (float): x-coordinate
            y (float): y-coordinate

        Returns:
            float: Routing supply D.
        """
        return 1.0
    

    def D_rout_mat(self, x_min, y_min, x_max, y_max, n_x=64, n_y=64) -> np.ndarray:
        """Get the routing demand in the area defined by <x_min>, <y_min>, <x_max>, <y_max>.

        Args:
            x_min (float): Min. x coordinate of the area.
            y_min (float): Min. y coordinate of the area.
            x_max (float): Max. x coordinate of the area.
            y_max (float): Max. y coordinate of the area.
            n_x (int, optional): Number of x-points. Defaults to 64.
            n_y (int, optional): Number of y-points. Defaults to 64.

        Returns:
            np.ndarray: Routing demand of the area.
        """
        D = np.zeros((n_x, n_y))
        #setup the coordinates
        x = np.arange(x_min, x_max, (x_max-x_min)/n_x, dtype=float)
        y = np.arange(y_min, y_max, (y_max-y_min)/n_y, dtype=float)

        #get the routing demand at each coordinate
        for i in range(n_x):
            for j in range(n_y):
                D[j,i] = self.D_rout_dem(x[i],y[j])
        
        return D
    
    def plot_route_demand(self, x_min, y_min, x_max, y_max, n_x=64, n_y=64):
        """Plot the routing demand in the area defined by <x_min>, <y_min>, <x_max>, <y_max>.

        Args:
            x_min (float): Min. x coordinate of the area.
            y_min (float): Min. y coordinate of the area.
            x_max (float): Max. x coordinate of the area.
            y_max (float): Max. y coordinate of the area.
            n_x (int, optional): Number of x-points. Defaults to 64.
            n_y (int, optional): Number of y-points. Defaults to 64.
        """
        D = self.D_rout_mat(x_min, y_min, x_max, y_max, n_x, n_y)

        plt.imshow(D, cmap='hot', origin='lower')
        plt.colorbar()
        plt.title("Route-demand")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.show()
    
    @staticmethod
    def _intersection_area(r1 : tuple, r2 : tuple):
        """Get the area of the intersecting rectangles defined by r1 and r2.

        Args:
            r1 (tuple): Boundingbox of the 1st rectangle.
            r2 (tuple): BOundingbox of the 2nd rectangle. 

        Returns:
            float: Area of the intersection.
        """
        x_min = max(r1[0], r2[0])
        x_max = min(r1[2],r2[2])
        y_min = max(r1[1],r2[1])
        y_max = min(r1[3],r2[3])

        if x_min>x_max or y_min>y_max:
            return 0.0
        else:
            w = (x_max-x_min)+1.0
            h = (y_max-y_min)+1.0
            return w*h
        
    def congestion(self) -> float:
        """Get the congestion of the placement.

        Returns:
            float: Congestion of the placement.
        """
        c = 0.0

        #iterate over each net-pair
        for (net1, (d1, bound1)) in self._nets.items():
            for (net2, (d2, bound2)) in self._nets.items():
                if net1 != net2:
                    # add the wire density times 
                    # the intersecting net-area to the  total congestion 
                    c += d2 * RUDY._intersection_area(bound1, bound2)
        
        return c