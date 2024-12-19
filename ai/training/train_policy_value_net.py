import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from ai.neural_network import PolicyValueNet

# Configuration
DATASET_FILE = "dataset/policy_value_dataset.npz"
MODEL_OUTPUT = "model/policy_value_model.pt"
BATCH_SIZE = 64
NUM_EPOCHS = 5
LEARNING_RATE = 0.001

# Load dataset
data = np.load(DATASET_FILE)
inputs = data["inputs"]          # (N, input_dim): Feature vectors per position
policy_targets = data["policy"]  # (N, policy_size): Probability distribution of moves
value_targets = data["value"]    # (N,): Scalar position evaluations

# Convert to torch tensors
inputs_tensor = torch.from_numpy(inputs)
policy_tensor = torch.from_numpy(policy_targets)
value_tensor = torch.from_numpy(value_targets)

dataset = TensorDataset(inputs_tensor, policy_tensor, value_tensor)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

input_dim = inputs.shape[1]
policy_size = policy_targets.shape[1]

model = PolicyValueNet(input_dim, policy_size)
model.train()

# We have two predictions to train:
# 1. The "policy": a distribution over moves.
#    We'll compare the model's output (log probabilities) to the target distribution using KLDivLoss.
#
# 2. The "value": a single number in [-1,1].
#    We'll use MSELoss to compare predicted and target values.

policy_loss_fn = nn.KLDivLoss(reduction="batchmean")  # For comparing distributions
value_loss_fn = nn.MSELoss()                          # For comparing a single scalar value

# Use Adam optimizer for convenience
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

for epoch in range(NUM_EPOCHS):
    total_policy_loss = 0.0
    total_value_loss = 0.0
    total_loss = 0.0

    # Training loop
    for batch_inputs, batch_policy, batch_value in dataloader:
        # Clear previous gradients
        optimizer.zero_grad()

        # Forward pass: model outputs policy_out and value_out
        # policy_out: (batch, policy_size) - raw scores for each move
        # value_out: (batch, 1) - predicted scalar value
        policy_out, value_out = model(batch_inputs.float())

        # Convert policy_out to log probabilities for KLDivLoss
        policy_log_probs = torch.log_softmax(policy_out, dim=1)
        # policy_log_probs: the model's predicted log(probabilities)
        # batch_policy: the target probabilities for these positions

        # policy_loss measures how close the model's predicted distribution is to the target distribution.
        policy_loss = policy_loss_fn(policy_log_probs, batch_policy)

        # value_loss measures how close the model's predicted value is to the target value.
        # value_out is (batch,1) so we view as (batch,)
        value_loss = value_loss_fn(value_out.view(-1), batch_value.float())

        # Our total loss is the sum of policy and value losses.
        loss = policy_loss + value_loss

        # Backprop to adjust model weights
        loss.backward()
        optimizer.step()

        # Keep track of losses for stats
        total_policy_loss += policy_loss.item() * batch_inputs.size(0)
        total_value_loss += value_loss.item() * batch_inputs.size(0)
        total_loss += loss.item() * batch_inputs.size(0)

    # Compute average loss over the entire dataset for this epoch
    avg_policy_loss = total_policy_loss / len(dataset)
    avg_value_loss = total_value_loss / len(dataset)
    avg_loss = total_loss / len(dataset)

    print(f"Epoch {epoch+1}/{NUM_EPOCHS} - Loss: {avg_loss:.4f} (Policy: {avg_policy_loss:.4f}, Value: {avg_value_loss:.4f})")

# Save the model
torch.save(model.state_dict(), MODEL_OUTPUT)
print(f"Model saved to {MODEL_OUTPUT}")
