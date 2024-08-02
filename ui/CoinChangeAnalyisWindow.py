import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QComboBox, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import libs.binanceConnect  # Ensure this module is implemented for Binance API
import libs.binanceConnectionLock  # Ensure this module is correctly implemented for Binance API


class CoinChangeAnalyisWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Coin Change Analysis")
        self.setGeometry(150, 150, 800, 600)

        # Layout and Label
        layout = QVBoxLayout(self)

        # Time interval selection
        self.time_interval_label = QLabel("Select Time Interval:", self)
        self.time_interval_combo = QComboBox(self)
        self.time_interval_combo.addItems([
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        ])
        self.time_interval_combo.setCurrentText('15m')  # Default selection to 1 day

        # Fetch button
        self.fetch_button = QPushButton("Fetch and Display", self)
        self.fetch_button.clicked.connect(self.fetch_and_display_negative_coins)

        # Matplotlib Figure
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        # Add widgets to layout
        layout.addWidget(self.time_interval_label)
        layout.addWidget(self.time_interval_combo)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        
        self.timer = QTimer()

    def fetch_and_display_negative_coins(self):
        lock = libs.binanceConnectionLock.BinanceFileLock()
        try:
            with lock:
                # Initialize the BinanceConnect class
                bc = libs.binanceConnect.BinanceConnect()

                # Get all symbols and set the desired interval
                symbols = bc.get_all_symbols()
                interval = self.time_interval_combo.currentText()
                
                i = 5 * 60 * 1000
                    
                self.timer.setInterval(i)
                self.timer.timeout.connect(self.fetch_and_display_negative_coins)
                self.timer.start()

                print(f"Fetched {len(symbols)} trading pairs.")

                # Fetch klines for each symbol
                kline_data = bc.fetch_klines_for_symbols(symbols, interval)

                # Calculate average changes
                avg_changes = self.calculate_average_changes(kline_data)
                negative_coins = {k: v for k, v in avg_changes.items() if v < 0}
                positive_coins = {k: v for k, v in avg_changes.items() if v >= 0}

                # Plot the pie charts
                self.plot_pie_charts(positive_coins, negative_coins)

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def calculate_average_changes(self, data):
        """Calculate average percentage changes for each coin."""
        changes = {}
        for symbol, df in data.items():
            if df is not None and not df.empty:
                df['percentage_change'] = ((df['close'] - df['open']) / df['open']) * 100
                avg_change = df['percentage_change'].mean()
                changes[symbol] = avg_change
                print(f"{symbol} average change: {avg_change:.2f}%")
        return changes

    def plot_pie_charts(self, positive_changes, negative_changes):
        """Plot pie charts for positive and negative changes."""
        self.figure.clear()

        # First Pie Chart: Number of Positive vs Negative Coins
        ax1 = self.figure.add_subplot(121)
        num_positive = len(positive_changes)
        num_negative = len(negative_changes)
        ax1.pie([num_positive, num_negative], labels=['Positive', 'Negative'], autopct='%1.1f%%', startangle=140)
        ax1.set_title('Positive vs Negative Coins')

        # Second Pie Chart: Average Positive vs Negative Changes
        if positive_changes or negative_changes:
            ax2 = self.figure.add_subplot(122)
            avg_positive_change = np.mean(list(positive_changes.values())) if positive_changes else 0
            avg_negative_change = abs(np.mean(list(negative_changes.values()))) if negative_changes else 0

            # Ensure there is data to plot
            if avg_positive_change == 0 and avg_negative_change == 0:
                ax2.text(0.5, 0.5, "No Changes Available", ha='center', va='center')
            else:
                ax2.pie([avg_positive_change, avg_negative_change], labels=['Avg Positive', 'Avg Negative'],
                        autopct='%1.1f%%', startangle=140)
                ax2.set_title('Avg Positive vs Negative Change')

        # Update canvas
        self.canvas.draw()
