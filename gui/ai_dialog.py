from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from gui.ai_select_component import AISelectComponent

class AIDialog(QDialog):
    """
    A dialog for choosing and configuring an AI for Human vs AI mode.
    Provides a clearer title, instructions, and validation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure AI for Human vs AI")
        self.selected_algorithm = None

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Instruction heading
        header_label = QLabel("<b>Select and configure an AI algorithm for the opponent:</b>")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # AI selection component
        self.ai_select_component = AISelectComponent()
        layout.addWidget(self.ai_select_component)

        # OK/Cancel buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.button(QDialogButtonBox.Ok).setText("Start Game")
        self.buttons.button(QDialogButtonBox.Cancel).setText("Cancel")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def accept(self):
        """
        Validate the chosen AI configuration before closing.
        If no algorithm is selected, show an error message.
        """
        self.selected_algorithm = self.ai_select_component.get_selected_algorithm()
        if not self.selected_algorithm:
            QMessageBox.warning(self, "Invalid Configuration",
                                "Please ensure that you've properly configured the AI before starting.")
            return

        super().accept()
