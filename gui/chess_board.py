import os
import chess
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QBrush, QPen, QColor, QPixmap
from PyQt5.QtCore import Qt
from gui.chess_piece import ChessPiece
from gui.promotion_dialog import PromotionDialog


class ChessBoard(QGraphicsScene):
    """
    Handles the visual representation of the chessboard and its pieces.
    Interacts with a provided Game object for state, but focuses on drawing and user input.
    """

    def __init__(self, game, human_can_move=False):
        super().__init__()
        self.setSceneRect(0, 0, 800, 800)
        self.square_size = 100
        self.squares = {}
        self.pieces = {}
        self.game = game
        self.human_can_move = human_can_move
        self.is_human_turn = True
        self.game_over_callback = None
        self.human_move_callback = None
        self._init_board()
        self._init_pieces()

    def set_game_over_callback(self, callback):
        """
        Assign a function to be called when the game ends.
        """
        self.game_over_callback = callback

    def set_human_move_callback(self, callback):
        """
        Assign a function to handle human moves once they're made on the board.
        """
        self.human_move_callback = callback

    def _init_board(self):
        """
        Draw the chessboard squares.
        """
        colors = [QColor('#F0D9B5'), QColor('#B58863')]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                square = QGraphicsRectItem(
                    col * self.square_size,
                    row * self.square_size,
                    self.square_size,
                    self.square_size
                )
                square.setBrush(QBrush(color))
                square.setPen(QPen(Qt.NoPen))
                self.addItem(square)
                self.squares[(row, col)] = square

    def _init_pieces(self):
        """
        Place pieces onto the board based on the current Game's FEN.
        """
        base_path = os.path.join("assets", "pieces")

        piece_symbols = {
            'r': os.path.join(base_path, 'rook-b.svg'),
            'n': os.path.join(base_path, 'knight-b.svg'),
            'b': os.path.join(base_path, 'bishop-b.svg'),
            'q': os.path.join(base_path, 'queen-b.svg'),
            'k': os.path.join(base_path, 'king-b.svg'),
            'p': os.path.join(base_path, 'pawn-b.svg'),
            'R': os.path.join(base_path, 'rook-w.svg'),
            'N': os.path.join(base_path, 'knight-w.svg'),
            'B': os.path.join(base_path, 'bishop-w.svg'),
            'Q': os.path.join(base_path, 'queen-w.svg'),
            'K': os.path.join(base_path, 'king-w.svg'),
            'P': os.path.join(base_path, 'pawn-w.svg'),
        }

        self._clear_board()

        fen_parts = self.game.board.fen().split()
        board_fen = fen_parts[0]
        rows = board_fen.split('/')

        for row_index, row_data in enumerate(rows):
            actual_row = row_index
            col = 0
            for char in row_data:
                if char.isdigit():
                    col += int(char)
                elif char in piece_symbols:
                    pixmap_path = piece_symbols[char]
                    pixmap = QPixmap(pixmap_path)
                    piece = ChessPiece(pixmap, (actual_row, col), self)
                    self.addItem(piece)
                    self.pieces[(actual_row, col)] = piece
                    col += 1

    def _clear_board(self):
        """
        Remove all pieces currently shown.
        """
        for piece in list(self.pieces.values()):
            self.removeItem(piece)
        self.pieces.clear()

    def coords_to_square(self, row, col):
        """
        Convert (row, col) in the board's coordinate system to a chess square index.
        row and col start at 0 from the top-left of the board.
        """
        square = chess.square(col, 7 - row)
        print(f"Mapping (row={row}, col={col}) -> square={chess.square_name(square)}")
        return square

    def square_to_coords(self, square):
        """
        Convert a chess square index into (row, col) coordinates for GUI placement.
        """
        return 7 - chess.square_rank(square), chess.square_file(square)

    def is_valid_move(self, move):
        """
        Check if a tentative move (src_row, src_col, dest_row, dest_col) is legal.
        Also consider special cases like promotions.
        """
        src_row, src_col, dest_row, dest_col = move
        move_obj = chess.Move(
            self.coords_to_square(src_row, src_col),
            self.coords_to_square(dest_row, dest_col)
        )

        print(f"Checking move: {move_obj}")

        moving_piece = self.game.board.piece_at(self.coords_to_square(src_row, src_col))
        print(f'Moving piece: {moving_piece}, Pawn? {moving_piece.piece_type == chess.PAWN if moving_piece else "N/A"}')
        if moving_piece and moving_piece.piece_type == chess.PAWN:
            promotion_rank = 0 if moving_piece.color == chess.WHITE else 7
            if dest_row == promotion_rank:
                # Try all promotion pieces to see if any are legal
                for promo in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                    move_obj.promotion = promo
                    if move_obj in self.game.board.legal_moves:
                        print(f"Valid promotion move: {move_obj}")
                        return True
                print("Invalid promotion move")
                return False

        is_legal = move_obj in self.game.board.legal_moves
        print(f"Is move {move_obj} legal? {is_legal}")
        return is_legal

    def handle_move(self, piece, old_position, new_position):
        """
        Called when a human player tries to move a piece from old_position to new_position.
        Checks promotions and castling, then applies the move through the Game.
        If invalid, reverts the piece's position.
        """
        src_square = self.coords_to_square(*old_position)
        dest_square = self.coords_to_square(*new_position)
        move = chess.Move(src_square, dest_square)

        moving_piece = self.game.board.piece_at(src_square)
        print(f"Handling move: {move}")

        # Check for pawn promotion
        if moving_piece and moving_piece.piece_type == chess.PAWN:
            promotion_rank = 0 if moving_piece.color == chess.WHITE else 7
            dest_row, dest_col = new_position
            if dest_row == promotion_rank:
                # Ask user to choose promotion piece
                promotion_dialog = PromotionDialog()
                promotion_piece = promotion_dialog.get_promotion_choice()

                if promotion_piece:
                    move.promotion = promotion_piece
                    self._update_piece_image(piece, promotion_piece, moving_piece.color)
                else:
                    print("Promotion canceled or invalid choice.")
                    piece.update_position()
                    return

        is_castling = self.game.board.is_castling(move)
        if self.game.make_move(move):
            self._update_piece_position(piece, old_position, new_position)

            if is_castling:
                self._handle_castling(move)

            if self.game.is_game_over() and self.game_over_callback:
                self.game_over_callback(self.game.get_result())
            else:
                if self.human_move_callback:
                    self.human_move_callback(move)
        else:
            print("Move invalid!")
            piece.update_position()

    def make_ai_move(self, move, is_castling, moving_color):
        """
        Called externally once an AI move is decided.
        Applies the move visually and checks if the game ends.
        """
        src_row, src_col = self.square_to_coords(move.from_square)
        dest_row, dest_col = self.square_to_coords(move.to_square)

        if (src_row, src_col) in self.pieces:
            piece = self.pieces.pop((src_row, src_col))

            if move.promotion:
                self._update_piece_image(piece, move.promotion, moving_color)

            self._update_piece_position(piece, (src_row, src_col), (dest_row, dest_col))

            if is_castling:
                self._handle_castling(move)

            if self.game.is_game_over():
                print("Game Over!")
                self._handle_game_over()

            self.is_human_turn = True
        else:
            print(f"No piece found at ({src_row}, {src_col}).")

    def _handle_castling(self, move):
        """
        Handle rook movement for castling.
        """
        if move.to_square == chess.G1:  # White kingside
            rook_start, rook_end = chess.H1, chess.F1
        elif move.to_square == chess.C1:  # White queenside
            rook_start, rook_end = chess.A1, chess.D1
        elif move.to_square == chess.G8:  # Black kingside
            rook_start, rook_end = chess.H8, chess.F8
        elif move.to_square == chess.C8:  # Black queenside
            rook_start, rook_end = chess.A8, chess.D8
        else:
            return

        rook_start_coords = self.square_to_coords(rook_start)
        rook_end_coords = self.square_to_coords(rook_end)

        rook_piece = self.pieces.pop(rook_start_coords, None)
        if rook_piece:
            rook_piece.position = rook_end_coords
            rook_piece.update_position()
            self.pieces[rook_end_coords] = rook_piece

    def _update_piece_position(self, piece, old_position, new_position):
        """
        Move a piece from old_position to new_position, capturing if needed.
        """
        src_row, src_col = old_position
        dest_row, dest_col = new_position

        if new_position in self.pieces:
            captured = self.pieces.pop(new_position)
            self.removeItem(captured)

        piece.position = new_position
        piece.update_position()
        self.pieces[new_position] = piece
        if old_position in self.pieces:
            del self.pieces[old_position]

    def _update_piece_image(self, piece, promotion_piece, color):
        """
        Change the piece image after promotion.
        """
        base_path = os.path.join("assets", "pieces")
        piece_symbols = {
            chess.QUEEN: os.path.join(base_path, 'queen-w.svg') if color == chess.WHITE else os.path.join(base_path, 'queen-b.svg'),
            chess.ROOK: os.path.join(base_path, 'rook-w.svg') if color == chess.WHITE else os.path.join(base_path, 'rook-b.svg'),
            chess.BISHOP: os.path.join(base_path, 'bishop-w.svg') if color == chess.WHITE else os.path.join(base_path, 'bishop-b.svg'),
            chess.KNIGHT: os.path.join(base_path, 'knight-w.svg') if color == chess.WHITE else os.path.join(base_path, 'knight-b.svg'),
        }

        pixmap_path = piece_symbols[promotion_piece]
        pixmap = QPixmap(pixmap_path)
        piece.setPixmap(pixmap.scaled(
            self.square_size, self.square_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        print(f"Promoted piece at {piece.position} to {promotion_piece}")

    def _handle_game_over(self):
        """
        If there's a callback for game over, call it now.
        """
        if self.game_over_callback:
            self.game_over_callback(self.game.get_result())

    def highlight_square(self, row, col):
        """
        Highlight the given square.
        """
        square = self.squares.get((row, col))
        if square:
            square.setBrush(QBrush(QColor("#FFFFA0")))
            square.setPen(QPen(QColor("#FFD700"), 2))

    def unhighlight_square(self, row, col):
        """
        Remove highlighting from the given square.
        """
        square = self.squares.get((row, col))
        if square:
            color = QColor('#F0D9B5') if (row + col) % 2 == 0 else QColor('#B58863')
            square.setBrush(QBrush(color))
            square.setPen(QPen(Qt.NoPen))
