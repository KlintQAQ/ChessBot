import chess
from .common import PIECE_VALUES, PIECE_SQUARE_TABLES, is_endgame

def heuristic_evaluation(board, move_history=None):
    # Basic heuristic using material and positional tables
    score = 0
    endgame = is_endgame(board)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_value = PIECE_VALUES[piece.piece_type]
            if piece.piece_type == chess.KING and endgame:
                pst_value = PIECE_SQUARE_TABLES['endgame_king'][square if piece.color == chess.WHITE else chess.square_mirror(square)]
            else:
                pst_value = PIECE_SQUARE_TABLES[piece.piece_type][square if piece.color == chess.WHITE else chess.square_mirror(square)]
            total_piece_value = piece_value + pst_value
            score += total_piece_value if piece.color == chess.WHITE else -total_piece_value

    return score
