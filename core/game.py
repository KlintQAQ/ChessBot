import chess
from core.player import AIPlayer

class Game:
    """
    Manages a single chess game:
    - Tracks board state
    - Handles moves from players (human or AI)
    - Keeps a history of positions
    - Determines when the game ends and why
    """

    def __init__(self, player1, player2):
        # player1 is White, player2 is Black by convention
        self.board = chess.Board()
        self.players = {chess.WHITE: player1, chess.BLACK: player2}
        self.move_history = []  # Store fen strings after each move
        self.current_turn = chess.WHITE  # White moves first

    def make_move(self, move):
        """
        Try to apply 'move' to the board.
        If legal, update board and history, switch turn, and return True.
        If not, return False.
        """
        if move in self.board.legal_moves:
            self.board.push(move)
            self.move_history.append(move)
            self.current_turn = not self.current_turn
            return True
        return False

    def get_ai_move(self):
        """
        If it's an AI's turn, ask it for the next move.
        If it's not an AI, raise an error.
        """
        current_player = self.players[self.board.turn]
        if not isinstance(current_player, AIPlayer):
            raise ValueError("Current player is not an AI!")
        return current_player.get_move(self.board, self.move_history)

    def is_game_over(self):
        """
        Check if the board state indicates game over.
        """
        return self.board.is_game_over()

    def get_result(self):
        """
        Explain how the game ended and who won (if anyone).
        Also show final details like the last move if available.
        """
        if self.board.is_checkmate():
            winner = "White" if not self.board.turn else "Black"
            result_message = f"Checkmate! {winner} wins."
        elif self.board.is_stalemate():
            result_message = "Draw! Stalemate."
        elif self.board.is_insufficient_material():
            result_message = "Draw! Insufficient material."
        elif self.board.is_seventyfive_moves():
            result_message = "Draw! 75-move rule."
        elif self.board.is_fivefold_repetition():
            result_message = "Draw! Fivefold repetition."
        elif self.board.is_variant_draw():
            result_message = "Draw! Variant rule."
        else:
            result_message = "Draw: Unknown reason!"

        # If there were moves played, show the last one
        if self.move_history:
            last_move = self.move_history[-1]
            result_message += f"\nLast move made was: {last_move.uci()}"

        return result_message