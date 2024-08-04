import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer
import libs.binanceConnectionLock
import libs.taapiConnectionLock
import libs.binanceKeyRW
from ui import KeyWindow
from ui.CoinStatusWindow import CoinStatusWindow
from ui.NegativeCoinWindow import NegativeCoinWindow
from ui.CoinChangeAnalyisWindow import CoinChangeAnalyisWindow
from ui.PositiveCoinWindow import PositiveCoinWindow
from ui.VolumePositionWindow import VolumePositionWindow
from ui.CoinExplorerWindow import CoinExplorerWindow
from ui.Coin24hChangeWindow import Coin24hChangeWindow
from ui.FuturePositionWindow import FuturePositionWindow
from ui.TopPositiveCoinsWindow import TopPositiveCoinWindow
from ui.TopNegativeCoinWindow import TopNegativeCoinWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Crypto Dashboard")
        self.setGeometry(100, 100, 400, 300)

        # Main widget and layout
        main_widget = QWidget(self)
        layout = QVBoxLayout(main_widget)

        self.key_status_text = QLabel("Key Status")

        self.timer = QTimer()
        self.timer.timeout.connect(self.lock_status)
        self.timer.start(1000)

        self.daily_change_button = QPushButton("24h Change", self)
        self.daily_change_button.clicked.connect(self.open_24h_change_window)

        self.top_positive_coins_button = QPushButton("Top Positive Coins", self)
        self.top_positive_coins_button.clicked.connect(self.open_top_positive_coins_window)

        self.top_negative_coins_button = QPushButton("Top Negative Coins", self)
        self.top_negative_coins_button.clicked.connect(self.open_top_negative_coins_window)

        self.future_position_button = QPushButton("Future Position", self)
        self.future_position_button.clicked.connect(self.open_future_position_window)

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

        self.coin_explorer_button = QPushButton("Coin Explorer", self)
        self.coin_explorer_button.clicked.connect(self.open_coin_explorer_window)

        layout.addWidget(self.key_status_text)
        layout.addWidget(self.key_status_button)
        layout.addWidget(self.daily_change_button)
        layout.addWidget(self.coin_status_button)
        layout.addWidget(self.coin_change_analysis_button)
        layout.addWidget(self.negative_coin_button)
        layout.addWidget(self.positive_coin_button)
        layout.addWidget(self.volume_position_button)
        layout.addWidget(self.coin_explorer_button)
        layout.addWidget(self.future_position_button)
        layout.addWidget(self.top_positive_coins_button)
        layout.addWidget(self.top_negative_coins_button)

        self.setCentralWidget(main_widget)

        self.is_key_file()

        # Instance variables for the windows
        self.key_status_window = []
        self.future_position_window = []
        self.coin_status_window = []
        self.negative_coin_window = []
        self.coin_explorer_window = []
        self.open_coin_change_analysis_window = []
        self.positive_coin_window = []
        self.top_positive_coins_window = []
        self.top_negative_coins_window = []
        self.volume_position_window = []
        self.coin_24h_change_window = []

    def lock_status(self):
        binanceLock = libs.binanceConnectionLock.BinanceFileLock()
        block = binanceLock.is_locked()
        taapiLock = libs.taapiConnectionLock.TAAPIFileLock()
        tlock = taapiLock.is_locked()
        self.setWindowTitle("Crypto Dashboard - Binance: " + str(block) + " Taapi: " + str(tlock))

    # Functions to open new windows
    def is_key_file(self):
        bc = libs.binanceKeyRW.BinanceAPIKeys()
        if bc.api_key is not None:
            self.coin_status_button.setEnabled(True)
            self.daily_change_button.setEnabled(True)
            self.negative_coin_button.setEnabled(True)
            self.positive_coin_button.setEnabled(True)
            self.coin_explorer_button.setEnabled(True)
            self.volume_position_button.setEnabled(True)
            self.future_position_button.setEnabled(True)
            self.coin_change_analysis_button.setEnabled(True)
            self.top_positive_coins_button.setEnabled(True)
            self.top_negative_coins_button.setEnabled(True)
            self.key_status_button.setEnabled(False)
            self.key_status_text.setText("Key Status: Key File Found")
        elif bc.api_key is None:
            self.coin_status_button.setEnabled(False)
            self.daily_change_button.setEnabled(False)
            self.future_position_button.setEnabled(False)
            self.negative_coin_button.setEnabled(False)
            self.positive_coin_button.setEnabled(False)
            self.coin_explorer_button.setEnabled(False)
            self.coin_change_analysis_button.setEnabled(False)
            self.top_positive_coins_button.setEnabled(False)
            self.top_negative_coins_button.setEnabled(False)
            self.volume_position_button.setEnabled(False)
            self.key_status_button.setEnabled(True)
            self.key_status_text.setText("Key Status: No Key File Found")

    def open_top_positive_coins_window(self):
        self.top_positive_coins_window.append(TopPositiveCoinWindow())
        for window in self.top_positive_coins_window:
            if not window.isVisible():
                window.show()

    def open_top_negative_coins_window(self):
        self.top_negative_coins_window.append(TopPositiveCoinWindow())
        for window in self.top_negative_coins_window:
            if not window.isVisible():
                window.show()

    def open_future_position_window(self):
        self.future_position_window.append(FuturePositionWindow())
        for window in self.future_position_window:
            if not window.isVisible():
                window.show()

    def open_24h_change_window(self):
        self.coin_24h_change_window.append(Coin24hChangeWindow())
        for window in self.coin_24h_change_window:
            if not window.isVisible():
                window.show()

    def open_coin_explorer_window(self):
        self.coin_explorer_window.append(CoinExplorerWindow())
        for window in self.coin_explorer_window:
            if not window.isVisible():
                window.show()

    def open_key_status_window(self):
        self.key_status_window.append(KeyWindow.APIKeyWindow())
        for window in self.key_status_window:
            if not window.isVisible():
                window.show()

    def open_coin_status_window(self):
        self.coin_status_window.append(CoinStatusWindow())
        for window in self.coin_status_window:
            if not window.isVisible():
                window.show()

    def open_negative_coin_window(self):
        self.negative_coin_window.append(NegativeCoinWindow())
        for window in self.negative_coin_window:
            if not window.isVisible():
                window.show()

    def open_coin_change_analysis_window(self):
        self.open_coin_change_analysis_window.append(CoinChangeAnalyisWindow())
        for window in self.open_coin_change_analysis_window:
            if not window.isVisible():
                window.show()

    def open_positive_coin_window(self):
        self.positive_coin_window.append(PositiveCoinWindow())
        for window in self.positive_coin_window:
            if not window.isVisible():
                window.show()

    def open_volume_position_window(self):
        self.volume_position_window.append(VolumePositionWindow())
        for window in self.volume_position_window:
            if not window.isVisible():
                window.show()
