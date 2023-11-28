# MIT License
#
# Copyright (c) 2022 Eric Yang Yu
#
# Copyright (c) 2023 Jakob Ratschenberger
#
# Modifications:
# - added init_weights method
# - Renamed class to Placement_PPO
# - Modified __init_ for the placement-environment and using a policy-network
# - Modified learn() for the improved PPO algorithm and added computation of KL-divergence
# - Modified rollout() for interacting with the placement-environment and for the improved PPO algorithm
# - Modified compute_rts() to normalize the output
# - added compute_advantages()
# - Modified get_action() for the used policy network and advantage estimation
# - Modified evaluate() for the used policy network
# - Modified _init_hyperparameters() for the improved PPO algorithm
# - Modified _log_summary() to include logging data regarding the placement-environment 
# - Added save_logs_to_csv()
# - Added plot_logs()
# - Added plot_grad_flow()
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

import time

import numpy as np
import time
import torch
from torch_geometric.loader import DataLoader
from torch_geometric.data import Data

import torch.nn as nn
from torch.optim import Adam


from Network.GAT_D2RL_Actor import GAT_D2RL_Actor
from Network.GAT_D2RL_Critic import GAT_D2RL_Critic
from Network.GAT_Policy import GAT_Policy

from Network.D2RL_Actor import D2RL_Actor
from Network.D2RL_Critic import D2RL_Critic

import matplotlib.pyplot as plt 

import copy

import logging

import pandas as pd

def init_weights(m):
    if type(m)==nn.Linear:
        torch.nn.init.orthogonal_(m.weight)
        m.bias.data.fill_(0)

