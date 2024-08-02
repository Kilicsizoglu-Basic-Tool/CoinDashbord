import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel

import libs.binanceKeyRW
from ui import KeyWindow
from ui.CoinStatusWindow import CoinStatusWindow
from ui.NegativeCoinWindow import NegativeCoinWindow
from ui.CoinChangeAnalyisWindow import CoinChangeAnalyisWindow
from ui.PositiveCoinWindow import PositiveCoinWindow
from ui.VolumePositionWindow import VolumePositionWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Crypto Dashboard")
        self.setGeometry(100, 100, 400, 300)

        # Main widget and layout
        main_widget = QWidget(self)
        layout = QVBoxLayout(main_widget)
        
        self.key_status_text = QLabel("Key Status")
        
        # Create buttons and connect them to functions
        self.key_status_button = QPushButton("Key Status", self)
        self.key_status_button.clicked.connect(self.open_key_status_window)

        # Create buttons and connect them to functions
        self.coin_status_button = QPushButton("Average Percentage Change of Coins", self)
        self.coin_status_button.clicked.connect(self.open_coin_status_window)

        self.negative_coin_button = QPushButton("Negative Coin", self)
        self.negative_coin_button.clicked.connect(self.open_negative_coin_window)
        
        self.coin_change_analysis_button = QPushButton("Coin Change Analysis", self)
        self.coin_change_analysis_button.clicked.connect(self.open_coin_change_analysis_window)

        self.positive_coin_button = QPushButton("Positive Coin", self)
        self.positive_coin_button.clicked.connect(self.open_positive_coin_window)

        self.volume_position_button = QPushButton("Volume Position", self)
        self.volume_position_button.clicked.connect(self.open_volume_position_window)
        
        layout.addWidget(self.key_status_text)
        layout.addWidget(self.key_status_button)
        layout.addWidget(self.coin_status_button)
        layout.addWidget(self.coin_change_analysis_button)
        layout.addWidget(self.negative_coin_button)
        layout.addWidget(self.positive_coin_button)
        layout.addWidget(self.volume_position_button)
        
        self.setCentralWidget(main_widget)
        
        self.is_key_file()

        # Instance variables for the windows
        self.key_status_window = None
        self.coin_status_window = None
        self.negative_coin_window = None
        self.open_coin_change_analysis_window = None
        self.positive_coin_window = None
        self.volume_position_window = None

    # Functions to open new windows
    def is_key_file(self):
        bc = libs.binanceKeyRW.BinanceAPIKeys()
        if bc.api_key != None:
            self.coin_status_button.setEnabled(True)
            self.negative_coin_button.setEnabled(True)
            self.positive_coin_button.setEnabled(True)
            self.volume_position_button.setEnabled(True)
            self.coin_change_analysis_button.setEnabled(True)
            self.key_status_button.setEnabled(False)
            self.key_status_text.setText("Key Status: Key File Found")
        elif bc.api_key == None:
            self.coin_status_button.setEnabled(False)
            self.negative_coin_button.setEnabled(False)
            self.positive_coin_button.setEnabled(False)
            self.coin_change_analysis_button.setEnabled(False)
            self.volume_position_button.setEnabled(False)
            self.key_status_button.setEnabled(True)
            self.key_status_text.setText("Key Status: No Key File Found")

    def open_key_status_window(self):
        if not self.key_status_window or not self.key_status_window.isVisible():
            self.key_status_window = KeyWindow.APIKeyWindow(self)
            self.key_status_window.show()
            
    def open_coin_status_window(self):
        # Ensure only one instance is open at a time
        if not self.coin_status_window or not self.coin_status_window.isVisible():
            self.coin_status_window = CoinStatusWindow()
            self.coin_status_window.show()

    def open_negative_coin_window(self):
        if not self.negative_coin_window or not self.negative_coin_window.isVisible():
            self.negative_coin_window = NegativeCoinWindow()
            self.negative_coin_window.show()
            
    def open_coin_change_analysis_window(self):
        if not self.open_coin_change_analysis_window or not self.open_coin_change_analysis_window.isVisible():
            self.open_coin_change_analysis_window = CoinChangeAnalyisWindow()
            self.open_coin_change_analysis_window.show()

    def open_positive_coin_window(self):
        if not self.positive_coin_window or not self.positive_coin_window.isVisible():
            self.positive_coin_window = PositiveCoinWindow()
            self.positive_coin_window.show()

    def open_volume_position_window(self):
        if not self.volume_position_window or not self.volume_position_window.isVisible():
            self.volume_position_window = VolumePositionWindow()
            self.volume_position_window.show()
