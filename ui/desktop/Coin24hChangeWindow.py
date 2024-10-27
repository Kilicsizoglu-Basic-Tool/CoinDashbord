from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
from libs.binanceConnect import BinanceConnect

class Coin24hChangeWindow(QMainWindow):
    """
    A window that displays the top 10 gainers and losers in the last 24 hours from Binance.
    Attributes:
        client (BinanceConnect): The Binance API client for fetching ticker data.
        central_widget (QWidget): The central widget of the main window.
        layout (QVBoxLayout): The layout manager for the central widget.
        gainers_table (QTableWidget): The table widget displaying the top 10 gainers.
        losers_table (QTableWidget): The table widget displaying the top 10 losers.
        timer (QTimer): The timer for periodically updating the data.
    Methods:
        __init__(): Initializes the Coin24hChangeWindow.
        load_data(): Fetches and processes the 24-hour ticker data from Binance.
        update_table(table, data, raw_data): Updates the given table with the provided data.
    """
    def __init__(self):
        super().__init__()

        # Ana pencere ayarları
        self.setWindowTitle("Binance Top 10 Movers")
        self.setGeometry(100, 100, 250, 700)
        
        self.client = BinanceConnect()

        # Ana widget ve layout
        self.central_widget = QWidget(self)
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Tablo widgetları
        self.gainers_table = QTableWidget(self)
        self.losers_table = QTableWidget(self)

        # Tablo başlıklarını ayarla
        self.gainers_table.setColumnCount(2)
        self.gainers_table.setHorizontalHeaderLabels(["Symbol", "Change (%)"])
        self.losers_table.setColumnCount(2)
        self.losers_table.setHorizontalHeaderLabels(["Symbol", "Change (%)"])

        # Layout'a tabloları ekle
        self.layout.addWidget(self.gainers_table)
        self.layout.addWidget(self.losers_table)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(60 * 60 * 1000)

        # Verileri yükle
        self.load_data()

    def load_data(self):
        # Veriyi al
        data = self.client.get_24hr_ticker()

        # Değişim oranlarına göre sırala
        sorted_tickers = sorted(data.keys(), key=lambda x: float(data[x]), reverse=True)
        sorted_tickers_two = sorted(data.keys(), key=lambda x: float(data[x]))
        
        # En çok yükselen 10 coin
        top_gainers = sorted_tickers[:10]
        # En çok düşen 10 coin
        top_losers = sorted_tickers_two[:10]

        # Tabloları güncelle
        self.update_table(self.gainers_table, top_gainers, data)
        self.update_table(self.losers_table, top_losers, data)
    
    def update_table(self, table, data, raw_data):
        table.setRowCount(len(data))
        for row, ticker in enumerate(data):
            symbol_item = QTableWidgetItem(ticker)
            change_item = QTableWidgetItem(f"{raw_data[ticker]}%")
            table.setItem(row, 0, symbol_item)
            table.setItem(row, 1, change_item)