import torch
import torch.nn as nn

class PolicyValueNet(nn.Module):
    def __init__(self, input_dim, policy_size, hidden_dim=256):
        super(PolicyValueNet, self).__init__()
        # A simple MLP: input -> hidden -> hidden -> separate heads for policy and value
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)

        # Policy head
        self.policy_head = nn.Linear(hidden_dim, policy_size)

        # Value head
        self.value_head = nn.Linear(hidden_dim, 1)

        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))

        policy_out = self.policy_head(x)     # shape: (batch, policy_size)
        value_out = self.value_head(x)        # shape: (batch, 1)
        value_out = torch.tanh(value_out)     # value in [-1, 1]

        return policy_out, value_out