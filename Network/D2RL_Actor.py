# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 10:12:56 2023

@author: jakob
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 15:46:33 2023

@author: jakob
"""

import torch
from torch_geometric.nn import SAGEConv, MeanAggregation
from torch_geometric.nn.norm import BatchNorm
import torch.nn.functional as F


class D2RL_Actor(torch.nn.Module):
    def __init__(self, out_dim_x, out_dim_y):
        super().__init__()
        
        self.conv1 = SAGEConv(-1, 16)
        self.norm1 = BatchNorm(16)
        self.conv2 = SAGEConv(16, 16)       
        self.mean_aggr = MeanAggregation()
        
        
        self.norm_lin1 = torch.nn.BatchNorm1d(16)
        self.lin_1 = torch.nn.Linear(16, 16)
        self.norm_lin2 = torch.nn.BatchNorm1d(32)
        self.lin_2 = torch.nn.Linear(32, 16)
        self.norm_lin3 = torch.nn.BatchNorm1d(32)
        self.lin_3 = torch.nn.Linear(32, 16)
        
        
        self.linear_x = torch.nn.Linear(16, out_dim_x)
        self.linear_y = torch.nn.Linear(16, out_dim_y)
        self.linear_rot = torch.nn.Linear(16, 4)
        
    def forward(self, data):

        x = data.x
        edge_index = data.edge_index
        batch = data.batch
            
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.norm1(x)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x_encoded = self.mean_aggr(x, batch)
        x = self.norm_lin1(x_encoded)
        x = self.lin_1(x)
        x = F.relu(x)
        x = self.norm_lin2(torch.concatenate([x, x_encoded], dim=1))
        x = self.lin_2(x)
        x = F.relu(x)
        x = self.norm_lin3(torch.concatenate([x, x_encoded], dim=1))
        x = self.lin_3(x)
        x = F.relu(x)
        
        y = self.linear_y(x)
        xx = self.linear_x(x)

        y = F.softmax(y, dim=1)
        xx = F.softmax(xx, dim=1)
        rot = self.linear_rot(x)
        rot = F.softmax(rot, dim=1)
        

        return xx, y, rot
        