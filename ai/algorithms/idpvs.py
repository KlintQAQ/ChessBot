import chess
from multiprocessing import Pool
from ai.algorithms.base import AIAlgorithm
from ai.evaluation.simple_net_evaluation import evaluate_board_with_simple_net


class IDPVS(AIAlgorithm):
    """
    Uses Iterative Deepening Principal Variation Search to find moves.
    """

    def __init__(self, depth=3, parallel=False):
        super().__init__(parallel=parallel)
        self.depth = depth
        self.transposition_table = {}

    def get_best_move(self, board: chess.Board, history: list = None, depth: int = None) -> chess.Move:
        depth = depth or self.depth
        if self.parallel and self.num_workers > 1:
            return self.idpvs_parallel(board, depth, history)
        else:
            return self.idpvs_sequential(board, depth, history)

    def idpvs(self, board, depth, alpha, beta, color, history):
        """
        Principal Variation Search with alpha-beta pruning.
        """
        fen = board.fen()

        # Check if we’ve seen this position before
        if fen in self.transposition_table:
            stored_depth, stored_eval = self.transposition_table[fen]
            if stored_depth >= depth:
                return stored_eval

        # If no depth left or game ended, just evaluate
        if depth == 0 or board.is_game_over():
            eval = color * evaluate_board_with_simple_net(board, history)
            self.transposition_table[fen] = (depth, eval)
            return eval

        max_eval = float('-inf')
        first_move = True

        for move in self.order_moves(board):
            if move.promotion:
                # Try all promotions
                for promotion_piece in [chess.QUEEN, chess.KNIGHT, chess.ROOK, chess.BISHOP]:
                    move.promotion = promotion_piece
                    board.push(move)
                    history.append(fen)
                    eval = -self.idpvs(board, depth - 1, -beta, -alpha, -color, history)
                    history.pop()
                    board.pop()
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if alpha >= beta:
                        break
            else:
                board.push(move)
                history.append(fen)
                if first_move:
                    eval = -self.idpvs(board, depth - 1, -beta, -alpha, -color, history)
                    first_move = False
                else:
                    eval = -self.idpvs(board, depth - 1, -alpha - 1, -alpha, -color, history)
                    if alpha < eval < beta:
                        eval = -self.idpvs(board, depth - 1, -beta, -alpha, -color, history)
                history.pop()
                board.pop()

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break

        self.transposition_table[fen] = (depth, max_eval)
        return max_eval

    def idpvs_sequential(self, board, depth, history):
        """
        Runs IDPVS one depth at a time.
        """
        best_move = None
        color = 1 if board.turn == chess.WHITE else -1

        for current_depth in range(1, depth + 1):
            max_eval = float('-inf')
            alpha, beta = float('-inf'), float('inf')
            for move in self.order_moves(board):
                board.push(move)
                history.append(board.fen())
                eval = -self.idpvs(board, current_depth - 1, -beta, -alpha, -color, history)
                history.pop()
                board.pop()

                if eval > max_eval:
                    max_eval = eval
                    best_move = move

                alpha = max(alpha, eval)
                if alpha >= beta:
                    break

        return best_move

    def idpvs_parallel(self, board, depth, history):
        """
        Uses multiple workers to speed up the search.
        """
        color = 1 if board.turn == chess.WHITE else -1

        for current_depth in range(1, depth + 1):
            moves = list(self.order_moves(board))
            worker_args = [
                (board.copy(), move, current_depth, float('-inf'), float('inf'), color, history.copy())
                for move in moves
            ]

            with Pool(self.num_workers) as pool:
                results = pool.map(self.idpvs_parallel_worker, worker_args)

            best_move = max(results, key=lambda x: x[1])[0]

        return best_move

    def idpvs_parallel_worker(self, args):
        """
        Worker function for parallel search.
        """
        board, move, depth, alpha, beta, color, history = args
        board.push(move)
        history.append(board.fen())
        eval = -self.idpvs(board, depth - 1, -beta, -alpha, -color, history)
        history.pop()
        board.pop()
        return move, eval

    def order_moves(self, board):
        """
        Sort moves to try promising ones first.
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
