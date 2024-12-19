
import numpy as np
import chess

def board_to_feature_vector(board: chess.Board) -> np.ndarray:
    """
    Convert board to a numeric vector.
    Includes pieces, side to move, castling rights, and move counters.
    """
    piece_map = {
        chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 2,
        chess.ROOK: 3, chess.QUEEN: 4, chess.KING: 5
    }

    # One-hot encode each square for all piece types + empty
    # 64 squares, 13 channels (12 pieces + 1 empty)
    vector = np.zeros((64, 13), dtype=np.float32)
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is not None:
            base_idx = piece_map[piece.piece_type]
            if piece.color == chess.BLACK:
                base_idx += 6
            vector[sq, base_idx] = 1.0
        else:
            vector[sq, 12] = 1.0

    feature_vector = vector.flatten()

    # Add side to move (+1 for White, -1 for Black)
    side_to_move = 1.0 if board.turn == chess.WHITE else -1.0
    feature_vector = np.concatenate((feature_vector, [side_to_move]))

    # Add castling rights for both sides
    castling_vec = [
        1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0,
        1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0,
        1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0,
        1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0
    ]
    feature_vector = np.concatenate((feature_vector, castling_vec))

    # Add halfmove clock and fullmove number
    feature_vector = np.concatenate((feature_vector, [board.halfmove_clock, board.fullmove_number]))

    return feature_vector

import chess

def move_to_index(move: chess.Move, board: chess.Board) -> int:
    """
    Convert a chess move into an index following a custom AlphaZero-like scheme.
    Assumes a predefined 90-move scheme per square:
    - 0-55: Sliding moves (8 directions x 7 steps)
    - 56-63: Knight moves (8)
    - 64-71: King normal moves (8 directions x 1 step)
    - 72: King castling kingside (2 steps to the right)
    - 73: King castling queenside (2 steps to the left)
    - 74: Pawn single push
    - 75: Pawn double push
    - 76: Pawn capture left
    - 77: Pawn capture right
    - 78-81: Single push promotions (Q,R,B,N)
    - 82-85: Capture left promotions (Q,R,B,N)
    - 86-89: Capture right promotions (Q,R,B,N)
    """
    from_sq = move.from_square
    to_sq = move.to_square
    piece = board.piece_at(from_sq)
    if piece is None:
        raise ValueError("No piece at from_square.")

    color = piece.color
    piece_type = piece.piece_type

    from_rank = from_sq // 8
    from_file = from_sq % 8
    to_rank = to_sq // 8
    to_file = to_sq % 8

    rank_diff = to_rank - from_rank
    file_diff = to_file - from_file

    direction_vectors = [
        (-1, 0), (-1, 1), (0, 1), (1, 1),
        (1, 0), (1, -1), (0, -1), (-1, -1)
    ]
    knight_moves = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        (1, -2), (1, 2), (2, -1), (2, 1)
    ]
    king_moves = direction_vectors

    move_subindex = None

    # Sliding moves (Q,R,B)
    if piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP]:
        if piece_type == chess.ROOK:
            valid_dirs = [0,2,4,6] # N,E,S,W
        elif piece_type == chess.BISHOP:
            valid_dirs = [1,3,5,7] # NE,SE,SW,NW
        else:
            valid_dirs = range(8) # Queen in all directions
        for d_idx, (dr, df) in enumerate(direction_vectors):
            if d_idx in valid_dirs:
                step = 1
                r, f = from_rank + dr, from_file + df
                while 0 <= r < 8 and 0 <= f < 8 and step <= 7:
                    if r == to_rank and f == to_file:
                        move_subindex = d_idx * 7 + (step - 1)
                        break
                    r += dr
                    f += df
                    step += 1
                if move_subindex is not None:
                    break

    # Knight moves
    if move_subindex is None and piece_type == chess.KNIGHT:
        for k_idx, (kr, kf) in enumerate(knight_moves):
            if rank_diff == kr and file_diff == kf:
                move_subindex = 56 + k_idx
                break

    # King normal moves
    if move_subindex is None and piece_type == chess.KING:
        for km_idx, (kr, kf) in enumerate(king_moves):
            if rank_diff == kr and file_diff == kf:
                move_subindex = 64 + km_idx
                break

    # King castling moves
    # White kingside: e1->g1 rank_diff=0 file_diff=2
    # White queenside: e1->c1 rank_diff=0 file_diff=-2
    # Black kingside: e8->g8 rank_diff=0 file_diff=2
    # Black queenside: e8->c8 rank_diff=0 file_diff=-2
    if move_subindex is None and piece_type == chess.KING:
        if rank_diff == 0 and file_diff == 2:
            # Kingside castle
            move_subindex = 72
        elif rank_diff == 0 and file_diff == -2:
            # Queenside castle
            move_subindex = 73

    # Pawn moves
    if move_subindex is None and piece_type == chess.PAWN:
        pawn_base = 74
        if color == chess.WHITE:
            direction = +1
            start_rank = 1
            last_rank = 7
        else:
            direction = -1
            start_rank = 6
            last_rank = 0

        # Single push
        if file_diff == 0 and rank_diff == direction:
            move_subindex = pawn_base
        # Double push
        elif file_diff == 0 and from_rank == start_rank and rank_diff == 2*direction:
            move_subindex = pawn_base + 1
        # Capture left/right
        elif rank_diff == direction and abs(file_diff) == 1:
            if file_diff == -1:
                move_subindex = pawn_base + 2
            else:
                move_subindex = pawn_base + 3

        # Promotions
        if move_subindex is not None and to_rank == last_rank:
            promo_map = {chess.QUEEN:0, chess.ROOK:1, chess.BISHOP:2, chess.KNIGHT:3}
            if move.promotion is not None:
                promo_idx = promo_map[move.promotion]
                # single push promotion: pawn_base+4..+7 (78..81)
                # capture left promotion: pawn_base+8..+11 (82..85)
                # capture right promotion: pawn_base+12..+15 (86..89)
                if move_subindex == pawn_base:        # single push
                    move_subindex = pawn_base + 4 + promo_idx
                elif move_subindex == pawn_base + 2:  # capture left
                    move_subindex = pawn_base + 8 + promo_idx
                elif move_subindex == pawn_base + 3:  # capture right
                    move_subindex = pawn_base + 12 + promo_idx

    if move_subindex is None:
        raise ValueError(f"Move {move.uci()} cannot be indexed by this scheme.")

    final_index = from_sq * 90 + move_subindex
    return final_index