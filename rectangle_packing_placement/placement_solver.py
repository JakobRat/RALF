# Copyright 2022 Kotaro Terada
#
# Copyright 2023 Jakob Ratschenberger
#
# Modifications:
# - Updated SequencePair to PlacementSequencePair
# - Introduced PlacementRectanglePackingProblemAnnealerSoft for the placement task
# - Introduced PlacementRectanglePackingProblemAnnealerHard for the placement task
# - Introduced n_placements to control the number of done placements
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
import pandas

class PlacementSolver(Solver):
    def __init__(self) -> None:
        super().__init__()

    def solve(
        self,
        problem: Problem,
        width_limit: Optional[float] = None,
        height_limit: Optional[float] = None,
        simanneal_minutes: float = 0.1,
        simanneal_steps: int = 100,
        n_placements: int = 100,
        show_progress: bool = False,
        seed: Optional[int] = None,
    ) -> PlacementSolution:
        if seed:
            random.seed(seed)

        if not isinstance(problem, Problem):
            raise TypeError("Invalid argument: 'problem' must be an instance of Problem.")

        # If width/height limits are not given...
        if (width_limit is None) and (height_limit is None):
            return self._solve_with_strategy(
                problem,
                width_limit,
                height_limit,
                None,
                simanneal_minutes,
                simanneal_steps,
                n_placements,
                show_progress,
                strategy="hard",
            )

        # If width/height limits are given...
        if width_limit is None:
            width_limit = sys.float_info.max
        if height_limit is None:
            height_limit = sys.float_info.max
        max_width = max([min(r["width"], r["height"]) if r["rotatable"] else r["width"] for r in problem.rectangles])
        max_height = max([min(r["width"], r["height"]) if r["rotatable"] else r["height"] for r in problem.rectangles])
        if width_limit < max_width:
            raise ValueError(
                f"'width_limit' must be greater than or equal to {max_width} "
                + "(= the largest width of the given problem)."
            )
        if height_limit < max_height:
            raise ValueError(
                f"'height_limit' must be greater than or equal to {max_height} "
                + "(= the largest height of the given problem)."
            )

        # If constraints of width and/or hight are given,
        # we can use two kinds of annealer in a hybrid way.
        # - 1) Hard constraints strategy:
        #      Find a solution so that the width/height limits must be met. Sometimes no solutions will be found.
        # - 2) Soft constraints strategy:
        #      Find a solution with smallest area as possible, the width/height limits may not be met.
        if (width_limit < sys.float_info.max) and (height_limit < sys.float_info.max):
            return self._solve_with_strategy(
                problem,
                width_limit,
                height_limit,
                None,
                simanneal_minutes,
                simanneal_steps,
                n_placements,
                show_progress,
                strategy="soft",
            )
        else:
            return self._solve_with_strategy(
                problem,
                width_limit,
                height_limit,
                None,
                simanneal_minutes,
                simanneal_steps,
                n_placements,
                show_progress,
                strategy="hard",
            )

    def _solve_with_strategy(self, problem: PlacementProblem, 
                             width_limit: float | None = None, 
                             height_limit: float | None = None, 
                             initial_state: List[int] | None = None, 
                             simanneal_minutes: float = 0.1, 
                             simanneal_steps: int = 100,
                             n_placements: int = 100, 
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
        schedule = rpp.auto(minutes=simanneal_minutes, steps=simanneal_steps)

        #if the number of placements were specified
        if not (n_placements is None):
            schedule['steps'] = n_placements #override the number of performed steps as the given
            schedule['updates'] = n_placements #update the logging after each step
        rpp.set_schedule(schedule)
        final_state, _ = rpp.anneal()

        # Convert simanneal's final_state to a Solution object
        gp, gn, rotations = rpp.retrieve_pairs(n=problem.n, state=final_state)
        seqpair = PlacementSequencePair(pair=(gp, gn))
        floorplan = seqpair.decode(problem=problem, rotations=rotations)

        data = pandas.DataFrame(rpp.logger)
        data.to_csv(f"Logs/{problem.circuit.name}_simanneal_log.csv")

        return PlacementSolution(sequence_pair=seqpair, floorplan=floorplan, problem=problem)


class PlacementRectanglePackingProblemAnnealerHard(RectanglePackingProblemAnnealerHard):
    def __init__(self, state: List[int], problem: PlacementProblem, width_limit: float | None = None, height_limit: float | None = None, show_progress: bool = False) -> None:
        super().__init__(state, problem, width_limit, height_limit, show_progress)
        self.logger = {
            'step' : [],
            'T' : [],
            'E' : [],
            'acceptance' : [],
            'improvement' : [],
        }

    def logging(self, step, T, E, acceptance, improvement):
        """Add the actual data to the logger.

        Args:
            step (int): Current step
            T (float): Current temperature
            E (float): Current energy
            acceptance (float): Acceptance rate
            improvement (float): Improvement rate
        """
        self.logger['step'].append(step)
        self.logger['T'].append(T)
        self.logger['E'].append(E)
        self.logger['acceptance'].append(acceptance)
        self.logger['improvement'].append(improvement)

    def update(self, step: int, T: int, E: float, acceptance: float, improvement: float) -> None:
        """Add the logging to the update method.
        """
        super().update(step, T, E, acceptance, improvement)
        self.logging(step, T, E, acceptance, improvement)    


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
        self.logger = {
            'step' : [],
            'T' : [],
            'E' : [],
            'acceptance' : [],
            'improvement' : [],
        }

    def logging(self, step, T, E, acceptance, improvement):
        """Add the actual data to the logger.

        Args:
            step (int): Current step
            T (float): Current temperature
            E (float): Current energy
            acceptance (float): Acceptance rate
            improvement (float): Improvement rate
        """
        self.logger['step'].append(step)
        self.logger['T'].append(T)
        self.logger['E'].append(E)
        self.logger['acceptance'].append(acceptance)
        self.logger['improvement'].append(improvement)

    def update(self, step: int, T: int, E: float, acceptance: float, improvement: float) -> None:
        """Add the logging to the update method.
        """
        super().update(step, T, E, acceptance, improvement)
        self.logging(step, T, E, acceptance, improvement)

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

