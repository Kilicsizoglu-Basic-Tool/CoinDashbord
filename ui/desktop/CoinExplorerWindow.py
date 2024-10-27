import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QComboBox, QLabel, QLineEdit, QCompleter
from PyQt6.QtCore import QTimer, QStringListModel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import libs.binanceConnect
import libs.binanceConnectionLock

class CoinExplorerWindow(QMainWindow):
    """
    CoinExplorerWindow is a QMainWindow subclass that provides a graphical interface for exploring cryptocurrency data.

    Attributes:
        figure (Figure): Matplotlib figure for plotting.
        canvas (FigureCanvas): Canvas for rendering the Matplotlib figure.
        ax (Axes): Axes object for plotting.
        start_button (QPushButton): Button to start fetching data.
        stop_button (QPushButton): Button to stop fetching data.
        time_interval_combo (QComboBox): ComboBox for selecting time intervals.
        label (QLabel): Label for the time interval selection.
        coin_input (QLineEdit): LineEdit for coin selection with QCompleter.
        coin_completer (QCompleter): Completer for coin input.
        kline_timer (QTimer): Timer for updating kline data.
        plotting_active (bool): Flag indicating if plotting is active.
        bc (BinanceConnect): Binance client for fetching data.
        kline_data (dict): Storage for kline data.

    Methods:
        __init__(): Initializes the CoinExplorerWindow.
        populate_coin_list(): Populates the coin input with available trading symbols.
        start_fetching(): Starts the timers for data fetching.
        stop_fetching(): Stops the data fetching timers.
        update_kline_data(): Updates kline data for the selected symbol and triggers the plot update.
        update_kline_plot(symbol, kline_data): Updates the plot with kline data.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Crypto Dashboard")
        self.setGeometry(100, 100, 800, 600)

        # Matplotlib Figure and Canvas setup
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # GUI components
        self.start_button = QPushButton("Start Fetching Data")
        self.start_button.clicked.connect(self.start_fetching)

        self.stop_button = QPushButton("Stop Fetching Data")
        self.stop_button.clicked.connect(self.stop_fetching)

        self.time_interval_combo = QComboBox()
        self.time_interval_combo.addItems(['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'])
        self.time_interval_combo.setCurrentText('1m')  # Default to 1 minute for frequent updates

        self.label = QLabel("Select Time Interval:")

        # LineEdit with QCompleter for coin selection
        self.coin_input = QLineEdit(self)
        self.coin_completer = QCompleter(self)
        self.coin_input.setCompleter(self.coin_completer)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.label)
        layout.addWidget(self.time_interval_combo)
        layout.addWidget(self.coin_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.kline_timer = QTimer()
        self.kline_timer.timeout.connect(self.update_kline_data)

        self.plotting_active = False

        # Initialize Binance client and populate coin list
        self.bc = libs.binanceConnect.BinanceConnect()
        self.populate_coin_list()

        # Storage for kline data
        self.kline_data = {}

    def populate_coin_list(self):
        """Populates the coin input with available trading symbols."""
        try:
            symbols = self.bc.get_all_symbols()
            usdt_symbols = [symbol for symbol in symbols if symbol.endswith('USDT')]
            self.coin_completer.setModel(QStringListModel(usdt_symbols))  # Use QStringListModel for QCompleter
        except Exception as e:
            print(f"Error populating coin list: {e}")

    def start_fetching(self):
        """Starts the timers for data fetching."""
        if not self.plotting_active:
            self.plotting_active = True

            # Start kline data timer for 15-minute updates
            kline_interval_ms = 15 * 60 * 1000  # 15 minutes in milliseconds
            self.kline_timer.setInterval(kline_interval_ms)
            self.kline_timer.start()

            # Immediately call the function to fetch and update data
            self.update_kline_data()  # Initial kline data fetch and plot

            print("Started fetching data...")

    def stop_fetching(self):
        """Stops the data fetching timers."""
        self.plotting_active = False
        self.kline_timer.stop()
        print("Stopped fetching data.")

    def update_kline_data(self):
        """Updates kline data for the selected symbol and triggers the plot update."""
        selected_symbol = self.coin_input.text().strip()

        if not selected_symbol:
            print("No coin selected for fetching kline data.")
            return

        binance_lock = libs.binanceConnectionLock.BinanceFileLock()
        try:
            if not binance_lock.is_locked():
                binance_lock.acquire()
                print(f"Fetching kline data for selected symbol: {selected_symbol}")

                interval = self.time_interval_combo.currentText()
                kline_data = self.bc.get_klines_return(selected_symbol, interval)

                # Check if kline_data is not None and has data
                if kline_data is not None and selected_symbol in kline_data:
                    self.kline_data[selected_symbol] = kline_data
                    print(f"Kline data for {selected_symbol} updated.")

                    # Trigger the plot update
                    self.update_kline_plot(selected_symbol, kline_data)
                else:
                    print(f"No kline data available for {selected_symbol}.")

        except Exception as e:
            print(f"Error updating kline data for {selected_symbol}: {e}")
        finally:
            binance_lock.release()

    def update_kline_plot(self, symbol, kline_data):
        """Updates the plot with kline data."""
        self.ax.clear()

        # Check if kline_data is not empty and has data
        if symbol in kline_data:
            df = kline_data[symbol]  # symbol is used as a key to get the DataFrame

            if not df.empty:
                try:
                    # Extract time and price information from DataFrame
                    close_times = pd.to_datetime(df['open_time'])
                    close_prices = df['close'].astype(float)  # 'close' column is price info

                    print(f"Plotting times for {symbol}:\n{close_times}")
                    print(f"Plotting close prices for {symbol}:\n{close_prices}")

                    # Plotting the kline data
                    self.ax.plot(close_times, close_prices, marker='o', linestyle='-', color='green', label='Close Price')
                    self.ax.set_title(f"Kline Data for {symbol}")
                    self.ax.set_xlabel("Time")
                    self.ax.set_ylabel("Price")
                    self.ax.legend()

                    # Rotate x-axis labels for better visibility
                    self.ax.set_xticks(close_times[::max(len(close_times) // 10, 1)])  # Reduce number of ticks for readability
                    self.ax.set_xticklabels([t.strftime('%Y-%m-%d %H:%M') for t in close_times[::max(len(close_times) // 10, 1)]], rotation=45, ha='right')

                except Exception as e:
                    print(f"Error processing kline data for {symbol}: {e}")
                    self.ax.set_title(f"Error plotting data for {symbol}")

            else:
                print(f"Error plotting data for {symbol}: DataFrame is empty.")
                self.ax.set_title(f"No Data for {symbol}")

        else:
            print(f"Error plotting data: Symbol '{symbol}' not found in kline_data.")
            self.ax.set_title(f"No Data for {symbol}")

        self.canvas.draw()