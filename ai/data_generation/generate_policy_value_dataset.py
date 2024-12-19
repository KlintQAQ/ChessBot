import sys
import signal
import chess
import chess.pgn
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from ai.neural_network.utils import board_to_feature_vector, move_to_index

STOCKFISH_PATH = "./engines/stockfish"
PGN_FILE = "rawdata/lichess_db_standard_rated_2013-01.pgn"
OUTPUT_FILE = "dataset/policy_value_dataset.npz"
NUM_POSITIONS = 100000
DEPTH = 10
MULTIPV = 3
POLICY_SIZE = 64 * 90
NUM_CORES = multiprocessing.cpu_count()
MAX_WORKERS = max(1, int(NUM_CORES))

def evaluate_position(fen):
    """
    Runs Stockfish on one position to get feature_vector, policy_vector, and value
    """
    import chess.engine
    board = chess.Board(fen)
    if not board.is_valid():
        return None, None, None

    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            info = engine.analyse(board, chess.engine.Limit(depth=DEPTH), multipv=MULTIPV)
            if not info:
                return None, None, None

            policy_vector = np.zeros(POLICY_SIZE, dtype=np.float32)
            for entry in info:
                if "pv" not in entry or not entry["pv"]:
                    continue
                move = entry["pv"][0]
                pov_score = entry["score"].pov(chess.WHITE)
                mate_score = pov_score.mate()
                if mate_score is not None:
                    if mate_score > 0:
                        move_score = 1000.0
                    else:
                        move_score = -1000.0
                elif pov_score.cp is not None:
                    move_score = float(pov_score.cp)
                else:
                    move_score = 0.0

                if move_score > 0:
                    try:
                        move_index = move_to_index(move, board)
                        policy_vector[move_index] += move_score
                    except ValueError:
                        continue

            total = policy_vector.sum()
            if total > 0:
                policy_vector /= total

            top_score = info[0].get("score")
            if top_score is None:
                return None, None, None

            top_pov = top_score.pov(chess.WHITE)
            top_mate = top_pov.mate()
            if top_mate is not None:
                value = 1.0 if top_mate > 0 else -1.0
            elif top_pov.cp is not None:
                value = max(min(top_pov.cp / 1000.0, 1.0), -1.0)
            else:
                value = 0.0

            feature_vector = board_to_feature_vector(board)
            return feature_vector, policy_vector, value
    except:
        return None, None, None

def signal_handler(sig, frame):
    print("Interrupted by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    inputs = []
    policies = []
    values = []
    positions_extracted = 0

    # First, extract fen strings from games
    fen_positions = []
    with open(PGN_FILE, "r", encoding="utf-8") as pgn:
        while positions_extracted < NUM_POSITIONS:
            print(positions_extracted)
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                fen_positions.append(board.fen())
                positions_extracted += 1
                if positions_extracted >= NUM_POSITIONS:
                    break

    print(f"Collected {len(fen_positions)} positions.")

    # Now parallelize the evaluation of fen positions
    positions_extracted = 0
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        print(MAX_WORKERS)
        futures = [executor.submit(evaluate_position, fen) for fen in fen_positions]
        for future in as_completed(futures):
            fv, pv, val = future.result()
            if fv is not None:
                inputs.append(fv)
                policies.append(pv)
                values.append(val)
                positions_extracted += 1
                if positions_extracted % 100 == 0:
                    print(f"Processed {positions_extracted} positions.")
    print("SAVE")
    np.savez(
        OUTPUT_FILE,
        inputs=np.array(inputs, dtype=np.float32),
        policy=np.array(policies, dtype=np.float32),
        value=np.array(values, dtype=np.float32)
    )
    print(f"Saved {len(inputs)} positions to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
