from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import libs.binanceConnect  # Ensure this module is correctly implemented for Binance API
import libs.binanceConnectionLock  # Ensure this module is correctly implemented for Binance API

class VolumePositionWindow(QWidget):
    """
    VolumePositionWindow is a QWidget subclass that provides a graphical interface for displaying the top volume coins
    in a pie chart format. It allows users to select a time interval and fetch volume data from Binance.
    Attributes:
        label (QLabel): Label displaying "Top Volume Coins".
        time_interval_label (QLabel): Label prompting the user to select a time interval.
        time_interval_combo (QComboBox): ComboBox for selecting the time interval.
        fetch_button (QPushButton): Button to fetch and display volume data.
        figure (Figure): Matplotlib Figure object for plotting pie charts.
        canvas (FigureCanvas): Canvas for rendering the Matplotlib Figure.
        timer (QTimer): Timer for periodically fetching and updating volume data.
    Methods:
        __init__(): Initializes the VolumePositionWindow, sets up the UI components, and configures the layout.
        fetch_and_display_volume_data(): Fetches volume data from Binance, calculates top volumes, and updates the pie charts.
        calculate_top_volumes(data): Calculates the coins with the highest average volume from the fetched data.
        plot_volume_pie_charts(volume_data): Plots pie charts for buy, sell, and total volume data.
    """
    def __init__(self):
        super().__init__()

        # Set up the window properties
        self.setWindowTitle("Volume Position")
        self.setGeometry(150, 150, 1200, 800)  # Adjusted size for displaying multiple charts

        # Create layout and widgets
        layout = QVBoxLayout(self)

        self.label = QLabel("Top Volume Coins", self)

        # Time interval selection
        self.time_interval_label = QLabel("Select Time Interval:", self)
        self.time_interval_combo = QComboBox(self)
        self.time_interval_combo.addItems([
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        ])
        self.time_interval_combo.setCurrentText('1h')  # Default selection to 1 day

        # Fetch and display button
        self.fetch_button = QPushButton("Fetch and Display", self)
        self.fetch_button.clicked.connect(self.fetch_and_display_volume_data)

        # Matplotlib Figure for Pie Charts
        self.figure = Figure(figsize=(15, 8))
        self.figure = Figure(figsize=(15, 8))

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.time_interval_label)
        layout.addWidget(self.time_interval_combo)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        
        self.timer = QTimer()

    def fetch_and_display_volume_data(self):
        
        lock = libs.binanceConnectionLock.BinanceFileLock()
        try:
            with lock:
                # Initialize BinanceConnect class
                bc = libs.binanceConnect.BinanceConnect()
                symbols = bc.get_all_symbols()
                interval = self.time_interval_combo.currentText()
                
                # Set timer interval to 5 minutes (5 * 60 * 1000 milliseconds)
                i = 15 * 60 * 1000
                self.timer.setInterval(i)
                self.timer.timeout.connect(self.fetch_and_display_volume_data)
                self.timer.start()

                print(f"Fetching {len(symbols)} symbols with interval: {interval}")
                
                try:
                    # Fetch kline data for each symbol
                    kline_data = bc.fetch_klines_for_symbols(symbols, interval)
                    kline_data = bc.fetch_klines_for_symbols(symbols, interval)
                    # Calculate top volumes
                    top_volume_coins = self.calculate_top_volumes(kline_data)

                    # Plot the pie charts
                    self.plot_volume_pie_charts(top_volume_coins)

                except Exception as e:  
                    QMessageBox.critical(self, "Error", f"Failed to fetch data: {e}")
                    
        except Exception as e:
            print(f"Failed to acquire lock: {e}")

    def calculate_top_volumes(self, data):
        """Calculate coins with the highest average volume."""
        buy_volume_data = {}
        sell_volume_data = {}
        total_volume_data = {}

        for symbol, df in data.items():
            if df is not None and not df.empty:
                # Convert volume columns to numeric
                df['taker_buy_base_asset_volume'] = pd.to_numeric(df['taker_buy_base_asset_volume'], errors='coerce')
                df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

                avg_buy_volume = df['taker_buy_base_asset_volume'].mean()
                avg_total_volume = df['volume'].mean()
                avg_sell_volume = avg_total_volume - avg_buy_volume

                buy_volume_data[symbol] = avg_buy_volume
                sell_volume_data[symbol] = avg_sell_volume
                total_volume_data[symbol] = avg_total_volume

                print(f"{symbol} - Avg Buy Volume: {avg_buy_volume:.2f}, Avg Sell Volume: {avg_sell_volume:.2f}, Avg Total Volume: {avg_total_volume:.2f}")

        # Sort by total average volume in descending order and get the top 10
        sorted_total_volumes = dict(sorted(total_volume_data.items(), key=lambda item: item[1], reverse=True)[:10])
        sorted_buy_volumes = {k: buy_volume_data[k] for k in sorted_total_volumes}
        sorted_sell_volumes = {k: sell_volume_data[k] for k in sorted_total_volumes}

        return sorted_buy_volumes, sorted_sell_volumes, sorted_total_volumes

    def plot_volume_pie_charts(self, volume_data):
        """Plot pie charts for buy, sell, and total volume data."""
        self.figure.clear()

        buy_volume_data, sell_volume_data, total_volume_data = volume_data

        # Unpack symbols and volumes
        symbols_buy, volumes_buy = zip(*buy_volume_data.items())
        symbols_sell, volumes_sell = zip(*sell_volume_data.items())
        symbols_total, volumes_total = zip(*total_volume_data.items())

        # Create subplots for the three pie charts
        ax1 = self.figure.add_subplot(131)
        ax1.pie(volumes_buy, labels=symbols_buy, autopct='%1.1f%%', startangle=140)
        ax1.pie(volumes_buy, labels=symbols_buy, autopct='%1.1f%%', startangle=140)

        ax2 = self.figure.add_subplot(132)
        ax2.pie(volumes_sell, labels=symbols_sell, autopct='%1.1f%%', startangle=140)
        ax2.pie(volumes_sell, labels=symbols_sell, autopct='%1.1f%%', startangle=140)

        ax3 = self.figure.add_subplot(133)
        ax3.pie(volumes_total, labels=symbols_total, autopct='%1.1f%%', startangle=140)
        ax3.set_title('Top Coins by Total Volume')

        # Adjust layout and update the canvas
        self.figure.tight_layout()
        self.canvas.draw()

