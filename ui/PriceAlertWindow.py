import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
    QRadioButton,
    QHBoxLayout,
    QGroupBox,
    QCompleter
)
from PyQt6.QtCore import QTimer, Qt
from libs.binanceConnect import BinanceConnect
from libs.twilioConnect import twilioConnect


class PriceAlertWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Crypto Price Alerts')
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.label = QLabel("Select Coin:")
        self.layout.addWidget(self.label)

        # Create a QLineEdit with QCompleter for auto-complete functionality
        self.coin_input = QLineEdit()
        self.coin_input.setPlaceholderText("Enter coin symbol (e.g., BTCUSDT)")
        self.layout.addWidget(self.coin_input)

        # Initialize the BinanceConnect and get all symbols
        self.binance = BinanceConnect()
        self.twilio = twilioConnect()
        self.symbols = self.binance.get_all_symbols()

        # Set up auto-complete with QCompleter
        self.completer = QCompleter(self.symbols)
        self.coin_input.setCompleter(self.completer)

        self.price_label = QLabel("Set Price Alert:")
        self.layout.addWidget(self.price_label)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Enter price")
        self.layout.addWidget(self.price_input)

        # Create radio buttons for greater than or less than options
        self.condition_group = QGroupBox("Condition")
        self.condition_layout = QHBoxLayout()

        self.greater_than_radio = QRadioButton("Greater Than")
        self.less_than_radio = QRadioButton("Less Than")
        self.greater_than_radio.setChecked(True)

        self.condition_layout.addWidget(self.greater_than_radio)
        self.condition_layout.addWidget(self.less_than_radio)
        self.condition_group.setLayout(self.condition_layout)
        self.layout.addWidget(self.condition_group)

        self.add_alert_button = QPushButton("Add Alert")
        self.add_alert_button.clicked.connect(self.add_alert)
        self.layout.addWidget(self.add_alert_button)

        self.alert_list_widget = QListWidget()
        self.layout.addWidget(self.alert_list_widget)

        self.setLayout(self.layout)

        self.alerts = []  # Store alerts

        self.timer = QTimer()
        self.timer.setInterval(10000)  # Check every 10 seconds
        self.timer.timeout.connect(self.check_alerts)
        self.timer.start()

    def add_alert(self):
        coin = self.coin_input.text().strip().upper()  # Ensure the coin symbol is uppercase and trimmed
        price_text = self.price_input.text()

        if coin not in self.symbols:
            QMessageBox.critical(self, "Error", "Please enter a valid coin symbol.")
            return

        try:
            price = float(price_text)
            condition = "greater" if self.greater_than_radio.isChecked() else "less"
            self.alerts.append({'coin': coin, 'price': price, 'condition': condition})

            alert_message = f"Alert for {coin}: {'>' if condition == 'greater' else '<'} {price}"
            self.alert_list_widget.addItem(alert_message)
            self.price_input.clear()
            self.coin_input.clear()

        except ValueError:
            QMessageBox.critical(self, "Error", "Please enter a valid number for the price.")

    def check_alerts(self):
        for alert in self.alerts[:]:  # Iterate over a copy of the list to modify it during iteration
            coin = alert['coin']
            target_price = alert['price']
            condition = alert['condition']

            # Fetch latest price from 24-hour statistics
            try:
                current_price = self.binance.get_price(coin)

                if (condition == 'greater' and current_price > target_price) or \
                   (condition == 'less' and current_price < target_price):
                    alert_message = f"Alert Triggered for {coin}: Current price is {current_price}, target was {target_price}."
                    self.twilio.sendSMS(alert_message)
                    self.alert_list_widget.addItem(f"Triggered: {alert_message}")

                    # Remove triggered alert
                    self.alerts.remove(alert)

            except Exception as e:
                print(f"Error fetching price for {coin}: {e}")
                QMessageBox.critical(self, "Error", f"Could not fetch the current price for {coin}.")
