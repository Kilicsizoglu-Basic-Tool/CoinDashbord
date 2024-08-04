import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import libs.binanceConnect  # Make sure you have this module for Binance API
import libs.binanceConnectionLock  # Ensure this module is correctly implemented for Binance API


class CoinStatusWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Average Percentage Change of Coins")
        self.setGeometry(150, 150, 800, 600)

        # Layout setup
        layout = QVBoxLayout(self)

        # Time interval selection
        self.time_interval_label = QLabel("Select Time Interval:", self)
        self.time_interval_combo = QComboBox(self)
        self.time_interval_combo.addItems([
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        ])
        self.time_interval_combo.setCurrentText('1h')  # Default selection to 4 hours

        # Fetch and plot button
        self.fetch_button = QPushButton("Fetch and Plot", self)
        self.fetch_button.clicked.connect(self.fetch_and_plot_data)

        # Matplotlib Figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Add widgets to layout
        layout.addWidget(self.time_interval_label)
        layout.addWidget(self.time_interval_combo)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        
        self.timer = QTimer()

    def fetch_and_plot_data(self):
        print("Fetching and plotting data...")

        # Clear previous plots
        self.figure.clear()

        # Get selected time interval
        interval = self.time_interval_combo.currentText()
        print(f"Selected time interval: {interval}")
        
        i = 15 * 60 * 1000
            
        self.timer.setInterval(i)
        self.timer.timeout.connect(self.fetch_and_plot_data)
        self.timer.start()

        lock = libs.binanceConnectionLock.BinanceFileLock()
        try:
            with lock:
                # Fetch coin klines
                bc = libs.binanceConnect.BinanceConnect()
                symbols = bc.get_all_symbols()
                print(f"Fetched {len(symbols)} trading pairs.")
                data = bc.fetch_klines_for_symbols(symbols, interval)

                # Calculate average percentage changes
                avg_changes = self.calculate_average_changes(data)
                print("Calculated average percentage changes.")

                # Plot the results as a scatter plot
                self.plot_scatter_chart(avg_changes)
                print("Plotted scatter chart.")
                
        except Exception as e:
            print(f"An error occurred during data fetching or plotting: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def calculate_average_changes(self, data):
        changes = {}
        for symbol, df in data.items():
            if df is not None and not df.empty:
                # Ensure no divide-by-zero errors 
                df['percentage_change'] = df.apply(
                    lambda row: 0 if row['open'] == 0 else ((row['close'] - row['open']) / row['open']) * 100,
                    axis=1
                )
                avg_change = df['percentage_change'].mean()
                changes[symbol] = avg_change
                print(f"Average change for {symbol}: {avg_change:.2f}%")
            else:
                print(f"No data found for {symbol}")
        return changes

    def plot_scatter_chart(self, avg_changes):
        # Create a scatter plot
        ax = self.figure.add_subplot(111)

        # Sort changes for better visualization
        sorted_avg_changes = sorted(avg_changes.items(), key=lambda item: item[1])
        symbols, values = zip(*sorted_avg_changes)

        # Define colors based on positive/negative values
        colors = ['green' if v > 0 else 'red' for v in values]

        # Plot
        scatter = ax.scatter(range(len(values)), values, c=colors, alpha=0.6, edgecolors='w', s=100)

        # Add labels
        ax.set_xticks(range(len(symbols)))
        ax.set_xticklabels(symbols, rotation=90, fontsize=8)
        ax.set_ylabel('Average Percentage Change (%)')
        ax.set_xlabel('Coin Symbol')
        ax.set_title('Scatter Plot of Average Percentage Change of Coins')

        # Add horizontal line at zero
        ax.axhline(0, color='grey', linewidth=0.8, linestyle='--')

        # Grid for better readability
        ax.grid(True, linestyle='--', alpha=0.5)

        # Adjust layout
        plt.tight_layout()

        # Update canvas
        self.canvas.draw()
