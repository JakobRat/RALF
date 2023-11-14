# MIT License
#
# Copyright (c) 2022 Eric Yang Yu
#
# Copyright (c) 2023 Jakob Ratschenberger
#
# Modifications:
# - Modified train() to use a placement-environment and to define the total number of placements
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Environment.Environment import Placement

import matplotlib.pyplot as plt
import torch
import sys
import numpy as np

from PPO.Placement_PPO import Placement_PPO
from Network.D2RL_Actor import D2RL_Actor


def train(env : Placement, hyperparameters : dict, actor_model : str = '', critic_model : str = '', total_placements=200e6):
    """Train a policy network to learn placing cells.

    Args:
        env (Placement): Placement environment.
        hyperparameters (dict): Hyperparameters of the PPO algorithm.
        actor_model (str, optional): Weights-file of the actor-model. Defaults to ''.
        critic_model (str, optional): Weights-file of the critic-model. Defaults to '':
        total_placements (int, optional): Number of total-placements which shall be performed. Defaults to 200e6.
    """
    print(f"Training", flush=True)
    #setup a model to train the policy
    model = Placement_PPO(env, hyperparameters)
        
    if actor_model != '' and critic_model != '':
        print(f"Loading in {actor_model} and {critic_model}...", flush=True)
        model.actor.load_state_dict(torch.load(actor_model))
        model.critic.load_state_dict(torch.load(critic_model))
        print(f"Successfully loaded.", flush=True)
    elif actor_model != '' or critic_model != '': # Don't train from scratch if user accidentally forgets actor/critic model
        print(f"Error: Either specify both actor/critic models or none at all. We don't want to accidentally override anything!")
        sys.exit(0)
    else:
        print(f"Training from scratch.", flush=True)

    #learn to place
    model.learn(total_placements=total_placements)