class Placement_PPO:
    """Class to learn how to place a circuit using the PPO-algorithm.
    """
    def __init__(self, env, hyperparameters):
        
        self._init_hyperparameters(hyperparameters)
        self.env = env
        
        playground_size = self.env.size

        #Init actor and critic networks
        #self.actor = D2RL_Actor(playground_size[0], playground_size[1])
        #self.critic = D2RL_Critic()

        self.actor = GAT_D2RL_Actor(playground_size[0], playground_size[1])
        self.critic = GAT_D2RL_Critic()
        #self.critic.apply(init_weights)
        #self.actor.apply(init_weights)
        
        self.policy = GAT_Policy(self.actor, self.critic)
        
        #initialize the weights of the network
        self.policy.apply(init_weights)

        #Init optimizers for actor and critic
        self.actor_optim = Adam(self.actor.parameters(), lr=self.lr)
        self.critic_optim = Adam(self.critic.parameters(), lr=self.lr)
        self.policy_optim = Adam(self.policy.parameters(), lr=self.lr)

        #This logger will help us with printing out summaries of each iteration
        self.logger = {
			'delta_t': time.time_ns(),
			'placements_so_far': 0,          # placements so far
			'iterations_so_far': 0,          # iterations so far
			'batch_lens': [],       # episodic lengths in batch
			'batch_rews': [],       # episodic returns in batch
			'actor_losses': [],     # losses of actor network in current iteration
            'critic_losses': [],
            'policy_losses' : [],
            'avg_critic_loss' : [],
            'avg_rews' : [],
            'avg_actor_loss' : [],
            'avg_policy_loss' : [],
            'std_rews' : [],
            'KL_divergences' : [],
            'avg_KL_divergences' : [],
        }


        self.file_logger = logging.getLogger(__name__)

    
    
    def learn(self, total_placements):
        """Learn to place.
        """
        print(f"Learning to place for {total_placements} placements.")
        print(f"Doing {self.placements_per_batch} placements per batch.")
        
        self.file_logger.info(f"Learning to place for {total_placements} placements.")
        self.file_logger.info(f"Doing {self.placements_per_batch} placements per batch.")

        placements_so_far = 0 #track the done placements
        self.iterations_so_far = 0 #track the done iterations

        #set_start_method("spawn")

        while placements_so_far < total_placements:
            
            #check if we can stop early
            if len(self.logger['std_rews'])>100:
                mean_std = np.mean(np.array(self.logger['std_rews'][-100:]))
                if mean_std < self.stopping_std:
                    break
            
            start = time.time_ns()
            #roll-out the environment
            self.file_logger.debug(f"Rolling out the environment.")
            batch_obs, batch_acts, batch_log_probs, batch_rts, batch_advantages, batch_placements = self.rollout() 

            print(f"Rollout took: {(time.time_ns()-start)/1e6} ms")
            
            placements_so_far += batch_placements

            self.iterations_so_far += 1

            #iterations and placements so far
            self.logger["iterations_so_far"] = self.iterations_so_far
            self.logger["placements_so_far"] = placements_so_far

            start = time.time_ns()
            
            #Standardize the batch-returns
            #batch_rts = (batch_rts-batch_rts.mean())/(batch_rts.std()+1e-10)

            #Compute advantage estimates
            #V, _ = self.evaluate(batch_obs, batch_acts)
            #A = batch_rts - V.detach()

            #Standardize the advantage
            #A = (A-A.mean())/(A.std()+1e-10)

            #get the batch advantages
            A = batch_advantages.detach()
            #get the batch returns
            batch_rts = batch_rts.detach()
            #get the batch probabilities
            batch_log_probs = batch_log_probs.detach()
            #get the batch actions
            batch_acts = batch_acts.detach()

            actor_losses = []
            critic_losses = []
            policy_losses = []
            KL_divergences = []
            #Optimize the networks
            for _ in range(self.n_updates_per_iteration):
                
                self.file_logger.debug(f"Optimization round {_}/{self.n_updates_per_iteration}.")
                self.file_logger.debug(f"Evaluating batch.")

                #Calculate actual state-value and pi_theta(a_t | s_t)
                V, step_log_prob = self.evaluate(batch_obs, batch_acts)

                #Calculate the probability ratio
                # r_t(theta) = pi_theta(a_t | s_t)/pi_theta_old(a_t | s_t)
                ratios = torch.exp(step_log_prob-batch_log_probs)

                #Calculate the surrogate losses
                surr1 = ratios * A
                surr2 = torch.clamp(ratios, 1-self.clip, 1+self.clip)*A

                #Calculate actor and critic loss
                actor_loss = (-torch.min(surr1,surr2)).mean()
                critic_loss = nn.MSELoss()(V,batch_rts)
                policy_loss = actor_loss + 0.5*critic_loss

                #KL approximation
                KL_approx = (ratios*torch.log(ratios)-(torch.add(ratios, torch.tensor(-1.0)))).mean()

                #Do the optimization
                """
                # Old routine, save as commend if needed in future works
                self.file_logger.debug(f"Optimizing the actor.")
                self.actor_optim.zero_grad()
                actor_loss.backward(retain_graph=True)
                torch.nn.utils.clip_grad_norm_(self.actor.parameters(), 5)
                self.actor_optim.step()

                if self.plot_grad_flow:
                    plot_grad_flow(self.actor.named_parameters(), "Actor")
                
                self.file_logger.debug(f"Optimizing the critic.")
                self.critic_optim.zero_grad()
                critic_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.critic.parameters(),5)
                self.critic_optim.step()

                if self.plot_grad_flow:
                    plot_grad_flow(self.critic.named_parameters(), "Critic")

                self.logger['actor_losses'].append(actor_loss.detach())
                self.logger['critic_losses'].append(critic_loss.detach())"""

                self.policy_optim.zero_grad()
                policy_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.policy.parameters(),5)
                self.policy_optim.step()

                actor_losses.append(actor_loss.item())
                critic_losses.append(critic_loss.item())
                policy_losses.append(policy_loss.item())
                KL_divergences.append(KL_approx.item())

                print(f"KL={KL_approx.item()}")

            print(f"Optimization took: {(time.time_ns()-start)/1e6} ms")

            self.logger['actor_losses'].append(actor_losses)
            self.logger['critic_losses'].append(critic_losses)
            self.logger['policy_losses'].append(policy_losses)
            self.logger['KL_divergences'].append(KL_divergences)
            
            self._log_summary()

            if self.plot_log:
                self.plot_logs(title=self.env.name)

            if self.iterations_so_far % self.save_freq == 0:
                torch.save(self.actor.state_dict(), 'Network/Weights/ppo_actor.pth')
                torch.save(self.critic.state_dict(), 'Network/Weights/ppo_critic.pth')
        
        self.save_logs_to_csv()
        self.env.save_logs_to_csv()

    def rollout(self):
        """Rollout the environment.

        Returns:
            tuple[DataLoader, Tensor, Tensor, Tensor, Tensor, int]: 
                - DataLoader: Batch observations
                - Tensor: Batch actions
                - Tensor: Batch log. probabilities
                - Tensor: Batch returns
                - Tensor: Batch advantages
                - int: Number of done placements
        """

        #setup lists to store batch-data
        batch_obs = []
        batch_acts = []
        batch_log_probs = []
        batch_values = []
        batch_rews = []
        batch_placements = 0

        episode_rews = []

        while batch_placements < self.placements_per_batch:
            #rollout a episode - a placement
            #reset the rewards of the episode
            episode_rews = []

            self.file_logger.debug(f"Rolling out placement {batch_placements}/{self.placements_per_batch}.")
            #Reset the environment
            obs, info = self.env.reset()

            done = False

            #reset the episodic data
            episode_obs = []
            episode_acts = []
            episode_log_probs = []
            episode_values = []
            #run until all devices are placed
            while not done: 

                #save the observation
                episode_obs.append(copy.deepcopy(obs))

                #get next action which shall be performed
                action, log_prob, value = self.get_action(obs)
              
                coord = (int(action[0]), int(action[1]))
                rot = int(action[2])

                #perform the action in the environment
                obs, rew, term, trunc, info = self.env.step(coord, rot)
                
                d_pl = info

                #store the data
                episode_rews.append(rew)
                episode_acts.append(action)
                episode_log_probs.append(log_prob)
                episode_values.append(value)
                done = term or trunc

                if done: #placement finished
                    if self.render:
                        self.env.render() #render the result

            
            #store the episode
            batch_obs.extend(episode_obs)
            batch_acts.extend(episode_acts)
            batch_rews.append(episode_rews)
            batch_log_probs.extend(episode_log_probs)
            batch_values.append(episode_values)
            batch_placements += 1
        
        #setup a DataLoader to store the batch-data
        batch_obs = DataLoader(batch_obs, batch_size=len(batch_obs))
        #setup a tensor to store the batch actions
        batch_acts = torch.tensor(np.stack(batch_acts), dtype=torch.float)
        #setup a tensor to store the batch log. probabilities
        batch_log_probs = torch.stack(batch_log_probs).squeeze()
        #get the batch returns
        batch_rts = self.compute_rts(batch_rews)
        #get the batch advantages
        batch_advantages = self.compute_advantages(batch_rews, batch_values)

        self.logger['batch_rews'] = batch_rews
        
        return batch_obs, batch_acts, batch_log_probs, batch_rts, batch_advantages, batch_placements

    def compute_rts(self, batch_rews : list[list], normalize=True) -> torch.Tensor:
        """
            Compute the discounted return for each step.
        
        Args:
            batch_rews (list[list]): List of episodic rewards.
            normalize (bool): If True, the output will be normalized. Defaults to True.
        
        Returns:
            torch.Tensor: Tensor of the discounted return.
        """ 
        batch_rts = []
        #iterate over the batches reversed
        for episode_rews in reversed(batch_rews):
            discounted_reward = 0
            #iterate over the episode rewards - reversed
            for rew in reversed(episode_rews):
                #calculate the discounted reward
                discounted_reward = rew + discounted_reward*self.gamma
                batch_rts.insert(0, discounted_reward)

        #setup a tensor with the returns
        batch_rts = torch.tensor(batch_rts, dtype=torch.float)

        if normalize:
            #normalize the batch
            batch_rts = (batch_rts-batch_rts.mean())/(batch_rts.std()+1e-10)

        return batch_rts
    
    def compute_advantages(self, batch_rews : list[list], batch_values : list[list], normalize=True) -> torch.Tensor:
        """Compute the advantages, by generalized advantage estimation (GAE).

        Args:
            batch_rews (list[list]): List of episodic rewards.
            batch_values (list[list]): List of episodic values (outputs of the Value-Network).
            normalize (bool, optional): If True, the output will be normalized.. Defaults to True.

        Returns:
            torch.Tensor: Tensor of the batches advantages.
        """

        advantages = []
        #iterate over the episodic rewards and values
        for episode_rews, episode_values in zip(reversed(batch_rews), reversed(batch_values)):
            advantage = 0
            next_value = 0
            #iterate over the rewards and values (reversed)
            for r,v in zip(reversed(episode_rews), reversed(episode_values)):
                #calculate the TD residual (estimated advantage of actual action)
                # delta_t = r_t + gamma*V(s_{t+1})-V(s_t)
                td_error = r + next_value * self.gamma - v
                #calculate the advantage of the actual action
                # A_t = delta_t + gamma*lambda*A_{t+1}
                advantage = td_error + advantage * self.gamma * self.trace_decay
                next_value = v
                advantages.insert(0,advantage)
        
        advantages = torch.tensor(advantages)
        if normalize:
            advantages = (advantages-advantages.mean())/(advantages.std()+1e-10)
        
        return advantages

    def get_action(self, obs : Data) -> tuple[np.ndarray, torch.Tensor, torch.Tensor]:
        """Get the action for observation <obs>.

        Args:
            obs (Data): Observation. (Environment data)

        Returns:
            tuple[np.ndarray, torch.Tensor, torch.Tensor]: 
                - action: [action_x, action_y, action_rot]
                - log. probability of the action
                - estimated value of the action
        """

        #evaluate the policy network
        self.policy.eval()
        with torch.no_grad():
            actions, value_pred = self.policy(obs)

        #setup a CDF for the actions
        action_x, action_y, action_rot = actions[0], actions[1], actions[2]
        distr_x = torch.distributions.Categorical(action_x)
        distr_y = torch.distributions.Categorical(action_y)
        distr_rot = torch.distributions.Categorical(action_rot)

        #sample actions
        action_x = distr_x.sample()
        action_y = distr_y.sample()
        action_rot = distr_rot.sample()

        # calculate the log. prob. of an action
        # See taken actions as independent events
        # -> P(action) = P(action_x)*P(action_y)*P(action_rot)
        log_prob = distr_x.log_prob(action_x) + distr_y.log_prob(action_y) + distr_rot.log_prob(action_rot)

        #stack the sampled actions
        action = torch.stack((action_x, action_y, action_rot))

        #self.critic.eval()
        #value_pred = self.critic(obs)

        return action.squeeze().detach().numpy(), log_prob.detach(), value_pred
    
    def evaluate(self, batch_obs : DataLoader, batch_acts : torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
            Evaluate the batches, for policy-training.
        
        Args:
            batch_obs (DataLoader): Batched observations.
            batch_acts (torch.Tensor): Batched actions.
        
        Returns:
            tuple[torch.Tensor, torch.Tensor]:
                - Estimated values of the actions.
                - Log. probabilities of the actions.
        """
        #get the batch
        batch = next(iter(batch_obs))
        
        #train the policy and get the actions and values
        self.policy.train()
        actions, V = self.policy(batch)

        action_x, action_y, action_rot = actions[0], actions[1], actions[2]
        
        #setup CDFs for the actions
        self.file_logger.debug("Setting up the distributions.")
        distr_x = torch.distributions.Categorical(action_x)
        distr_y = torch.distributions.Categorical(action_y)
        distr_rot = torch.distributions.Categorical(action_rot)

        #get the done actions
        self.file_logger.debug("Getting the actions.")
        action_x = batch_acts[:,0]
        action_y = batch_acts[:,1]
        action_rot = batch_acts[:,2]

        #get the log. probabilities of the actions under current policy
        self.file_logger.debug("Getting the log_probs.")
        log_probs = distr_x.log_prob(action_x) + distr_y.log_prob(action_y) + distr_rot.log_prob(action_rot)
        
        V = V.squeeze()
        return V, log_probs
    

    def _init_hyperparameters(self, hyperparameters : dict):
        """Initialize the hyperparameters of the algorithm.

        Args:
            hyperparameters (dict): key: Name of the hyperparameter, value: Value of the hyperparameter

        Raises:
            ValueError: If no valid seed is given.
        """
        #Hyperparameters for the algorithm
        self.placements_per_batch = 1000    #number of placements per batch
        self.n_updates_per_iteration = 5    #number of updates taken per iteration
        self.lr = 0.005                     #learning rate for network optimization
        self.gamma = 0.95                   #discount factor for return shaping
        self.clip = 0.2                     #clip hyperparameter for PPO
        self.stopping_std = 500             #max reward std. after which the algorithm will stop early 
        self.trace_decay = 0.99             #trace decay for general advantage estimation                  

        #Control parameters
        self.render = False                 #render the environment
        self.save_freq = 10                 #save the network weights all save_freq iterations
        self.seed = None                    #set a seed
        self.plot_grad_flow = False         #plot the gradient-flow of the networks
        self.plot_log = False               #plot the logging information
        self.save_to_csv = True             #save data to a CSV file

        #Change default hyperparameters if specified
        for k,v in hyperparameters.items():
            exec(f"self.{k} = {v}")

        #set the seed
        if self.seed != None:
            try:
                torch.manual_seed(self.seed)
                print(f"Set seed to {self.seed}")
            except:
                raise ValueError("No valid seed given!")
            
    def _log_summary(self):
        """Print a summary of the logged data.
        """
        delta_t = self.logger['delta_t']
        self.logger['delta_t'] = time.time_ns()
        delta_t = (self.logger['delta_t']-delta_t)/1e9

        placements_so_far = self.logger["placements_so_far"]
        iterations_so_far = self.logger["iterations_so_far"]

        avg_episode_rews = np.mean([np.sum(rews) for rews in self.logger["batch_rews"]])
        std_episode_rews = np.std([np.sum(rews) for rews in self.logger["batch_rews"]])
        
        avg_actor_loss = np.mean(self.logger['actor_losses'][-1])
        avg_critic_loss = np.mean(self.logger['critic_losses'][-1])
        avg_policy_loss = np.mean(self.logger['policy_losses'][-1])
        avg_KL_divergences = np.mean(self.logger['KL_divergences'][-1])

        self.logger['avg_rews'].append(round(avg_episode_rews, 2))
        self.logger['std_rews'].append(round(std_episode_rews, 2))

        self.logger['avg_actor_loss'].append(round(avg_actor_loss, 5))
        self.logger['avg_critic_loss'].append(round(avg_critic_loss, 5))
        self.logger['avg_policy_loss'].append(round(avg_policy_loss, 5))
        self.logger['avg_KL_divergences'].append(round(avg_KL_divergences, 5))

        mean_hpwl = round(np.mean(np.array(self.env.HPWLs[:self.placements_per_batch])),2)
        
        # Print logging statements
        print(flush=True)
        print(f"-------------------- Iteration #{iterations_so_far} --------------------", flush=True)
        print(f"Average Episodic Return: {avg_episode_rews}", flush=True)
        print(f"Mean HPWL: {mean_hpwl}", flush=True)
        print(f"Average Actor Loss: {avg_actor_loss}", flush=True)
        print(f"Average Critic Loss: {avg_critic_loss}", flush=True)
        print(f"Average Policy Loss: {avg_policy_loss}", flush=True)
        print(f"Average KL divergences: {avg_KL_divergences}", flush=True)
        print(f"Placements So Far: {placements_so_far}", flush=True)
        print(f"Iteration took: {delta_t} secs", flush=True)
        print(f"------------------------------------------------------", flush=True)
        print(flush=True)

        # Reset batch-specific logging data
        self.logger['batch_rews'] = []
        self.logger['actor_losses'] = []
        self.logger['critic_losses'] = []
        self.logger['policy_lisse'] = []
        self.logger['KL_divergences'] = []

    def save_logs_to_csv(self):
        """
            Save the logged data to a CSV file.
            The file will be located under Logs/<environment_name>_training_log.csv
        """
        data = {
                'avg_rews' : self.logger['avg_rews'],
                'std_rews' : self.logger['std_rews'],
                'avg_actor_loss' : self.logger['avg_actor_loss'],
                'avg_critic_loss' : self.logger['avg_critic_loss'],
                'avg_policy_loss' : self.logger['avg_policy_loss'],
                'avg_kl_divergence': self.logger['avg_KL_divergences'],
        }

        dataframe = pd.DataFrame(data)
        filename = "Logs/" + self.env.name + "_training_log.csv"

        dataframe.to_csv(filename)

    def plot_logs(self, title : str):
        """Plot the logged data.

        Args:
            title (str): Title of the plot
        """
        x = np.arange(len(self.logger['avg_rews']))
        plt.subplot(3,1,1)
        plt.plot(x,np.array(self.logger['avg_rews']))
        plt.ylabel('Average returns')
        plt.xlabel("Iteration")
        plt.subplot(3,1,2)
        plt.plot(x,np.array(self.logger['avg_critic_loss']))
        plt.ylabel('Average critic loss')
        plt.xlabel("Iteration")
        plt.subplot(3,1,3)
        plt.plot(x,np.array(self.logger['avg_actor_loss']))
        plt.ylabel('Average actor loss')
        plt.xlabel("Iteration")
        
        plt.suptitle(f"Logs - {title}")
        plt.show()

def plot_grad_flow(named_parameters, title):
    """Plot the gradient flow across the policy network.

    Args:
        named_parameters (tuple): Named parameters of the network.
        title (str): Title of the plot.
    """
    ave_grads = []
    max_grads= []
    layers = []
    for n, p in named_parameters:
        if(p.requires_grad) and ("bias" not in n):
            layers.append(n)
            ave_grads.append(p.grad.abs().mean())
            max_grads.append(p.grad.abs().max())
    
    plt.bar(np.arange(len(max_grads)), max_grads, alpha=0.1, lw=1, color="c")
    plt.bar(np.arange(len(max_grads)), ave_grads, alpha=0.1, lw=1, color="b")
    plt.hlines(0, 0, len(ave_grads)+1, lw=2, color="k" )
    plt.xticks(range(0,len(ave_grads), 1), layers, rotation="vertical")
    plt.xlim(left=0, right=len(ave_grads))
    #plt.ylim(bottom = -0.001, top=0.02) # zoom in on the lower gradient regions
    plt.xlabel("Layers")
    plt.ylabel("average gradient")
    plt.title(f"Gradient flow - {title}")
    plt.grid(True)
    plt.legend([plt.Line2D([0], [0], color="c", lw=4),
                plt.Line2D([0], [0], color="b", lw=4),
                plt.Line2D([0], [0], color="k", lw=4)], ['max-gradient', 'mean-gradient', 'zero-gradient'])
    plt.show()
