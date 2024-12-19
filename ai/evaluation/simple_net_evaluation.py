import chess
import torch
from ai.neural_network.simple_chess_net import SimpleChessNet
from ai.neural_network.utils import board_to_feature_vector
from .heuristic_evaluation import heuristic_evaluation

device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")

INPUT_SIZE = 839
HIDDEN_SIZE = 256
OUTPUT_SIZE = 1

SIMPLE_MODEL = SimpleChessNet(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE)
SIMPLE_MODEL.load_state_dict(torch.load("model/simple_model.pt", map_location=device))
SIMPLE_MODEL.to(device)
SIMPLE_MODEL.eval()

def evaluate_board_with_simple_net(board, move_history=None):
    # Blend simple net evaluation with heuristic
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
        nn_score = SIMPLE_MODEL(input_tensor).item()

    h_score = heuristic_evaluation(board, move_history)
    scaled_h = h_score / 1000.0
    final = 0.7 * nn_score + 0.3 * scaled_h
    return final * 1000.0
