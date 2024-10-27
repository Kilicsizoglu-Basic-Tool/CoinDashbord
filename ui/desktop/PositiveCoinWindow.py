from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QListWidget
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import libs.binanceConnect  # Custom module for Binance API connection
import libs.binanceConnectionLock  # Ensure this module is correctly implemented for Binance API
import libs.twilioConnect  # Custom module for Twilio API connection


class PositiveCoinWindow(QWidget):
    """
    PositiveCoinWindow is a QWidget subclass that provides a graphical interface for displaying coins with positive changes.
    Attributes:
        taapikey (str): API key for technical analysis.
        exchange (str): The exchange platform, default is 'binance'.
        interval (str): Time interval for fetching data.
        label (QLabel): Label for the window title.
        time_interval_label (QLabel): Label for the time interval selection.
        time_interval_combo (QComboBox): ComboBox for selecting time intervals.
        fetch_button (QPushButton): Button to fetch and display positive coins.
        figure (Figure): Matplotlib figure for the pie chart.
        canvas (FigureCanvas): Canvas for displaying the pie chart.
        coin_list_widget (QListWidget): List widget for displaying coins with potential.
        timer (QTimer): Timer for periodic fetching of data.
        binance (BinanceConnect): Instance of BinanceConnect for interacting with Binance API.
    Methods:
        __init__(): Initializes the PositiveCoinWindow and sets up the UI components.
        fetch_and_display_positive_coins(): Fetches and displays coins with positive changes.
        calculate_positive_changes(data): Calculates average percentage changes for each coin and finds positive ones.
        plot_positive_changes_pie_chart(positive_coins): Plots a pie chart of the positive changes.
        fetch_and_display_potential_coins(positive_coins): Fetches RSI and StochRSI for coins with potential continuous growth and displays them.
    """
    def __init__(self):
        super().__init__()

        self.taapikey = secret=''
        self.exchange = 'binance'
        self.interval = ''

        # Set up window properties
        self.setWindowTitle("Positive Coin")
        self.taapikey = ''
        self.binance = libs.binanceConnect.BinanceConnect()
        # Create layout and widgets
        layout = QVBoxLayout(self)

        self.label = QLabel("Positive Change Coins", self)
        
        # Time interval selection
        self.time_interval_label = QLabel("Select Time Interval:", self)
        self.time_interval_combo = QComboBox(self)
        self.time_interval_combo.addItems([
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        ])
        self.time_interval_combo.setCurrentText('1h')  # Default selection to 4 hours

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
        positive_coins = None
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
                self.timer.timeout.connect(self.fetch_and_display_positive_coins)
                self.timer.start()

                # Fetch kline data for each symbol
                kline_data = self.binance.fetch_klines_for_symbols(symbols, interval)

                # Calculate positive changes
                positive_coins = self.calculate_positive_changes(kline_data)

                # Display the results in a pie chart
                self.plot_positive_changes_pie_chart(positive_coins)

                # Fetch and display RSI/StochRSI for potential coins
                self.fetch_and_display_potential_coins(positive_coins)
                    
        except Exception as e:
            print(f"Failed to acquire lock: {e}")

                # Fetch and display RSI/Stochastic RSI for potential coins

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
        # Sort potential coins by RSI value (descending order)
        positive_coins.sort(key=lambda x: x[1], reverse=True)

        twilio = libs.twilioConnect.twilioConnect()

        """Fetch RSI and Stochastic RSI for coins with potential continuous growth."""
        message = "Positive Coins with potential recovery:\n"
            
        i = 0
        binance = libs.binanceConnect.BinanceConnect()
        list_coin = binance.get_24hr_ticker()
        # Update list widget with potential coins
        self.coin_list_widget.clear()
        for coin, rsi, k, d in potential_coins:
            i += 1
            temp_change = 0
            for c in list_coin:
                if c["symbol"] == coin:
                    temp_change = float(c["priceChangePercent"])
        potential_coins = self.calculate_potential_coins(positive_coins)
        for coin, rsi, k, d in potential_coins:
            self.coin_list_widget.addItem(f"{coin}: 24h:{temp_change}")
            
        if i != 0:   
            # Send SMS with potential coins
            twilio.sendSMS(message)
