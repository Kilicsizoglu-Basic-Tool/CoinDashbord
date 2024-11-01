import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QListWidget, QMessageBox
from PyQt6.QtCore import QTimer
import libs.binanceConnect as binanceConnect
import libs.binanceConnectionLock


class TopNegativeCoinWindow(QWidget):
    def __init__(self):
        """
        Initializes the TopNegativeCoinWindow class.

        This constructor sets up the main window for the Crypto Tracker application
        with a title, geometry, and layout. It includes a label, a combo box for 
        selecting time intervals, a button to fetch data, and a list widget to 
        display the coins. It also initializes a Binance connection and a timer.

        Attributes:
            layout (QVBoxLayout): The main layout of the window.
            label (QLabel): A label prompting the user to select a time interval.
            time_interval_combo (QComboBox): A combo box for selecting time intervals.
            fetch_button (QPushButton): A button to fetch data based on the selected time interval.
            coin_list_widget (QListWidget): A list widget to display the coins with negative trends.
            binance (binanceConnect.BinanceConnect): An instance of the BinanceConnect class for API interaction.
            timer (QTimer): A timer to handle periodic updates.
        """
        super().__init__()
        self.setWindowTitle('Crypto Tracker - Negative Trend')
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.label = QLabel("Select Time Interval:")
        self.layout.addWidget(self.label)

        self.time_interval_combo = QComboBox()
        self.time_interval_combo.addItems(["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"])
        self.layout.addWidget(self.time_interval_combo)

        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.clicked.connect(self.fetch)
        self.layout.addWidget(self.fetch_button)

        self.coin_list_widget = QListWidget()
        self.layout.addWidget(self.coin_list_widget)

        self.setLayout(self.layout)

        self.binance = binanceConnect.BinanceConnect()
        self.timer = QTimer()

    def fetch(self):
        lock_instance = libs.binanceConnectionLock.BinanceFileLock()
        try:
            if not lock_instance.is_locked():
                lock_instance.acquire()

                symbols = self.binance.get_all_symbols()
                interval = self.time_interval_combo.currentText()
                print(f"Fetching {len(symbols)} symbols with interval: {interval}")

                i = 15 * 60 * 1000
                self.timer.setInterval(i)
                self.timer.timeout.connect(self.fetch_and_display_lowest_coin)
                self.timer.start()

                kline_data = self.binance.fetch_klines_for_symbols(symbols, interval)

                kline_data = self.binance.fetch_klines_for_symbols(symbols, interval)

                # Find the lowest coin
                lowest_coin, lowest_price = self.find_lowest_coin(kline_data)
                if lowest_coin:
                    message = f"Lowest Coin: {lowest_coin} with price: {lowest_price}"
                    self.coin_list_widget.addItem(message)

                    # Send SMS with Twilio
                    self.twilio.sendSMS(message)
            print(f"An error occurred: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

        finally:
            lock_instance.release()

    def find_lowest_coin(self, kline_data):
        lowest_average_price = float('inf')
        lowest_coin = None

        for symbol, data in kline_data.items():
            # Ensure the data is a DataFrame with at least 100 rows and a 'close' column
            if isinstance(data, pd.DataFrame) and 'close' in data.columns and len(data) >= 100:
                try:
                    # Extract the closing prices from the last 100 klines
                    closing_prices = data['close'].astype(float).tolist()[-100:]
                    # Extract the closing prices from the last 100 candlesticks
                    closing_prices = data['close'].astype(float).tolist()[-100:]
                    bottom_10_closing_prices = sorted(closing_prices)[:10]
                    average_bottom_10 = sum(bottom_10_closing_prices) / len(bottom_10_closing_prices)

                    # Determine if this is the lowest average price so far
                    if average_bottom_10 < lowest_average_price:
                        lowest_average_price = average_bottom_10
                        lowest_coin = symbol

                except ValueError as e:
                    print(f"Error converting closing prices to float for {symbol}: {e}")
                except Exception as e:
                    print(f"Unexpected error processing {symbol}: {e}")

        return lowest_coin, lowest_average_price

    def fetch_and_display_lowest_coin(self):
        try:
            self.coin_list_widget.clear()
            symbols = self.binance.get_all_symbols()
            interval = self.time_interval_combo.currentText()
            kline_data = self.binance.fetch_klines_for_symbols(symbols, interval)
            lowest_coin, lowest_price = self.find_lowest_coin(kline_data)
            if lowest_coin:
                message = f"Lowest Coin: {lowest_coin} with price: {lowest_price}"
                self.coin_list_widget.addItem(message)

        except Exception as e:
            print(f"An error occurred during timer execution: {str(e)}")