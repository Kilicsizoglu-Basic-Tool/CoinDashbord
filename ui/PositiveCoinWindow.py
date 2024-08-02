import time
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QListWidget
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import libs.binanceConnect  # Custom module for Binance API connection
import libs.binanceConnectionLock  # Ensure this module is correctly implemented for Binance API
import libs.taapiConnect  # Custom module for TAAPI API connection


class PositiveCoinWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.taapikey = secret='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjUwODExYTc0OThkNzVkYTM2YmNkZDIxIiwiaWF0IjoxNzIyMzc0MTQxLCJleHAiOjMzMjI2ODM4MTQxfQ.wreJRC9-Do8N72lULFPtJXe_fuztoGXJt-5hJw00SCY'
        self.exchange = 'binance'
        self.interval = ''

        # Set up window properties
        self.setWindowTitle("Positive Coin")
        self.setGeometry(150, 150, 800, 600)  # Adjusted size for pie chart

        # Create layout and widgets
        layout = QVBoxLayout(self)

        self.label = QLabel("Positive Change Coins", self)
        
        # Time interval selection
        self.time_interval_label = QLabel("Select Time Interval:", self)
        self.time_interval_combo = QComboBox(self)
        self.time_interval_combo.addItems([
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        ])
        self.time_interval_combo.setCurrentText('15m')  # Default selection to 4 hours

        # Fetch and display button
        self.fetch_button = QPushButton("Fetch and Display", self)
        self.fetch_button.clicked.connect(self.fetch_and_display_positive_coins)

        # Matplotlib Figure for Pie Chart
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        # List widget for displaying coins with potential
        self.coin_list_widget = QListWidget()

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.time_interval_label)
        layout.addWidget(self.time_interval_combo)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.canvas)
        layout.addWidget(self.coin_list_widget)

        self.setLayout(layout)
        
        self.timer = QTimer()

    def fetch_and_display_positive_coins(self):
        positive_coins = {}
        lock = libs.binanceConnectionLock.BinanceFileLock()
        try:
            with lock:
                # Initialize BinanceConnect class
                bc = libs.binanceConnect.BinanceConnect()
                symbols = bc.get_all_symbols()
                interval = self.time_interval_combo.currentText()
                print(f"Fetching {len(symbols)} symbols with interval: {interval}")
                
                i = 5 * 60 * 1000
                
                self.timer.setInterval(i)
                self.timer.timeout.connect(self.fetch_and_display_positive_coins)
                self.timer.start()

                # Fetch kline data for each symbol
                kline_data = bc.fetch_klines_for_symbols(symbols, interval)

                # Calculate positive changes
                positive_coins = self.calculate_positive_changes(kline_data)

                # Display the results in a pie chart
                self.plot_positive_changes_pie_chart(positive_coins)

            # Fetch and display RSI/StochRSI for potential coins
            self.fetch_and_display_potential_coins(positive_coins)
        
        except Exception as e:
            print(f"Failed to acquire lock: {e}")

    def calculate_positive_changes(self, data):
        """Calculate average percentage changes for each coin and find positive ones."""
        positive_coins = {}
        for symbol, df in data.items():
            if df is not None and not df.empty:
                df['percentage_change'] = ((df['close'] - df['open']) / df['open']) * 100
                avg_change = df['percentage_change'].mean()
                if avg_change > 0:  # Check for positive average change
                    positive_coins[symbol] = avg_change
                    print(f"{symbol} average positive change: {avg_change:.2f}%")
        return positive_coins

    def plot_positive_changes_pie_chart(self, positive_coins):
        """Plot a pie chart of the positive changes."""
        self.figure.clear()

        if positive_coins:
            # Sort by average positive change and get the top 10
            sorted_positive_coins = dict(sorted(positive_coins.items(), key=lambda item: item[1], reverse=True)[:10])

            # Unpack symbols and changes
            symbols, changes = zip(*sorted_positive_coins.items())

            # Create a pie chart
            ax = self.figure.add_subplot(111)
            ax.pie(changes, labels=symbols, autopct='%1.1f%%', startangle=140)
            ax.set_title('Top 10 Coins by Positive Change')

            # Update the canvas
            self.canvas.draw()
        else:
            QMessageBox.information(self, "No Data", "No positive change data available to display.")

    def fetch_and_display_potential_coins(self, positive_coins):
        """Fetch RSI and StochRSI for coins with potential continuous growth."""
        
        coins = top_5_positive_coins = dict(sorted(positive_coins.items(), key=lambda item: item[1], reverse=True)[:5])
        
        potential_coins = []

        lock = libs.taapiConnectionLock.TAAPIFileLock()
        with lock:
            for symbol in coins:
                try:
                    # Convert symbol format for TAAPI
                    taapi_symbol = libs.taapiConnect.taapiConnect.convert_symbol(symbol)
                    
                    print(f"Fetching RSI and StochRSI for {symbol} ({taapi_symbol})")
                    
                    self.interval = self.time_interval_combo.currentText()
                    
                    # Get RSI and StochRSI values
                    rsi_value = libs.taapiConnect.taapiConnect.get_rsi_values(self.taapikey, self.exchange, symbol, self.interval)
                    print(f"RSI value: {rsi_value}")
                    time.sleep(5)
                    k_value, d_value = libs.taapiConnect.taapiConnect.get_stochrsi_values(self.taapikey, self.exchange, symbol, self.interval)
                    print(f"StochRSI K value: {k_value}, D value: {d_value}")
                    time.sleep(5)

                    print(f"{symbol}: RSI={rsi_value}, StochRSI K={k_value}, D={d_value}")

                    # Check if RSI and StochRSI indicate a potential continuous growth
                    if rsi_value < 50 and k_value < 50 and d_value < 50:
                        potential_coins.append((symbol, rsi_value, k_value, d_value))

                except Exception as e:
                    print(f"Error fetching RSI/StochRSI for {symbol}: {str(e)}")

            # Sort potential coins by RSI value (descending order)
            potential_coins.sort(key=lambda x: x[1], reverse=True)

            # Update list widget with potential coins
            self.coin_list_widget.clear()
            for coin, rsi, k, d in potential_coins:
                self.coin_list_widget.addItem(f"{coin}: RSI={rsi:.2f}, StochRSI K={k:.2f}, D={d:.2f}")
