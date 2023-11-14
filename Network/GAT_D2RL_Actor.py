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

import torch
from torch_geometric.nn import GATConv, MeanAggregation
from torch_geometric.nn.norm import BatchNorm
import torch.nn.functional as F


class GAT_D2RL_Actor(torch.nn.Module):
    def __init__(self, out_dim_x, out_dim_y):
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
        
        
        self.linear_x = torch.nn.Linear(16, out_dim_x)
        self.linear_y = torch.nn.Linear(16, out_dim_y)
        self.linear_rot = torch.nn.Linear(16, 4)
        
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
        
        y = self.linear_y(x)
        y = F.softmax(y, dim=1)
        xx = self.linear_x(x)
        xx = F.softmax(xx, dim=1)
        rot = self.linear_rot(x)
        rot = F.softmax(rot, dim=1)

        return xx, y, rot
        