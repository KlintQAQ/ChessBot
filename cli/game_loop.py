import chess
from core.game import Game
from core.player import HumanPlayer, AIPlayer
from cli.algorithm_selector import select_algorithm

def play_human_vs_ai():
    """
    Human vs AI:
    - Human (White) enters moves in UCI format (e.g., e2e4).
    - AI (Black) is chosen by user.
    - Type 'quit' at any point on your turn to end the game.
    """
    print("You are playing as White. The AI will play as Black.")
    ai_algorithm = select_algorithm()
    human_player = HumanPlayer()
    ai_player = AIPlayer(ai_algorithm)
    game = Game(human_player, ai_player)

    while not game.is_game_over():
        print("\nCurrent board:")
        print(game.board)

        if game.board.turn:  # White's turn (Human)
            move_input = input("Enter your move (or 'quit' to exit): ").strip()
            if move_input.lower() == "quit":
                print("You chose to quit the game.")
                break

            try:
                move = chess.Move.from_uci(move_input)
                if not game.make_move(move):
                    print("Invalid move. Please try again.")
            except Exception:
                print("Invalid input format. Please try again.")
        else:  # Black's turn (AI)
            move = game.get_ai_move()
            print(f"AI moves: {move.uci()}")
            game.make_move(move)

    if game.is_game_over():
        print("\nGame Over!")
        print(game.get_result())
    else:
        print("\nGame ended prematurely.")

def play_ai_vs_ai():
    """
    AI vs AI:
    - User selects AI for White (Player 1) and for Black (Player 2).
    - The game runs until it is over.
    """
    print("Select AI for Player 1 (White):")
    ai1 = AIPlayer(select_algorithm())

    print("Select AI for Player 2 (Black):")
    ai2 = AIPlayer(select_algorithm())

    game = Game(ai1, ai2)

    print("White AI:", ai1.ai_algorithm.__class__.__name__)
    print("Black AI:", ai2.ai_algorithm.__class__.__name__)

    while not game.is_game_over():
        print("\nCurrent board:")
        print(game.board)

        move = game.get_ai_move()
        current_player = "White" if game.board.turn else "Black"
        print(f"{current_player} AI moves: {move.uci()}")
        game.make_move(move)

    # When the game ends, show who won and the last move made
    print("\nGame Over!")
    print(game.get_result())
