import chess
import torch
from ai.neural_network.policy_value_net import PolicyValueNet
from ai.neural_network.utils import board_to_feature_vector
from .heuristic_evaluation import heuristic_evaluation

device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")

INPUT_DIM = 839
POLICY_SIZE = 5760
HIDDEN_DIM = 256

PV_MODEL = PolicyValueNet(INPUT_DIM, POLICY_SIZE, HIDDEN_DIM)
PV_MODEL.load_state_dict(torch.load("model/policy_value_model.pt", map_location=device))
PV_MODEL.to(device)
PV_MODEL.eval()

def evaluate_board_with_policy_value(board, move_history=None):
    # Blend NN value with heuristic
    if board.is_game_over():
        result = board.result()
        if result == "1-0":
            return 1000
        elif result == "0-1":
            return -1000
        else:
            return 0

    fv = board_to_feature_vector(board)
    input_tensor = torch.tensor(fv, dtype=torch.float32).unsqueeze(0).to(device)
    with torch.no_grad():
        policy_out, value_out = PV_MODEL(input_tensor)
        nn_value = value_out.item()

    h_score = heuristic_evaluation(board, move_history)
    scaled_h = h_score / 1000.0
    final = 0.7 * nn_value + 0.3 * scaled_h
    return final * 1000.0
