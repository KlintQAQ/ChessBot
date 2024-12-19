import chess
import chess.engine
import chess.pgn
import numpy as np
from ai.neural_network.utils import board_to_feature_vector

STOCKFISH_PATH = "./engines/stockfish"
PGN_FILE = "rawdata/lichess_db_standard_rated_2013-01.pgn"
OUTPUT_FILE = "dataset/simple_dataset.npz"
NUM_POSITIONS = 100000
DEPTH = 15  # Stockfish evaluation depth

def main():
    # Start the Stockfish engine
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    inputs = []
    labels = []
    positions_extracted = 0

    with open(PGN_FILE, "r", encoding="utf-8") as pgn:
        while positions_extracted < NUM_POSITIONS:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            board = game.board()

            for move in game.mainline_moves():
                if positions_extracted >= NUM_POSITIONS:
                    break

                board.push(move)

                # Evaluate position with Stockfish
                try:
                    info = engine.analyse(board, chess.engine.Limit(depth=DEPTH))
                except Exception as e:
                    print(f"Stockfish evaluation error: {e}")
                    break

                score = info["score"].pov(chess.WHITE)
                if score.is_mate():
                    evaluation = 1.0 if score.mate() > 0 else -1.0
                else:
                    evaluation = max(min(score.score() / 1000.0, 1.0), -1.0)

                fv = board_to_feature_vector(board)
                inputs.append(fv)
                labels.append(evaluation)
                positions_extracted += 1

                if positions_extracted % 1000 == 0:
                    print(f"Processed {positions_extracted} positions.")

    engine.quit()
    np.savez(OUTPUT_FILE, inputs=np.array(inputs, dtype=np.float32), labels=np.array(labels, dtype=np.float32))
    print(f"Saved {len(inputs)} positions to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
