from PyQt6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer
import libs.binanceConnectionLock
import libs.binanceKeyRW
from ui.desktop import KeyWindow
from ui.desktop.CoinStatusWindow import CoinStatusWindow
from ui.desktop.NegativeCoinWindow import NegativeCoinWindow
from ui.desktop.CoinChangeAnalyisWindow import CoinChangeAnalysisWindow
from ui.desktop.PositiveCoinWindow import PositiveCoinWindow
from ui.desktop.VolumePositionWindow import VolumePositionWindow
from ui.desktop.CoinExplorerWindow import CoinExplorerWindow
from ui.desktop.Coin24hChangeWindow import Coin24hChangeWindow
from ui.desktop.FuturePositionWindow import FuturePositionWindow
from ui.desktop.TopPositiveCoinsWindow import TopPositiveCoinWindow
from ui.desktop.TopNegativeCoinWindow import TopNegativeCoinWindow
from ui.desktop.PriceAlertWindow import PriceAlertWindow

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

        self.price_alarm_button = QPushButton("Price Alarm", self)
        self.price_alarm_button.clicked.connect(self.open_price_alarm_window)

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
        layout.addWidget(self.price_alarm_button)

        self.setCentralWidget(main_widget)

        self.is_key_file()

        # Instance variables for the windows
        self.key_status_window = None
        self.future_position_window = None
        self.coin_status_window = None
        self.negative_coin_window = None
        self.coin_explorer_window = None
        self.coin_change_analysis_window = None
        self.positive_coin_window = None
        self.top_positive_coins_window = None
        self.top_negative_coins_window = None
        self.volume_position_window = None
        self.coin_24h_change_window = None
        self.price_alarm_window = None

    def lock_status(self):
        binanceLock = libs.binanceConnectionLock.BinanceFileLock()
        block = binanceLock.is_locked()
        self.setWindowTitle("Crypto Dashboard - Binance: " + str(block))

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
            self.price_alarm_button.setEnabled(True)
            self.key_status_button.setEnabled(True)
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
            self.price_alarm_button.setEnabled(False)
            self.key_status_button.setEnabled(True)
            self.key_status_text.setText("Key Status: No Key File Found")

    def open_price_alarm_window(self):
        if self.price_alarm_window is None or not self.price_alarm_window.isVisible():
            self.price_alarm_window = PriceAlertWindow()
            self.price_alarm_window.show()

    def open_top_positive_coins_window(self):
        if self.top_positive_coins_window is None or not self.top_positive_coins_window.isVisible():
            self.top_positive_coins_window = TopPositiveCoinWindow()
            self.top_positive_coins_window.show()

    def open_top_negative_coins_window(self):
        if self.top_negative_coins_window is None or not self.top_negative_coins_window.isVisible():
            self.top_negative_coins_window = TopNegativeCoinWindow()
            self.top_negative_coins_window.show()

    def open_future_position_window(self):
        if self.future_position_window is None or not self.future_position_window.isVisible():
            self.future_position_window = FuturePositionWindow()
            self.future_position_window.show()

    def open_24h_change_window(self):
        if self.coin_24h_change_window is None or not self.coin_24h_change_window.isVisible():
            self.coin_24h_change_window = Coin24hChangeWindow()
            self.coin_24h_change_window.show()

    def open_coin_explorer_window(self):
        if self.coin_explorer_window is None or not self.coin_explorer_window.isVisible():
            self.coin_explorer_window = CoinExplorerWindow()
            self.coin_explorer_window.show()

    def open_key_status_window(self):
        if self.key_status_window is None or not self.key_status_window.isVisible():
            self.key_status_window = KeyWindow.APIKeyWindow()
            self.key_status_window.show()

    def open_coin_status_window(self):
        if self.coin_status_window is None or not self.coin_status_window.isVisible():
            self.coin_status_window = CoinStatusWindow()
            self.coin_status_window.show()

    def open_negative_coin_window(self):
        if self.negative_coin_window is None or not self.negative_coin_window.isVisible():
            self.negative_coin_window = NegativeCoinWindow()
            self.negative_coin_window.show()

    def open_coin_change_analysis_window(self):
        if self.coin_change_analysis_window is None or not self.coin_change_analysis_window.isVisible():
            self.coin_change_analysis_window = CoinChangeAnalysisWindow()
            self.coin_change_analysis_window.show()

    def open_positive_coin_window(self):
        if self.positive_coin_window is None or not self.positive_coin_window.isVisible():
            self.positive_coin_window = PositiveCoinWindow()
            self.positive_coin_window.show()

    def open_volume_position_window(self):
        if self.volume_position_window is None or not self.volume_position_window.isVisible():
            self.volume_position_window = VolumePositionWindow()
            self.volume_position_window.show()
