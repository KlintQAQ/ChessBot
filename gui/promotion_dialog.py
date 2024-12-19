from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
import chess

class PromotionDialog(QDialog):
    """
    A simple dialog that appears when a pawn reaches the last rank.
    Lets the user pick which piece the pawn should promote to.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Promote Pawn")
        self.setModal(True)

        self.chosen_piece = None

        # Create a basic label asking for user choice
        label = QLabel("Choose a piece to promote the pawn to:")
        label.setAlignment(Qt.AlignCenter)

        # Buttons for each piece: Queen, Rook, Bishop, Knight
        # We'll store their corresponding chess piece type constants
        queen_btn = QPushButton("Queen")
        queen_btn.clicked.connect(lambda: self._select_piece(chess.QUEEN))

        rook_btn = QPushButton("Rook")
        rook_btn.clicked.connect(lambda: self._select_piece(chess.ROOK))

        bishop_btn = QPushButton("Bishop")
        bishop_btn.clicked.connect(lambda: self._select_piece(chess.BISHOP))

        knight_btn = QPushButton("Knight")
        knight_btn.clicked.connect(lambda: self._select_piece(chess.KNIGHT))

        # Arrange buttons in a row
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(queen_btn)
        btn_layout.addWidget(rook_btn)
        btn_layout.addWidget(bishop_btn)
        btn_layout.addWidget(knight_btn)

        # Put everything in a vertical layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _select_piece(self, piece_type):
        """
        When the user picks a piece, store the choice and close the dialog.
        """
        self.chosen_piece = piece_type
        self.accept()

    def get_promotion_choice(self):
        """
        Show the dialog and return the chosen piece type.
        If the user closes without choosing, it returns None.
        """
        result = self.exec_()
        if result == QDialog.Accepted:
            return self.chosen_piece
        return None
