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
    from rectangle_packing_placement.placement_floorplan import PlacementFloorplan
    from rectangle_packing_placement.placement_problem import PlacementProblem
    from rectangle_packing_placement.rectangle_packing_solver.sequence_pair import SequencePair

from rectangle_packing_placement.rectangle_packing_solver.solution import Solution


class PlacementSolution(Solution):
    """Class to store a placement solution.
    """
    def __init__(self, sequence_pair: SequencePair, floorplan: PlacementFloorplan, problem : PlacementProblem) -> None:
        super().__init__(sequence_pair, floorplan)
        self.problem = problem

    def __repr__(self) -> str:
        s = "PlacementSolution({"
        s += "'sequence_pair': " + str(self.sequence_pair) + ", "
        s += "'floorplan': " + str(self.floorplan) + ", "
        s += "'problem': " + str(self.problem) + "})"

        return s