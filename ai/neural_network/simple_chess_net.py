import torch
import torch.nn as nn

class SimpleChessNet(nn.Module):
    def __init__(self, input_size=839, hidden_size=256, output_size=1):
        super(SimpleChessNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x
