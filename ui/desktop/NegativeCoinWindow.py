from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QListWidget
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import libs.binanceConnect  # Custom module for Binance API connection
import libs.binanceConnectionLock  # Ensure this module is correctly implemented for Binance API
import libs.taapiConnect  # Custom module for TAAPI API connection
import libs.taapiConnectionLock  # Custom module for TAAPI API connection
import libs.twilioConnect  # Custom module for Twilio API connection


class NegativeCoinWindow(QWidget):
    """
    NegativeCoinWindow is a QWidget subclass that provides a graphical interface for displaying coins with negative changes over a selected time interval.
    Attributes:
        taapi_key (str): API key for technical analysis.
        exchange (str): The exchange platform, default is 'binance'.
        interval (str): The time interval for fetching data.
        figure (Figure): Matplotlib figure for plotting pie charts.
        canvas (FigureCanvas): Canvas for displaying the matplotlib figure.
        binance (BinanceConnect): Instance of BinanceConnect for interacting with Binance API.
        coin_list_widget (QListWidget): Widget for displaying the list of coins with potential.
        timer (QTimer): Timer for periodic fetching and displaying of negative coins.
    Methods:
        __init__(): Initializes the NegativeCoinWindow with UI components and layout.
        fetch_and_display_negative_coins(): Fetches and displays coins with negative changes.
        calculate_negative_changes(data): Calculates average percentage changes for each coin and identifies negative ones.
        plot_negative_changes_pie_chart(negative_coins): Plots a pie chart of the negative changes.
        fetch_and_display_potential_coins(positive_coins): Fetches and displays coins with potential continuous growth.
        calculate_potential_coins(negative_coins): Calculates potential coins based on negative changes.
    """
    def __init__(self):
        super().__init__()
        
        self.taapikey = ''
        self.exchange = 'binance'
        self.interval = ''
        self.taapi_key = ''
        # Set up window properties
        self.setWindowTitle("Negative Coin")
        self.setGeometry(150, 150, 800, 600)  # Adjusted size for pie chart

        # Create layout and widgets
        layout = QVBoxLayout(self)

        self.label = QLabel("Negative Change Coins", self)
        
        # Time interval selection
        self.time_interval_label = QLabel("Select Time Interval:", self)
        self.time_interval_combo = QComboBox(self)
        self.time_interval_combo.addItems([
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        ])
        self.time_interval_combo.setCurrentText('1h')  # Default selection to 4 hours

        # Fetch and display button
        self.fetch_button = QPushButton("Fetch and Display", self)
        self.fetch_button.clicked.connect(self.fetch_and_display_negative_coins)

        # Matplotlib Figure for Pie Chart
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.binance = libs.binanceConnect.BinanceConnect()
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

    def fetch_and_display_negative_coins(self):
        negative_coins = None
        lock = libs.binanceConnectionLock.BinanceFileLock()
        try:
            if not lock.is_locked():
                lock.acquire()
                # Initialize BinanceConnect class
                symbols = self.binance.get_all_symbols()
                interval = self.time_interval_combo.currentText()
                print(f"Fetching {len(symbols)} symbols with interval: {interval}")
                
                i = 15 * 60 * 1000
                
                self.timer.setInterval(i)
                self.timer.timeout.connect(self.fetch_and_display_negative_coins)
                self.timer.start()

                # Fetch kline data for each symbol
                kline_data = self.binance.fetch_klines_for_symbols(symbols, interval)

                # Calculate negative changes
                negative_coins = self.calculate_negative_changes(kline_data)

                # Display the results in a pie chart
                self.plot_negative_changes_pie_chart(negative_coins)

                self.fetch_and_display_potential_coins(negative_coins)

        except Exception:
            potential_coins = self.calculate_potential_coins(negative_coins)
            self.fetch_and_display_potential_coins(potential_coins)

        lock.release()

    def calculate_negative_changes(self, data):
        """Calculate average percentage changes for each coin and find negative ones."""
        negative_coins = {}
        for symbol, df in data.items():
            if df is not None and not df.empty:
                df['percentage_change'] = ((df['close'] - df['open']) / df['open']) * 100
                avg_change = df['percentage_change'].mean()
                if avg_change < 0:  # Check for negative average change
                    negative_coins[symbol] = avg_change
                    print(f"{symbol} average negative change: {avg_change:.2f}%")
        return negative_coins

    def plot_negative_changes_pie_chart(self, negative_coins):
        """Plot a pie chart of the negative changes."""
        self.figure.clear()

        if negative_coins:
            # Sort by average negative change and get the top 10 (most negative)
            sorted_negative_coins = dict(sorted(negative_coins.items(), key=lambda item: item[1])[:10])

            # Unpack symbols and absolute changes
            symbols, changes = zip(*sorted_negative_coins.items())

            # Convert negative changes to positive for plotting
            absolute_changes = [abs(change) for change in changes]

            # Create a pie chart
            ax = self.figure.add_subplot(111)
            ax.pie(absolute_changes, labels=symbols, autopct='%1.1f%%', startangle=140)
            ax.set_title('Top 10 Coins by Negative Change (Absolute Values)')

            # Update the canvas
            self.canvas.draw()
        else:
            QMessageBox.information(self, "No Data", "No negative change data available to display.")
    
    def plot_negative_changes_pie_chart(self, negative_coins):
        """Plot a pie chart of the negative changes."""
        self.figure.clear()

        if negative_coins:
            # Sort by average negative change and get the top 10 (most negative)
            sorted_negative_coins = dict(sorted(negative_coins.items(), key=lambda item: item[1])[:10])

            # Unpack symbols and absolute changes
            symbols, changes = zip(*sorted_negative_coins.items())

            # Convert negative changes to positive for plotting
            absolute_changes = [abs(change) for change in changes]

            # Create a pie chart
            ax = self.figure.add_subplot(111)
            ax.pie(absolute_changes, labels=symbols, autopct='%1.1f%%', startangle=140)
            ax.set_title('Top 10 Coins by Negative Change (Absolute Values)')

            # Update the canvas
            self.canvas.draw()
        else:
            QMessageBox.information(self, "No Data", "No negative change data available to display.")
            
    def calculate_negative_changes(self, data):
        """Calculate average percentage changes for each coin and find negative ones."""
        negative_coins = {}
        for symbol, df in data.items():
            if df is not None and not df.empty:
                df['percentage_change'] = ((df['close'] - df['open']) / df['open']) * 100
                avg_change = df['percentage_change'].mean()
                if avg_change < 0:  # Check for negative average change
                    negative_coins[symbol] = avg_change
                    print(f"{symbol} average negative change: {avg_change:.2f}%")
        return negative_coins

    def fetch_and_display_potential_coins(self, potential_coins):
        potential_coins.sort(key=lambda x: x[1], reverse=True)

        i = 0
        binance = libs.binanceConnect.BinanceConnect()
        list_coin = binance.get_24hr_ticker()
        # Update list widget with potential coins
        self.coin_list_widget.clear()
        for coin, _, _, _ in potential_coins:
            i += 1
            temp_change = 0
            for c in list_coin:
                if c["symbol"] == coin:
                    temp_change = float(c["priceChangePercent"])
            message += f"{coin}: 24h:{temp_change}\n"
            self.coin_list_widget.addItem(f"{coin}: 24h:{temp_change}")
