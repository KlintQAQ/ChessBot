import chess
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF

class ChessPiece(QGraphicsPixmapItem):
    """
    A draggable chess piece on the board.
    This piece doesn't handle game logic itself, just the visual movement.
    The actual move legality is checked in the board code once the piece is dropped.
    """

    def __init__(self, pixmap, position, board):
        super().__init__(pixmap)

        self.board = board
        self.position = position  # (row, col)
        self.square_size = self.board.square_size

        # Scale the piece image to fit nicely in the square
        scaled_pixmap = pixmap.scaled(
            self.square_size, self.square_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

        # Allow the piece to be moved with the mouse
        self.setFlags(QGraphicsPixmapItem.ItemIsMovable | QGraphicsPixmapItem.ItemSendsScenePositionChanges)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setZValue(1)  # Draw pieces above the board squares

        self.current_highlighted_square = None

        # Move piece to initial correct position
        self.update_position()

    def update_position(self):
        """Visually place the piece at its (row, col) location."""
        x = self.position[1] * self.square_size
        y = self.position[0] * self.square_size
        self.setPos(x, y)

    def _get_square_from_position(self, position):
        """
        Given a graphical position (x,y), figure out which board square (row,col) is closest.
        This helps us know where the piece ended up after dragging.
        """
        x, y = position.x(), position.y()
        col = int(round(x / self.square_size))
        row = int(round(y / self.square_size))
        return row, col

    def mousePressEvent(self, event):
        """
        When the user clicks on the piece:
        - Check if human can move
        - Bring piece to front visually
        - Highlight the starting square
        """
        if not self.board.human_can_move or not self.board.is_human_turn:
            return
        self.setZValue(2)  # Bring the selected piece forward
        self.board.highlight_square(*self.position)
        self.current_highlighted_square = self.position
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        When the user drags the piece:
        - Update the piece's on-screen position as it moves
        - Highlight the square currently beneath it
        """
        if not self.board.human_can_move or not self.board.is_human_turn:
            return

        new_pos = event.scenePos() - QPointF(self.square_size / 2, self.square_size / 2)
        self.setPos(new_pos)

        row, col = self._get_square_from_position(new_pos)
        if (row, col) in self.board.squares:
            # If we moved to a new square, update highlights
            if self.current_highlighted_square != (row, col):
                if self.current_highlighted_square:
                    self.board.unhighlight_square(*self.current_highlighted_square)
                self.board.highlight_square(row, col)
                self.current_highlighted_square = (row, col)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        When the user releases the piece:
        - Determine which square the piece was dropped on
        - Ask the board to validate and handle the move
        - If invalid, revert to original position
        """
        if not self.board.human_can_move or not self.board.is_human_turn:
            return

        row, col = self._get_square_from_position(self.scenePos())

        # Remove highlight if any
        if self.current_highlighted_square:
            self.board.unhighlight_square(*self.current_highlighted_square)
            self.current_highlighted_square = None

        if 0 <= row <= 7 and 0 <= col <= 7:
            src_row, src_col = self.position
            move = (src_row, src_col, row, col)

            # Check if move is legal via board methods
            if self.board.is_human_turn and self.board.is_valid_move(move):
                self.board.handle_move(self, (src_row, src_col), (row, col))
            else:
                print(f"Invalid move attempted: {move}")
                self.update_position()  # Return to original spot
        else:
            print("Move out of bounds")
            self.update_position()

        self.setZValue(1)  # Reset piece stacking order
        super().mouseReleaseEvent(event)
