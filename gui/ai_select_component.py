from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QFormLayout, QGroupBox, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from ai.algorithms.heuristic import Heuristic
from ai.algorithms.negamax_alpha_beta import NegamaxAlphaBeta
from ai.algorithms.idpvs import IDPVS
from ai.algorithms.mcts_policy_guided import MCTSPolicyGuided

class AISelectComponent(QWidget):
    """
    A component that lets the user choose and configure an AI algorithm.
    Adds tooltips, placeholders, and ensures safe fallback defaults.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_algorithm = None

        main_layout = QVBoxLayout(self)

        # Instruction label
        self.algorithm_label = QLabel("Select AI Algorithm:")
        main_layout.addWidget(self.algorithm_label)

        # Algorithm dropdown
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Heuristic", "NegamaxAlphaBeta", "IDPVS", "MCTSPolicyGuided"])
        self.algorithm_combo.currentIndexChanged.connect(self.update_form)
        main_layout.addWidget(self.algorithm_combo)

        # Group box for settings
        self.settings_group = QGroupBox("Algorithm Settings")
        self.settings_group.setToolTip("Configure settings for the chosen AI.")
        self.form_layout = QFormLayout()
        self.settings_group.setLayout(self.form_layout)
        main_layout.addWidget(self.settings_group)

        # Spacer for layout spacing
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.update_form()  # Initialize with the first algorithm

    def update_form(self):
        """
        Update the displayed form fields based on the chosen algorithm.
        Clears old fields and shows only relevant inputs.
        """
        # Clear old fields
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        algorithm = self.algorithm_combo.currentText()

        if algorithm == "Heuristic":
            # Depth input for heuristic
            self.depth_input = QLineEdit()
            self.depth_input.setToolTip("Search depth (default: 3). Higher = slower but stronger.")
            self.depth_input.setPlaceholderText("e.g., 3")
            self.form_layout.addRow("Search Depth:", self.depth_input)

        elif algorithm in {"NegamaxAlphaBeta", "IDPVS"}:
            # Depth input
            self.depth_input = QLineEdit()
            self.depth_input.setToolTip("Search depth (default: 3).")
            self.depth_input.setPlaceholderText("e.g., 3")
            self.form_layout.addRow("Search Depth:", self.depth_input)

            # Parallel option
            self.parallel_input = QComboBox()
            self.parallel_input.setToolTip("Run in parallel for speed. 'Yes' or 'No'.")
            self.parallel_input.addItems(["Yes", "No"])
            self.form_layout.addRow("Enable Parallel:", self.parallel_input)

        elif algorithm == "MCTSPolicyGuided":
            # Simulations input
            self.simulations_input = QLineEdit()
            self.simulations_input.setToolTip("Number of simulations (default: 1000).")
            self.simulations_input.setPlaceholderText("e.g., 1000")
            self.form_layout.addRow("Simulations:", self.simulations_input)

            # Parallel option
            self.parallel_input = QComboBox()
            self.parallel_input.setToolTip("Run in parallel? 'Yes' or 'No'.")
            self.parallel_input.addItems(["Yes", "No"])
            self.form_layout.addRow("Enable Parallel:", self.parallel_input)

        # Hide group if no settings
        self.settings_group.setVisible(self.form_layout.count() > 0)

    def get_selected_algorithm(self):
        """
        Construct and return an instance of the chosen algorithm with the provided settings.
        If fields are empty or invalid, defaults are used.
        """
        algorithm = self.algorithm_combo.currentText()

        # Helper: get integer from a QLineEdit if possible, else return default
        def get_int_field(field, default):
            if hasattr(self, field):
                text = getattr(self, field).text().strip()
                if text.isdigit():
                    return int(text)
            return default

        # Helper: get boolean for parallel
        def get_parallel(default=False):
            if hasattr(self, 'parallel_input'):
                return (self.parallel_input.currentText() == "Yes")
            return default

        if algorithm == "Heuristic":
            depth = get_int_field('depth_input', 3)
            self.selected_algorithm = Heuristic(depth=depth)

        elif algorithm == "NegamaxAlphaBeta":
            depth = get_int_field('depth_input', 3)
            parallel = get_parallel(False)
            self.selected_algorithm = NegamaxAlphaBeta(depth=depth, parallel=parallel)

        elif algorithm == "IDPVS":
            depth = get_int_field('depth_input', 3)
            parallel = get_parallel(False)
            self.selected_algorithm = IDPVS(depth=depth, parallel=parallel)

        elif algorithm == "MCTSPolicyGuided":
            simulations = get_int_field('simulations_input', 1000)
            parallel = get_parallel(False)
            self.selected_algorithm = MCTSPolicyGuided(num_simulations=simulations, parallel=parallel)

        return self.selected_algorithm
