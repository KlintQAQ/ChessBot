import sys
import chess
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QMessageBox, QDialog, 
                             QVBoxLayout, QLabel, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from gui.chess_board import ChessBoard
from core.game import Game
from core.player import HumanPlayer, AIPlayer
from gui.ai_dialog import AIDialog
from gui.ai_ai_dialog import AIAIDialog

def main():
    app = QApplication(sys.argv)

    mode_dialog = ModeSelectionDialog()
    result = mode_dialog.exec_()

    if result == mode_dialog.HUMAN_VS_AI:
        dialog = AIDialog()
        if dialog.exec_() == AIDialog.Accepted:
            ai_algorithm = dialog.selected_algorithm
            if not ai_algorithm:
                QMessageBox.warning(None, "Error", "No valid AI configuration chosen. Exiting.")
                sys.exit(0)
            human = HumanPlayer()
            ai = AIPlayer(ai_algorithm)
            game = Game(human, ai)

            board = ChessBoard(game, human_can_move=True)
            board.set_human_move_callback(lambda move: process_human_move(move, game, board))
            board.set_game_over_callback(lambda result: show_game_over(result))

            view = QGraphicsView(board)
            view.setWindowTitle("ChessBot - Human vs AI")
            view.setFixedSize(820, 820)
            view.show()

            sys.exit(app.exec_())

    elif result == mode_dialog.AI_VS_AI:
        dialog = AIAIDialog()
        if dialog.exec_() == AIAIDialog.Accepted:
            ai1_algorithm, ai2_algorithm = dialog.selected_algorithm_ai1, dialog.selected_algorithm_ai2
            if not ai1_algorithm or not ai2_algorithm:
                QMessageBox.warning(None, "Error", "Both AI configurations must be completed. Exiting.")
                sys.exit(0)
            ai1 = AIPlayer(ai1_algorithm)
            ai2 = AIPlayer(ai2_algorithm)
            game = Game(ai1, ai2)

            board = ChessBoard(game, human_can_move=False)
            board.set_game_over_callback(lambda result: show_game_over(result))

            view = QGraphicsView(board)
            view.setWindowTitle("ChessBot - AI vs AI")
            view.setFixedSize(820, 820)
            view.show()

            start_ai_vs_ai(game, board)

            sys.exit(app.exec_())
    else:
        print("No option selected. Exiting.")
        sys.exit(0)

def process_human_move(move, game, board):
    if game.is_game_over():
        show_game_over(game.get_result())
    else:
        QTimer.singleShot(100, lambda: ai_move(game, board))

def ai_move(game, board):
    moving_color = game.board.turn
    move = game.get_ai_move()
    is_castling = game.board.is_castling(move)
    if game.make_move(move):
        board.make_ai_move(move, is_castling, moving_color)
        if game.is_game_over():
            show_game_over(game.get_result())

def start_ai_vs_ai(game, board):
    def process_ai_move():
        moving_color = game.board.turn
        move = game.get_ai_move()
        is_castling = game.board.is_castling(move)
        if game.make_move(move):
            board.make_ai_move(move, is_castling, moving_color)
            if game.is_game_over():
                timer.stop()
                show_game_over(game.get_result())

    timer = QTimer()
    timer.timeout.connect(process_ai_move)
    timer.start(1000)

def show_game_over(result):
    QMessageBox.information(None, "Game Over", result)

class ModeSelectionDialog(QDialog):
    """
    Dialog to select between Human vs AI or AI vs AI mode.
    Now with tab navigation and initial focus set on the first button.
    """
    HUMAN_VS_AI = 1
    AI_VS_AI = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ChessBot Game Mode")
        self.setModal(True)
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        label = QLabel("<b>Welcome to ChessBot!</b><br>Use Tab to switch between buttons, then press Enter to select a mode.")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        # Buttons for mode selection
        btn_layout = QHBoxLayout()
        self.hvai_btn = QPushButton("Human vs AI")
        self.hvai_btn.setFocusPolicy(Qt.StrongFocus)  # Ensure tab focus
        self.hvai_btn.setToolTip("Play as White against an AI opponent.")
        self.hvai_btn.clicked.connect(lambda: self._select_mode(self.HUMAN_VS_AI))

        self.aivai_btn = QPushButton("AI vs AI")
        self.aivai_btn.setFocusPolicy(Qt.StrongFocus) # Ensure tab focus
        self.aivai_btn.setToolTip("Watch two AIs play against each other.")
        self.aivai_btn.clicked.connect(lambda: self._select_mode(self.AI_VS_AI))

        btn_layout.addWidget(self.hvai_btn)
        btn_layout.addWidget(self.aivai_btn)
        layout.addLayout(btn_layout)

        # Set tab order so pressing tab goes between hvai_btn and aivai_btn
        self.setTabOrder(self.hvai_btn, self.aivai_btn)

        # Set initial focus on hvai_btn so user can start tabbing right away
        self.hvai_btn.setFocus()

    def _select_mode(self, mode):
        self.done(mode)

if __name__ == "__main__":
    main()
