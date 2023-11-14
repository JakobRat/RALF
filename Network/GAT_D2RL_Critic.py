# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 15:46:33 2023

@author: jakob
"""

import torch
from torch_geometric.nn import GATConv, MeanAggregation
from torch_geometric.nn.norm import BatchNorm
import torch.nn.functional as F

class GAT_D2RL_Critic(torch.nn.Module):
    def __init__(self):
        super().__init__()
        
        self.graph_embedding = GATConv(-1, 16, edge_dim=2)
        self.norm1 = BatchNorm(16)
        self.graph_embedding2 = GATConv(16, 16, edge_dim=2)
        self.mean_aggr = MeanAggregation()
        
        self.norm_lin1 = torch.nn.BatchNorm1d(16)
        self.lin_1 = torch.nn.Linear(16, 16)
        self.norm_lin2 = torch.nn.BatchNorm1d(32)
        self.lin_2 = torch.nn.Linear(32, 16)
        self.norm_lin3 = torch.nn.BatchNorm1d(32)
        self.lin_3 = torch.nn.Linear(32, 16)
        
        self.linear = torch.nn.Linear(16, 1)
        
    def forward(self, data):
        
        x = data.x
        edge_index = data.edge_index
        edge_attr = data.edge_attr
        batch = data.batch
            
        x_encoded = self.graph_embedding(x, edge_index, edge_attr=edge_attr)
        x_encoded = F.relu(x_encoded)
        x_encoded = self.norm1(x_encoded)
        x_encoded = self.graph_embedding2(x_encoded, edge_index, edge_attr=edge_attr)
        x_encoded = F.relu(x_encoded)
        x_encoded = self.mean_aggr(x_encoded, batch)

        x = self.norm_lin1(x_encoded)
        x = self.lin_1(x)
        x = F.relu(x)
        x = self.norm_lin2(torch.concatenate([x, x_encoded], dim=1))
        x = self.lin_2(x)
        x = F.relu(x)
        x = self.norm_lin3(torch.concatenate([x, x_encoded], dim=1))
        x = self.lin_3(x)
        x = F.relu(x)
        
        return self.linear(x)
        