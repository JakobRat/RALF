# Copyright 2022 Kotaro Terada
#
# Copyright 2023 Jakob Ratschenberger
#
# Modifications:
# - Updated SequencePair to PlacementSequencePair and added rotation to the positions dict
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

from rectangle_packing_placement.placement_floorplan import PlacementFloorplan

from rectangle_packing_placement.rectangle_packing_solver.problem import Problem
from rectangle_packing_placement.rectangle_packing_solver.sequence_pair import SequencePair

import graphlib
from typing import Any, Dict, List, Optional, Tuple

class PlacementSequencePair(SequencePair):
    def decode(self, problem: Problem, rotations: List | None = None) -> PlacementFloorplan:
        """
        Decode:
            Based on the sequence pair and the problem with rotations information, calculate a floorplan
            (bounding box, area, and rectangle positions).
        """

        if not isinstance(problem, Problem):
            raise TypeError("Invalid argument: 'problem' must be an instance of Problem.")

        if problem.n != self.n:
            raise ValueError("'problem.n' must be the same as the sequence-pair length.")

        if rotations is not None:
            if len(rotations) != self.n:
                raise ValueError("'rotations' length must be the same as the sequence-pair length.")

        coords = self.oblique_grid.coordinates

        # Width and height dealing with rotations
        width_wrot = []
        height_wrot = []
        for i in range(self.n):
            if (rotations is None) or (rotations[i] % 2 == 0):
                # no rotation
                width_wrot.append(problem.rectangles[i]["width"])
                height_wrot.append(problem.rectangles[i]["height"])
            else:
                # with rotation
                assert problem.rectangles[i]["rotatable"]
                width_wrot.append(problem.rectangles[i]["height"])
                height_wrot.append(problem.rectangles[i]["width"])

        # Calculate the longest path in the "Horizontal Constraint Graph" (G_h)
        # This time complexity is O(n^2), may be optimized...
        graph_h: Dict[int, List] = {i: [] for i in range(self.n)}
        for i in range(self.n):
            for j in range(self.n):
                # When j is right of i, set an edge from j to i
                if (coords[i]["a"] < coords[j]["a"]) and (coords[i]["b"] < coords[j]["b"]):
                    graph_h[j].append(i)

        # Topological order of DAG (G_h)
        topo_h = graphlib.TopologicalSorter(graph_h)
        torder_h = list(topo_h.static_order())

        # Calculate W (bounding box width) from G_h
        dist_h = [width_wrot[i] for i in range(self.n)]
        for i in torder_h:
            dist_h[i] += max([dist_h[e] for e in graph_h[i]], default=0)
        bb_width = max(dist_h)

        # Calculate the longest path in the "Vertical Constraint Graph" (G_v)
        # This time complexity is O(n^2), may be optimized...
        graph_v: Dict[int, List] = {i: [] for i in range(self.n)}
        for i in range(self.n):
            for j in range(self.n):
                # When j is above i, set an edge from j to i
                if (coords[i]["a"] > coords[j]["a"]) and (coords[i]["b"] < coords[j]["b"]):
                    graph_v[j].append(i)

        # Topological order of DAG (G_v)
        topo_v = graphlib.TopologicalSorter(graph_v)
        torder_v = list(topo_v.static_order())

        # Calculate H (bounding box height) from G_v
        dist_v = [height_wrot[i] for i in range(self.n)]
        for i in torder_v:
            dist_v[i] += max([dist_v[e] for e in graph_v[i]], default=0)
        bb_height = max(dist_v)

        # Calculate bottom-left positions
        positions = []
        for i in range(self.n):
            positions.append(
                {
                    "id": i,
                    "x": dist_h[i] - width_wrot[i],  # distance from left edge
                    "y": dist_v[i] - height_wrot[i],  # distande from bottom edge
                    "width": width_wrot[i],
                    "height": height_wrot[i],
                    "rotation": rotations[i]
                }
            )

        return PlacementFloorplan(bounding_box=(bb_width, bb_height), positions=positions, problem=problem)
        