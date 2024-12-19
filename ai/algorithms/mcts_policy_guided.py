import chess
import torch
import math
import numpy as np

from ai.algorithms.base import AIAlgorithm
from ai.neural_network.policy_value_net import PolicyValueNet
from ai.neural_network.utils import board_to_feature_vector, move_to_index
from ai.evaluation.policy_value_evaluation import evaluate_board_with_policy_value

DEVICE = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
MODEL_PATH = "model/policy_value_model.pt"
C_PUCT = 1.0
NUM_SIMULATIONS = 800
TEMPERATURE = 1e-3

class MCTSNode:
    def __init__(self, board, parent=None, move=None, prior=0.0):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = {}
        self.visits = 0
        self.value_sum = 0.0
        self.prior = prior

    def expanded(self):
        return len(self.children) > 0

    def value(self):
        if self.visits == 0:
            return 0.0
        return self.value_sum / self.visits

    def select_child(self):
        best_score = -float('inf')
        parent_visits = max(1, self.visits)
        best_child = None
        for child in self.children.values():
            q = child.value()
            u = C_PUCT * child.prior * math.sqrt(parent_visits) / (1 + child.visits)
            score = q + u
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self, action_priors):
        for move, prob in action_priors:
            new_board = self.board.copy()
            new_board.push(move)
            self.children[move] = MCTSNode(new_board, parent=self, move=move, prior=prob)

    def update(self, leaf_value):
        self.visits += 1
        self.value_sum += leaf_value

    def update_recursive(self, leaf_value):
        self.update(leaf_value)
        if self.parent:
            self.parent.update_recursive(-leaf_value)

class MCTS:
    def __init__(self, board, model, num_simulations=NUM_SIMULATIONS):
        self.root = MCTSNode(board)
        self.model = model
        self.num_simulations = num_simulations

    def run(self):
        """
        Runs MCTS simulations from the root.
        """
        for _ in range(self.num_simulations):
            node = self.root
            # Selection
            while node.expanded():
                node = node.select_child()

            # Evaluate leaf
            leaf_value = self.evaluate_leaf(node)

            # Expand if not terminal
            if not node.board.is_game_over():
                action_priors = self.get_action_priors(node.board)
                if action_priors:
                    node.expand(action_priors)

            # Backpropagation
            node.update_recursive(-leaf_value)

    def evaluate_leaf(self, node):
        """
        Evaluates a position at the leaf node.
        """
        board = node.board
        if board.is_game_over():
            result = board.result()
            if result == "1-0":
                return 1.0
            elif result == "0-1":
                return -1.0
            else:
                return 0.0
        val_cp = evaluate_board_with_policy_value(board)
        leaf_value = max(min(val_cp / 1000.0, 1.0), -1.0)
        return leaf_value

    def get_action_priors(self, board):
        """
        Gets move probabilities from the neural network policy.
        """
        if board.is_game_over():
            return []

        fv = board_to_feature_vector(board)
        input_tensor = torch.tensor(fv, dtype=torch.float32).unsqueeze(0).to(DEVICE)
        self.model.eval()
        with torch.no_grad():
            policy_logits, value = self.model(input_tensor)
            policy_probs = torch.softmax(policy_logits, dim=1).cpu().numpy()[0]

        legal_moves = list(board.legal_moves)
        action_priors = []
        for move in legal_moves:
            try:
                idx = move_to_index(move, board)
                prob = float(policy_probs[idx])
            except:
                # If indexing fails, assign a small probability
                prob = 1e-9
            action_priors.append((move, prob))

        total_prob = sum(p for _, p in action_priors)
        if total_prob > 0:
            action_priors = [(m, p / total_prob) for m, p in action_priors]

        return action_priors

    def choose_move(self, temperature=TEMPERATURE):
        """
        Chooses a move based on visit counts.
        """
        if len(self.root.children) == 0:
            return None

        visit_counts = [(child.visits, child.move) for child in self.root.children.values()]
        visits, moves = zip(*visit_counts)
        visits = np.array(visits, dtype=np.float32)

        # Prevent too-small temperature from causing overflow
        effective_temp = max(temperature, 1e-3)
        max_visits = 1e9
        visits_clipped = np.clip(visits, 1, max_visits)

        # Use logs to avoid overflow
        log_visits = np.log(visits_clipped)
        max_log = np.max(log_visits)

        # Compute exponents in a stable manner
        scaled_logs = (1/effective_temp) * (log_visits - max_log)
        probs = np.exp(scaled_logs)

        total = np.sum(probs)

        # Check for invalid probabilities
        if not np.isfinite(total) or total == 0:
            # fallback: choose move with max visits
            return moves[np.argmax(visits)]

        probs = probs / total
        if np.any(np.isnan(probs)):
            # fallback: choose move with max visits
            return moves[np.argmax(visits)]

        return np.random.choice(moves, p=probs)

    def update_root(self, move):
        """
        Moves the root forward after a chosen move.
        """
        if move in self.root.children:
            self.root = self.root.children[move]
            self.root.parent = None
        else:
            new_board = self.root.board.copy()
            new_board.push(move)
            self.root = MCTSNode(new_board)

def load_model(path=MODEL_PATH):
    """
    Loads the policy-value network.
    """
    input_dim = 839     # Must match training
    policy_size = 5760  # Must match training
    hidden_dim = 256
    model = PolicyValueNet(input_dim, policy_size, hidden_dim)
    model.load_state_dict(torch.load(path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

class MCTSPolicyGuided(AIAlgorithm):
    def __init__(self, num_simulations=NUM_SIMULATIONS, parallel=False):
        super().__init__(parallel=parallel)
        self.model = load_model()
        self.num_simulations = num_simulations

    def get_best_move(self, board: chess.Board, history: list = None, depth: int = None) -> chess.Move:
        mcts = MCTS(board, self.model, num_simulations=self.num_simulations)
        mcts.run()
        return mcts.choose_move()