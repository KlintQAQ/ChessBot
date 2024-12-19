from abc import ABC, abstractmethod
import chess

class AIAlgorithm(ABC):
    """
    A simple base class for all AI-based chess strategies.
    It sets a common interface so each AI can pick moves in its own style.
    """
    
    def __init__(self, parallel=False):
        self.parallel = parallel
        self.num_workers = self.get_num_workers() if parallel else 1

    @staticmethod
    def get_num_workers():
        """
        Tries to figure out how many workers we can use in parallel.
        If it can’t, it sticks to a safe single-worker fallback.
        """
        try:
            from multiprocessing import cpu_count
            return max(1, int(cpu_count() * 0.75))
        except NotImplementedError:
            return 1

    @abstractmethod
    def get_best_move(self, board: chess.Board, history: list = None, depth: int = None) -> chess.Move:
        """
        Given a board, pick a good move.
        Different AIs will fill in their own unique methods.
        """
        pass
