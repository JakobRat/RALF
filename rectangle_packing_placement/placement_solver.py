# Copyright 2022 Kotaro Terada
#
# Copyright 2023 Jakob Ratschenberger
#
# Modifications:
# - Updated SequencePair to PlacementSequencePair
# - Introduced PlacementRectanglePackingProblemAnnealerSoft for the placement task
# - Introduced PlacementRectanglePackingProblemAnnealerHard for the placement task
#
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


from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from rectangle_packing_placement.rectangle_packing_solver.problem import Problem
from rectangle_packing_placement.placement_solution import PlacementSolution

if TYPE_CHECKING:
    from rectangle_packing_placement.placement_problem import PlacementProblem

from rectangle_packing_placement.rectangle_packing_solver.solver import Solver, RectanglePackingProblemAnnealerHard, RectanglePackingProblemAnnealerSoft, exit_handler
from rectangle_packing_placement.placement_sequence_pair import PlacementSequencePair

import random
import sys
import signal
import math

class PlacementSolver(Solver):
    def __init__(self) -> None:
        super().__init__()

    def _solve_with_strategy(self, problem: PlacementProblem, 
                             width_limit: float | None = None, 
                             height_limit: float | None = None, 
                             initial_state: List[int] | None = None, 
                             simanneal_minutes: float = 0.1, 
                             simanneal_steps: int = 100, 
                             show_progress: bool = False, 
                             strategy: str = None) -> PlacementSolution:
        
        if not initial_state:
            # Initial state (= G_{+} + G_{-} + rotations)
            if width_limit and (width_limit < sys.float_info.max):
                # As flat as possible along with vertical line
                init_gp = list(range(problem.n))
                init_gn = list(reversed(list(range(problem.n))))
                init_rot = [1 if r["rotatable"] and r["width"] > r["height"] else 0 for r in problem.rectangles]
            elif height_limit and (height_limit < sys.float_info.max):
                # As flat as possible along with horizontal line
                init_gp = list(range(problem.n))
                init_gn = list(range(problem.n))
                init_rot = [1 if r["rotatable"] and r["width"] < r["height"] else 0 for r in problem.rectangles]
            else:
                # Random sequence pair (shuffle)
                init_gp = random.sample(list(range(problem.n)), k=problem.n)
                init_gn = random.sample(list(range(problem.n)), k=problem.n)
                init_rot = [0 for _ in range(problem.n)]
            init_state = init_gp + init_gn + init_rot
        else:
            init_state = initial_state

        if strategy == "hard":
            rpp = PlacementRectanglePackingProblemAnnealerHard(
                state=init_state,
                problem=problem,
                width_limit=width_limit,
                height_limit=height_limit,
                show_progress=show_progress,
            )
        elif strategy == "soft":
            rpp = PlacementRectanglePackingProblemAnnealerSoft(
                state=init_state,
                problem=problem,
                width_limit=width_limit,
                height_limit=height_limit,
                show_progress=show_progress,
            )
        else:
            raise ValueError("'strategy' must be either of ['hard', 'soft'].")

        signal.signal(signal.SIGINT, exit_handler)
        rpp.copy_strategy = "slice"  # We use "slice" since the state is a list
        rpp.set_schedule(rpp.auto(minutes=simanneal_minutes, steps=simanneal_steps))
        final_state, _ = rpp.anneal()

        # Convert simanneal's final_state to a Solution object
        gp, gn, rotations = rpp.retrieve_pairs(n=problem.n, state=final_state)
        seqpair = PlacementSequencePair(pair=(gp, gn))
        floorplan = seqpair.decode(problem=problem, rotations=rotations)

        return PlacementSolution(sequence_pair=seqpair, floorplan=floorplan, problem=problem)


class PlacementRectanglePackingProblemAnnealerHard(RectanglePackingProblemAnnealerHard):
    def __init__(self, state: List[int], problem: PlacementProblem, width_limit: float | None = None, height_limit: float | None = None, show_progress: bool = False) -> None:
        super().__init__(state, problem, width_limit, height_limit, show_progress)

    def energy(self) -> float:
        """
        Calculates energy of the actual floorplan.
            -> Energy = HPWL + sqrt(congestion)
        """
        
        # Pick up sequence-pair and rotations from state
        gp, gn, rotations = self.retrieve_pairs(n=self.problem.n, state=self.state)
        seqpair = PlacementSequencePair(pair=(gp, gn))
        floorplan = seqpair.decode(problem=self.problem, rotations=rotations)
        
        # Returns float max, if width/height limit is not satisfied
        if floorplan.bounding_box[0] > self.width_limit:
            return sys.float_info.max
        if floorplan.bounding_box[1] > self.height_limit:
            return sys.float_info.max

        return float(floorplan.HPWL()) + math.sqrt(floorplan.rudy_congestion())

class PlacementRectanglePackingProblemAnnealerSoft(RectanglePackingProblemAnnealerSoft):
    def __init__(self, state: List[int], problem: PlacementProblem, width_limit: float | None = None, height_limit: float | None = None, show_progress: bool = False) -> None:
        super().__init__(state, problem, width_limit, height_limit, show_progress)

    def energy(self) -> float:
        """
        Calculates energy of the actual floorplan.
            -> Energy = HPWL + sqrt(congestion)
        """
        # Pick up sequence-pair and rotations from state
        gp, gn, rotations = self.retrieve_pairs(n=self.problem.n, state=self.state)
        seqpair = PlacementSequencePair(pair=(gp, gn))
        floorplan = seqpair.decode(problem=self.problem, rotations=rotations)
        
        # Returns float max, if width/height limit is not satisfied
        if floorplan.bounding_box[0] > self.width_limit:
            return sys.float_info.max
        if floorplan.bounding_box[1] > self.height_limit:
            return sys.float_info.max

        return float(floorplan.HPWL()) + math.sqrt(floorplan.rudy_congestion())

