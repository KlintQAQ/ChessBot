import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from ai.neural_network import SimpleChessNet

# Configuration
DATASET_FILE = "dataset/simple_dataset.npz"
MODEL_OUTPUT = "model/simple_model.pt"
BATCH_SIZE = 64
NUM_EPOCHS = 5
LEARNING_RATE = 0.001

def main():
    # Load dataset
    data = np.load(DATASET_FILE)
    inputs = data["inputs"]   # shape (N, input_size)
    labels = data["labels"]   # shape (N,)
    X = torch.tensor(inputs, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.float32).unsqueeze(1)  # (N, 1)

    # Create a dataset and split it into training and validation sets
    dataset = TensorDataset(X, y)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    # Create loaders for batches
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Initialize the simple neural network
    model = SimpleChessNet(input_size=839, hidden_size=256, output_size=1)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(NUM_EPOCHS):
        # Training phase
        model.train()
        total_train_loss = 0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item() * batch_x.size(0)

        avg_train_loss = total_train_loss / len(train_loader.dataset)

        # Validation phase
        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                total_val_loss += loss.item() * batch_x.size(0)
        avg_val_loss = total_val_loss / len(val_loader.dataset)

        print(f"Epoch [{epoch+1}/{NUM_EPOCHS}] Train Loss: {avg_train_loss:.4f} Val Loss: {avg_val_loss:.4f}")

    torch.save(model.state_dict(), MODEL_OUTPUT)
    print(f"Simple model saved to {MODEL_OUTPUT}")

if __name__ == "__main__":
    main()
