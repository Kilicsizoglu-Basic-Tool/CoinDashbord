from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import libs.binanceKeyRW

class APIKeyWindow(QMainWindow):
    """
    APIKeyWindow is a QMainWindow subclass that provides a user interface for managing Binance API keys.

    Attributes:
        api_manager (BinanceAPIKeys): An instance of the BinanceAPIKeys class for reading and writing API keys.
        api_key_label (QLabel): A label for the API key input field.
        api_key_input (QLineEdit): An input field for the API key.
        api_secret_label (QLabel): A label for the API secret input field.
        api_secret_input (QLineEdit): An input field for the API secret, with password echo mode.
        save_button (QPushButton): A button to save the API keys.

    Methods:
        __init__(self, parent=None):
            Initializes the APIKeyWindow, sets up the UI components, and loads existing API keys if available.

        save_api_keys(self):
            Saves the API keys entered by the user to a CSV file. Displays a warning if either field is empty,
            and shows a success or error message based on the outcome of the save operation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Binance API Key Manager")
        self.setGeometry(100, 100, 400, 200)

        self.api_manager = libs.binanceKeyRW.BinanceAPIKeys()

        # Main widget and layout
        main_widget = QWidget(self)
        layout = QVBoxLayout(main_widget)

        # API Key input
        self.api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.api_manager.api_key or "")
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)

        # API Secret input
        self.api_secret_label = QLabel("API Secret:")
        self.api_secret_input = QLineEdit()
        self.api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)  # Hide the secret
        self.api_secret_input.setText(self.api_manager.api_secret or "")
        layout.addWidget(self.api_secret_label)
        layout.addWidget(self.api_secret_input)

        # Save button
        self.save_button = QPushButton("Save API Keys")
        self.save_button.clicked.connect(self.save_api_keys)
        layout.addWidget(self.save_button)

        self.setCentralWidget(main_widget)

    def save_api_keys(self):
        """Save the API keys to the CSV file."""
        api_key = self.api_key_input.text().strip()
        api_secret = self.api_secret_input.text().strip()

        if not api_key or not api_secret:
            QMessageBox.warning(self, "Input Error", "Both API Key and API Secret are required.")
            return

        try:
            self.api_manager.write_keys(api_key, api_secret)
            QMessageBox.information(self, "Success", "API keys have been saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save API keys: {e}")
