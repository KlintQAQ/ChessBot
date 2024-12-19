import chess
from abc import ABC, abstractmethod
from ai.algorithms.base import AIAlgorithm

class BasePlayer(ABC):
    """
    A base class for all players.
    Both HumanPlayer and AIPlayer must implement get_move().
    """

    @abstractmethod
    def get_move(self, board, move_history=None):
        """
        Return a move for the current position.
        board: current chess.Board state
        move_history: previous moves or states
        """
        pass

class HumanPlayer(BasePlayer):
    """
    A human player. For a GUI, we might not actually use get_move().
    """
    is_ai = False

    def get_move(self, board: chess.Board, move_history=None):
        # In a GUI scenario, this might never be called.
        # If you want console input, implement it here.
        raise NotImplementedError("Human moves handled by GUI, not console.")

class AIPlayer(BasePlayer):
    """
    An AI player that uses a given AI algorithm to pick moves.
    """

    def __init__(self, ai_algorithm: AIAlgorithm):
        """
        ai_algorithm: an object that implements get_best_move(board, move_history)
        """
        self.ai_algorithm = ai_algorithm

    def get_move(self, board: chess.Board, move_history=None):
        """
        Ask the AI algorithm for the best move and return it.
        If there's any error (e.g. AI logic), we print it and re-raise.
        """
        try:
            return self.ai_algorithm.get_best_move(board, move_history)
        except Exception as e:
            print(f"AI had a problem picking a move: {e}")
            raise
