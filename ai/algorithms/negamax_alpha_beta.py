from multiprocessing import Pool
import chess
from ai.algorithms.base import AIAlgorithm
from ai.evaluation.simple_net_evaluation import evaluate_board_with_simple_net


class NegamaxAlphaBeta(AIAlgorithm):
    """
    Negamax with alpha-beta pruning and optional parallelization.
    """

    def __init__(self, depth=3, parallel=False):
        super().__init__(parallel=parallel)
        self.depth = depth

    def get_best_move(self, board: chess.Board, history: list = None, depth: int = None) -> chess.Move:
        """
        Returns the best move found by negamax search.
        Uses parallel search if enabled and multiple workers are available.
        """
        depth = depth or self.depth
        if self.parallel and self.num_workers > 1:
            return self.negamax_parallel(board, depth, history)
        else:
            return self.negamax_sequential(board, depth, history)

    def negamax(self, board, depth, alpha, beta, color, history):
        """
        Negamax with alpha-beta pruning.
        Returns the best evaluation score for the current position.
        """
        if depth == 0 or board.is_game_over():
            return color * evaluate_board_with_simple_net(board, history)

        max_eval = float('-inf')

        for move in self.order_moves(board):
            if move.promotion:
                # Try all promotion types
                for promotion_piece in [chess.QUEEN, chess.KNIGHT, chess.ROOK, chess.BISHOP]:
                    move.promotion = promotion_piece
                    board.push(move)
                    history.append(board.fen())
                    eval = -self.negamax(board, depth - 1, -beta, -alpha, -color, history)
                    history.pop()
                    board.pop()

                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if alpha >= beta:
                        break
            else:
                board.push(move)
                history.append(board.fen())
                eval = -self.negamax(board, depth - 1, -beta, -alpha, -color, history)
                history.pop()
                board.pop()

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break

        return max_eval

    def negamax_sequential(self, board, depth, history):
        """
        Runs negamax search sequentially (single-threaded).
        Returns the best move found within the given depth.
        """
        best_move = None
        max_eval = float('-inf')
        alpha, beta = float('-inf'), float('inf')
        color = 1 if board.turn == chess.WHITE else -1

        for move in self.order_moves(board):
            board.push(move)
            history.append(board.fen())
            eval = -self.negamax(board, depth - 1, -beta, -alpha, -color, history)
            history.pop()
            board.pop()

            if eval > max_eval:
                max_eval = eval
                best_move = move

            alpha = max(alpha, eval)
            if alpha >= beta:
                break

        return best_move

    def negamax_parallel(self, board, depth, history):
        """
        Runs negamax search in parallel using multiple workers.
        Distributes moves among workers, then chooses the best result.
        """
        moves = list(self.order_moves(board))
        worker_args = [
            (board.copy(), move, depth, float('-inf'), float('inf'), 1 if board.turn == chess.WHITE else -1, history.copy())
            for move in moves
        ]

        with Pool(self.num_workers) as pool:
            results = pool.map(self.negamax_parallel_worker, worker_args)

        best_move = max(results, key=lambda x: x[1])[0]
        return best_move

    def negamax_parallel_worker(self, args):
        """
        Worker function for parallel negamax.
        Evaluates a single move at the given depth and returns (move, eval).
        """
        board, move, depth, alpha, beta, color, history = args
        board.push(move)
        history.append(board.fen())
        eval = -self.negamax(board, depth - 1, -beta, -alpha, -color, history)
        history.pop()
        board.pop()
        return move, eval

    def order_moves(self, board):
        """
        Orders moves to try promising moves first:
        captures, promotions, and checks have higher priority.
        """
        def move_score(move):
            score = 0
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                score += 10 + (captured_piece.piece_type if captured_piece else 0)
            if move.promotion:
                score += 20
            if board.gives_check(move):
                score += 5
            return score

        return sorted(board.legal_moves, key=move_score, reverse=True)
