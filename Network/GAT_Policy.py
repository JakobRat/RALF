import torch.nn as nn

class GAT_Policy(nn.Module):
    def __init__(self, actor, critic) -> None:
        super().__init__()
        self.actor = actor
        self.critic = critic
    
    def forward(self, data):
        action_pred = self.actor(data)
        value_pred = self.critic(data)

        return action_pred, value_pred
