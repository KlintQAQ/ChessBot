# ChessBot

ChessBot is a Python-based chess application offering both Command-Line (CLI) and Graphical (GUI) interfaces. It allows you to play or observe matches in various modes, generate training datasets, train models, and configure AI algorithms.

## Features

- **Python 3.9 Compatible**: Developed and tested on Python 3.9.
- **CLI and GUI Modes**:  
  - **CLI**: Simple, text-based interaction for quick play or AI vs AI observation.
  - **GUI**: A visual interface powered by PyQt5, with draggable pieces, dialogs for AI configuration, and Tab-key navigation.
- **Game Modes**:
  - **Human vs AI**: Play as White against a configurable AI (drag and drop moves in GUI, or UCI commands in CLI).
  - **AI vs AI**: Set two AIs against each other and watch them battle.
- **AI Configuration**: Choose algorithms like Heuristic, NegamaxAlphaBeta, IDPVS, or MCTSPolicyGuided. Adjust parameters (depth, parallelization, simulations) easily.
- **Data Generation & Model Training**: Generate datasets (policy/value or simple value), then train neural networks to improve AI decisions.

## Requirements

- **Python Version**: Python 3.9 recommended.
- **Dependencies**: Listed in `requirements.txt`.

Install dependencies:
```bash
pip install -r requirements.txt
```

## Generating Datasets

ChessBot can create datasets for training neural networks:

1. **Policy/Value Dataset**:
   - Script: `generate_policy_value_dataset.py`
   - Requires a PGN file of games and a Stockfish engine path.
   - Adjust parameters in the script (like `NUM_POSITIONS`, `DEPTH`).
   - Run:
     ```bash
     python generate_policy_value_dataset.py
     ```
   - Produces `policy_value_dataset.npz` with:
     - `inputs`: Board features
     - `policy`: Move probability targets
     - `value`: Position values in [-1,1]

2. **Simple Dataset (Value-only)**:
   - Script: `generate_simple_dataset.py`
   - Produces a simpler dataset with only inputs and scalar evaluations.
   - Run:
     ```bash
     python generate_simple_dataset.py
     ```
   - Results in `simple_dataset.npz`.

Ensure you have set `STOCKFISH_PATH` and `PGN_FILE` inside the scripts before running.

## Training Models

After dataset generation:

- **Train Policy-Value Net**:
  - Script: `train_policy_value_net.py`
  - Needs `policy_value_dataset.npz`.
  - Run:
    ```bash
    python train_policy_value_net.py
    ```
  - Saves `policy_value_model.pt` to `model/`.

- **Train Simple Value Net**:
  - Script: `train_simple_chess_net.py`
  - Needs `simple_dataset.npz`.
  - Run:
    ```bash
    python train_simple_chess_net.py
    ```
  - Saves `simple_model.pt` to `model/`.

Tune epochs, batch size, learning rate in the scripts as desired.

## Running ChessBot

Once ready, or even without training, you can run:

```bash
python main.py
```

You’ll see a menu:
```
=== ChessBot Interface Selection ===
1. Command-Line Interface (CLI)
2. Graphical User Interface (GUI)
3. Exit
====================================
Enter your choice:
```

- **"1" for CLI**:
  - Pick Human vs AI or AI vs AI.
  - Human vs AI: Configure AI, then enter moves in UCI format (`e2e4`).
  - AI vs AI: Configure two AIs and watch the moves in text form.

- **"2" for GUI**:
  - A dialog asks for Human vs AI or AI vs AI.
  - Human vs AI:
    - Configure the AI in a dialog.
    - A chessboard window appears.
    - Drag pieces to move, AI responds automatically.
  - AI vs AI:
    - Configure both AIs.
    - Watch them play automatically.

- **"3" to Exit**.

## Keyboard Navigation in GUI

Dialogs support Tab navigation:
- Press **Tab** to move between buttons and input fields.
- Press **Enter** to select the focused element. This ensures the GUI is accessible even without a mouse.

## Troubleshooting

- **GUI not starting?** Ensure `PyQt5` is installed and display is available.
- **Missing dependencies?** Reinstall:
  ```bash
  pip install -r requirements.txt
  ```
- **Performance issues?** Lower AI depth or disable parallelization.
- **No Python 3.9?** It may work on other 3.x versions, but 3.9 is recommended.