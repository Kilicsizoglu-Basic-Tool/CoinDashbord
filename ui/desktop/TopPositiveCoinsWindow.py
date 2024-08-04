import sys

import pandas as pd
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QListWidget, QMessageBox
from PyQt6.QtCore import QTimer
import libs.binanceConnect as binanceConnect
import libs.twilioConnect as twilioConnect
import libs.binanceConnectionLock


class TopPositiveCoinWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Crypto Tracker - Positive Trend')
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
        self.twilio = twilioConnect.twilioConnect()
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
                self.timer.timeout.connect(self.fetch_and_display_highest_coin)
                self.timer.start()

                kline_data = self.binance.fetch_klines_for_symbols(symbols, interval)

                # En yüksek coini bul
                highest_coin, highest_price = self.find_highest_coin(kline_data)
                if highest_coin:
                    message = f"Highest Coin: {highest_coin} with price: {highest_price}"
                    self.coin_list_widget.addItem(message)

                    # Twilio ile SMS gönder
                    self.twilio.sendSMS(message)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

        lock_instance.release()

    def find_highest_coin(self, kline_data):
        highest_average_price = 0
        highest_coin = None

        for symbol, data in kline_data.items():
            # Verify that the data is a DataFrame and contains the necessary columns
            if isinstance(data, pd.DataFrame) and 'close' in data.columns and len(data) >= 100:
                try:
                    # Convert the 'close' column to float
                    closing_prices = data['close'].astype(float).tolist()

                    # Calculate the average of the top 10 closing prices
                    top_10_closing_prices = sorted(closing_prices, reverse=True)[:10]
                    average_top_10 = sum(top_10_closing_prices) / len(top_10_closing_prices)

                    # Check if this is the highest average found so far
                    if average_top_10 > highest_average_price:
                        highest_average_price = average_top_10
                        highest_coin = symbol

                except ValueError as e:
                    print(f"Error converting closing prices to float for {symbol}: {e}")
                except Exception as e:
                    print(f"Unexpected error processing {symbol}: {e}")

        return highest_coin, highest_average_price

    def fetch_and_display_highest_coin(self):
        try:
            self.coin_list_widget.clear()
            symbols = self.binance.get_all_symbols()
            interval = self.time_interval_combo.currentText()
            kline_data = self.binance.fetch_klines_for_symbols(symbols, interval)
            highest_coin, highest_price = self.find_highest_coin(kline_data)
            if highest_coin:
                message = f"Highest Coin: {highest_coin} with price: {highest_price}"
                self.coin_list_widget.addItem(message)

                # Twilio ile SMS gönder
                self.twilio.sendSMS(message)

        except Exception as e:
            print(f"An error occurred during timer execution: {str(e)}")