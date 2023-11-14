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

def test(env, actor_model):
    """Test the trained policy.

    WARNING: Experimental function, no longer needed!

    Args:
        env (Placement): Placement environment.
        actor_model (str): Weights-file of the actor-model.
    """
    print(f"Testing {actor_model}", flush=True)
    if actor_model == '':
        print(f"Didn't specify model file!", flush=True)
		
    playground_size = env.size
    policy = D2RL_Actor(playground_size[0], playground_size[1])

    policy.load_state_dict(torch.load(actor_model))
    
    
    obs, info = env.reset()
    
    #run until all devices are placed
    done = False
    valid = True
    placed_dev = info
    while not done: 
        
        action_x, action_y, action_rot = get_action(policy, obs)
        coord = (int(action_x), int(action_y))
        rot = int(action_rot)
        
        obs, rew, term, trunc, _ = env.step(coord, rot)
        print(f"Placed {placed_dev} with reward: {rew}")
        placed_dev = _
        done = term or trunc



def get_action(policy, obs):
    """Get an action.

        WARNING: Experimental function, no longer needed!
    
    """
    policy.eval()
    action_x, action_y, action_rot = policy(obs)

    distr_x = torch.distributions.Categorical(action_x)
    distr_y = torch.distributions.Categorical(action_y)
    distr_rot = torch.distributions.Categorical(action_rot)

    action_x = distr_x.sample()
    action_y = distr_y.sample()
    action_rot = distr_rot.sample()

    return action_x, action_y, action_rot