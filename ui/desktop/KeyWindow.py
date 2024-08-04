import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import csv
import libs.binanceKeyRW

class APIKeyWindow(QMainWindow):
    def __init__(self, selfself):
        super().__init__()
        self.setWindowTitle("Binance API Key Manager")
        self.setGeometry(100, 100, 400, 200)

        self.api_manager = libs.binanceKeyRW.BinanceAPIKeys()
        
        self.selfself = selfself

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
            
        self.selfself.is_key_file()
