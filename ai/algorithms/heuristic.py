import chess
from ai.algorithms.base import AIAlgorithm
from ai.evaluation.simple_net_evaluation import evaluate_board_with_simple_net


class Heuristic(AIAlgorithm):
    """
    A simple AI that uses a heuristic evaluation to pick moves.
    """

    def __init__(self, depth: int = 3):
        self.depth = depth

    def get_best_move(self, board: chess.Board, history: list = None) -> chess.Move:
        """
        Pick the best move by searching ahead a few moves.
        """
        best_move = None
        max_score = float('-inf')

        for move in board.legal_moves:
            board.push(move)
            score = self.minimax(board, self.depth - 1, False, float('-inf'), float('inf'))
            board.pop()

            if score > max_score:
                max_score = score
                best_move = move

        return best_move

    def minimax(self, board: chess.Board, depth: int, is_maximizing: bool, alpha: float, beta: float) -> float:
        """
        Basic minimax with alpha-beta pruning to evaluate moves.
        """
        if depth == 0 or board.is_game_over():
            return evaluate_board_with_simple_net(board)

        if is_maximizing:
            max_score = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                score = self.minimax(board, depth - 1, False, alpha, beta)
                board.pop()
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = float('inf')
            for move in board.legal_moves:
                board.push(move)
                score = self.minimax(board, depth - 1, True, alpha, beta)
                board.pop()
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return min_score
