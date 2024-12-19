from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QSplitter, QFrame, QDialogButtonBox, 
                             QLabel, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt
from gui.ai_select_component import AISelectComponent

class AIAIDialog(QDialog):
    """
    A dialog for configuring two AI players for an AI vs AI game.
    Provides a side-by-side configuration and a final confirmation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure AI vs AI")
        self.setFixedSize(800, 400)

        self.selected_algorithm_ai1 = None
        self.selected_algorithm_ai2 = None

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # Instruction heading
        header_label = QLabel("<b>Set up the AI algorithms for both White and Black players:</b>")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        # Add some instructions
        instructions_label = QLabel("Choose and configure the AI for Player 1 (White) on the left and Player 2 (Black) on the right.\nThen click 'Start Match' to begin.")
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setWordWrap(True)
        main_layout.addWidget(instructions_label)

        splitter = QSplitter(Qt.Horizontal, self)

        # Left side (White AI)
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_label = QLabel("<b>White Player (AI 1)</b>")
        left_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(left_label)
        self.ai1_component = AISelectComponent()
        left_layout.addWidget(self.ai1_component)
        splitter.addWidget(left_frame)

        # Right side (Black AI)
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_label = QLabel("<b>Black Player (AI 2)</b>")
        right_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(right_label)
        self.ai2_component = AISelectComponent()
        right_layout.addWidget(self.ai2_component)
        splitter.addWidget(right_frame)

        main_layout.addWidget(splitter)

        # OK/Cancel buttons at the bottom
        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.dialog_buttons.button(QDialogButtonBox.Ok).setText("Start Match")
        self.dialog_buttons.button(QDialogButtonBox.Cancel).setText("Cancel")
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.rejected.connect(self.reject)
        main_layout.addWidget(self.dialog_buttons)

    def accept(self):
        """
        Validate both AI configurations. If both are good, proceed; otherwise show an error.
        """
        self.selected_algorithm_ai1 = self.ai1_component.get_selected_algorithm()
        self.selected_algorithm_ai2 = self.ai2_component.get_selected_algorithm()

        if not self.selected_algorithm_ai1 or not self.selected_algorithm_ai2:
            QMessageBox.warning(self, "Incomplete Configuration",
                                "Please ensure both AI players are configured before starting the match.")
            return

        super().accept()
