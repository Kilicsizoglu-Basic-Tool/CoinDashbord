import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QHBoxLayout, QFormLayout, QGroupBox, QComboBox, QListWidget, QMessageBox, QCheckBox,
    QSpinBox, QTableWidget, QTableWidgetItem, QCompleter
)
from PyQt6.QtCore import Qt, QTimer, QStringListModel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from libs.binanceConnect import BinanceConnect  # Ensure this module is implemented for Binance API


class FuturePositionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # BinanceConnect instance
        self.bc = BinanceConnect()

        # Global variable to hold current price
        self.current_price = None

        # Set window title and size
        self.setWindowTitle("Crypto Trading Application")
        self.setGeometry(100, 100, 1200, 800)

        # Main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Matplotlib canvas for the chart
        self.canvas = FigureCanvas(plt.Figure())
        self.layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot()

        # Control group box
        self.control_group = QGroupBox("Controls")
        self.control_layout = QFormLayout()
        self.control_group.setLayout(self.control_layout)
        self.layout.addWidget(self.control_group)

        # Input fields for symbol and interval
        self.symbol_input = QLineEdit()
        self.interval_input = QLineEdit()
        self.interval_input.setText("1h")

        # Fetch available symbols and set up autocomplete
        self.symbols = self.bc.get_all_symbols()
        self.symbol_completer = QCompleter(self.symbols)
        self.symbol_input.setCompleter(self.symbol_completer)

        self.symbol_input.setText("BTCUSDT")  # Default value for symbol input

        # Input fields for stop loss and take profit
        self.stop_loss_input = QLineEdit()
        self.take_profit_input = QLineEdit()

        # Add labels to form fields
        self.control_layout.addRow(QLabel("Symbol:"), self.symbol_input)
        self.control_layout.addRow(QLabel("Interval:"), self.interval_input)
        self.control_layout.addRow(QLabel("Stop Loss:"), self.stop_loss_input)
        self.control_layout.addRow(QLabel("Take Profit:"), self.take_profit_input)

        # Test mode toggle
        self.test_mode_checkbox = QCheckBox("Test Mode")
        self.control_layout.addRow(self.test_mode_checkbox)

        # Connect the test mode checkbox state change to the balance update method and order refresh
        self.test_mode_checkbox.stateChanged.connect(self.update_balance_display)
        self.test_mode_checkbox.stateChanged.connect(self.refresh_open_orders)

        # Balance label
        self.balance_label = QLabel("Balance: $0.00")
        self.control_layout.addRow(QLabel("Current Balance:"), self.balance_label)

        # Position controls
        self.position_group = QGroupBox("Position Controls")
        self.position_layout = QFormLayout()
        self.position_group.setLayout(self.position_layout)
        self.layout.addWidget(self.position_group)

        # Quantity and side for opening position
        self.quantity_input = QLineEdit()
        self.side_input = QComboBox()
        self.side_input.addItems(["BUY", "SELL"])

        # Leverage input
        self.leverage_input = QSpinBox()
        self.leverage_input.setRange(1, 125)
        self.leverage_input.setValue(1)  # Default leverage

        self.position_layout.addRow(QLabel("Quantity:"), self.quantity_input)
        self.position_layout.addRow(QLabel("Side:"), self.side_input)
        self.position_layout.addRow(QLabel("Leverage:"), self.leverage_input)

        # Button layout for positions
        self.position_button_layout = QHBoxLayout()
        self.layout.addLayout(self.position_button_layout)

        # Buttons for position management
        self.open_position_button = QPushButton("Open Position")
        self.close_position_button = QPushButton("Close Position")
        self.position_button_layout.addWidget(self.open_position_button)
        self.position_button_layout.addWidget(self.close_position_button)

        # Button click events for positions
        self.open_position_button.clicked.connect(self.open_position)
        self.close_position_button.clicked.connect(self.close_position)

        # Order management controls
        self.order_group = QGroupBox("Order Management")
        self.order_layout = QVBoxLayout()
        self.order_group.setLayout(self.order_layout)
        self.layout.addWidget(self.order_group)

        # List widget to display open orders
        self.open_orders_list = QListWidget()
        self.order_layout.addWidget(self.open_orders_list)

        # Button to refresh and cancel orders
        self.refresh_orders_button = QPushButton("Refresh Open Orders")
        self.cancel_order_button = QPushButton("Cancel Selected Order")
        self.order_layout.addWidget(self.refresh_orders_button)
        self.order_layout.addWidget(self.cancel_order_button)

        # Button click events for order management
        self.refresh_orders_button.clicked.connect(self.refresh_open_orders)
        self.cancel_order_button.clicked.connect(self.cancel_selected_order)

        # Timer for updating the chart every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_chart)
        self.timer.timeout.connect(self.update_price)  # Update price every interval
        self.timer.start(15 * 1000)  # 15 seconds interval

        # Test mode balance
        self.test_balance = 1000.0  # $1000 simulated balance

        # Data structures for storing test and real trades
        self.test_trades = []  # List to store test trade details
        self.real_trades = []  # List to store real trade details

        # Trade history table
        self.trade_history_table = QTableWidget()
        self.trade_history_table.setColumnCount(5)
        self.trade_history_table.setHorizontalHeaderLabels(["Symbol", "Quantity", "Side", "Leverage", "Balance"])
        self.layout.addWidget(self.trade_history_table)

        # Save trade data button
        self.save_trades_button = QPushButton("Save Trade Data")
        self.save_trades_button.clicked.connect(self.save_trade_data)
        self.layout.addWidget(self.save_trades_button)

        # Update the balance display initially
        self.update_balance_display()

    def load_chart(self):
        """Load and display the chart based on the selected symbol and interval."""
        try:
            # Get symbol and interval from the user
            symbol = self.symbol_input.text()
            interval = self.interval_input.text()

            # Fetch kline data using BinanceConnect
            klines = self.bc.fetch_klines_for_symbols([symbol], interval)
            df = klines.get(symbol)
            if df is not None:
                # Plot the chart
                self.ax.clear()
                self.ax.plot(df['open_time'], df['close'], label="Closing Price")
                self.ax.set_title(f"{symbol} - {interval} Chart")
                self.ax.set_xlabel("Date")
                self.ax.set_ylabel("Price (USDT)")
                self.ax.legend()
                self.canvas.draw()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load chart: {str(e)}")

    def update_price(self):
        """Update the current price for the symbol."""
        try:
            symbol = self.symbol_input.text()
            self.current_price = self.bc.get_price(symbol)
            if self.current_price is None:
                QMessageBox.warning(self, "Error", "Failed to fetch current price.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update price: {str(e)}")

    def open_position(self):
        """Open a new trading position."""
        try:
            # Get details for opening a position
            symbol = self.symbol_input.text()
            quantity = float(self.quantity_input.text())
            side = self.side_input.currentText()
            stop_loss = float(self.stop_loss_input.text()) if self.stop_loss_input.text() else None
            take_profit = float(self.take_profit_input.text()) if self.take_profit_input.text() else None
            leverage = self.leverage_input.value()

            # Ensure we have the latest price
            if self.current_price is None:
                self.update_price()

            if self.current_price is None:
                QMessageBox.warning(self, "Error", "Could not fetch the current price. Please try again.")
                return

            if self.test_mode_checkbox.isChecked():
                # Simulate a trade in test mode
                self.simulate_trade(symbol, quantity, side, leverage, stop_loss, take_profit)
            else:
                # Open position on Binance
                order = self.bc.open_position(symbol, quantity, side, stop_loss, take_profit, leverage)
                if order:
                    QMessageBox.information(self, "Position Opened", f"Position opened: {order['orderId']}")
                    self.real_trades.append({
                        "symbol": symbol,
                        "quantity": quantity,
                        "side": side,
                        "leverage": leverage,
                        "balance": self.bc.get_balance()  # Update balance after the trade
                    })
                else:
                    QMessageBox.warning(self, "Error", "Failed to open position.")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers for quantity, stop loss, and take profit.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open position: {str(e)}")

        # Update balance after the trade
        self.update_balance_display()
        self.refresh_open_orders()

    def simulate_trade(self, symbol, quantity, side, leverage, stop_loss, take_profit):
        """Simulate trading with a test balance."""
        try:
            if self.current_price is None:
                QMessageBox.warning(self, "Error", "No current price available for simulation.")
                return

            if leverage < 1:
                leverage = 1

            # Calculate cost and fees based on current price
            cost = quantity * self.current_price
            trade_fee = 0.001 * cost  # Assuming a 0.1% transaction fee

            # Adjust cost for leverage
            adjusted_cost = cost / leverage

            if side == "BUY":
                # Deduct from balance
                self.test_balance -= (adjusted_cost + trade_fee)
            elif side == "SELL":
                # Deduct from balance assuming market entry (as a leveraged short position)
                self.test_balance -= trade_fee
                # Consider possible gain upon closing a SELL (short) position
                potential_profit = adjusted_cost * 0.01  # Assuming a 1% movement for testing purposes
                self.test_balance += potential_profit

            if self.test_balance < 0:
                QMessageBox.warning(self, "Error", "Insufficient test balance.")
                self.test_balance = 0
            else:
                # Check stop loss and take profit
                self.check_stop_loss_take_profit(self.current_price, side, stop_loss, take_profit, quantity)
                QMessageBox.information(self, "Test Trade", f"Test balance: ${self.test_balance:.2f}")

            price = self.bc.get_price(symbol)  # Simulate fetching price to update the current price
            # Record the trade in the test trades list
            self.record_test_trade(symbol, quantity, price, side, leverage, self.test_balance)
        except Exception as e:
            QMessageBox.warning(self, "Simulation Error", f"Error in trade simulation: {str(e)}")

    def check_stop_loss_take_profit(self, current_price, side, stop_loss, take_profit, quantity):
        """Adjust balance based on stop loss and take profit."""
        try:
            if side == "BUY":
                if stop_loss and current_price <= stop_loss:
                    loss = (current_price - stop_loss) * quantity
                    self.test_balance += loss
                    QMessageBox.information(self, "Stop Loss Triggered", f"Stop loss triggered. Loss: ${-loss:.2f}")
                elif take_profit and current_price >= take_profit:
                    profit = (take_profit - current_price) * quantity
                    self.test_balance += profit
                    QMessageBox.information(self, "Take Profit Triggered", f"Take profit triggered. Profit: ${profit:.2f}")
            elif side == "SELL":
                if stop_loss and current_price >= stop_loss:
                    loss = (stop_loss - current_price) * quantity
                    self.test_balance -= loss
                    QMessageBox.information(self, "Stop Loss Triggered", f"Stop loss triggered. Loss: ${-loss:.2f}")
                elif take_profit and current_price <= take_profit:
                    profit = (current_price - take_profit) * quantity
                    self.test_balance -= profit
                    QMessageBox.information(self, "Take Profit Triggered", f"Take profit triggered. Profit: ${profit:.2f}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error in stop loss/take profit calculation: {str(e)}")

    def record_test_trade(self, symbol, quantity, price, side, leverage, balance):
        """Store the trade details in the list."""
        trade = {
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "side": side,
            "leverage": leverage,
            "balance": balance
        }
        self.test_trades.append(trade)

        # Update the trade history table
        self.update_trade_history_table()

    def update_trade_history_table(self):
        """Update the trade history table with the latest trade data."""
        # Clear the table before updating
        self.trade_history_table.setRowCount(0)

        # Select which trades to display based on the mode
        trades_to_display = self.test_trades if self.test_mode_checkbox.isChecked() else self.real_trades

        # Update the table with the latest trade data
        self.trade_history_table.setRowCount(len(trades_to_display))
        for row, trade in enumerate(trades_to_display):
            self.trade_history_table.setItem(row, 0, QTableWidgetItem(trade["symbol"]))
            self.trade_history_table.setItem(row, 1, QTableWidgetItem(str(trade["quantity"])))
            self.trade_history_table.setItem(row, 2, QTableWidgetItem(trade["side"]))
            self.trade_history_table.setItem(row, 3, QTableWidgetItem(str(trade["leverage"])))
            self.trade_history_table.setItem(row, 4, QTableWidgetItem(f"${trade['balance']:.2f}"))

    def save_trade_data(self):
        """Save the current trades to a CSV file."""
        try:
            trades_to_save = self.test_trades if self.test_mode_checkbox.isChecked() else self.real_trades
            df = pd.DataFrame(trades_to_save)
            filename = 'test_trades.csv' if self.test_mode_checkbox.isChecked() else 'real_trades.csv'
            df.to_csv(filename, index=False)
            QMessageBox.information(self, "Save Trades", f"Trade data saved to '{filename}'.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save trade data: {str(e)}")

    def close_position(self):
        """Close an open trading position."""
        try:
            # Get the symbol to close the position
            symbol = self.symbol_input.text()

            if self.test_mode_checkbox.isChecked():
                # Simulate closing position in test mode
                self.simulate_close_position(symbol)
            else:
                # Close position on Binance
                order = self.bc.close_position(symbol)
                if order:
                    QMessageBox.information(self, "Position Closed", f"Position closed for {symbol}.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to close position or no open position.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to close position: {str(e)}")

        # Update balance after closing the position
        self.update_balance_display()
        self.refresh_open_orders()

    def simulate_close_position(self, symbol):
        """Simulate closing a position in test mode."""
        try:
            # Simulate finding a matching trade
            matching_trade = next((trade for trade in self.test_trades if trade["symbol"] == symbol), None)

            if matching_trade:
                # Fetch real-time price to simulate closing
                price_per_unit = self.bc.get_price(symbol)
                if price_per_unit is None:
                    QMessageBox.warning(self, "Error", "Failed to fetch price for closing position.")
                    return

                # Simulate closing the position and updating the test balance
                if matching_trade["side"] == "BUY":
                    closing_cost = (price_per_unit - matching_trade["price"]) * matching_trade["quantity"] * matching_trade["leverage"]
                    self.test_balance += closing_cost
                else:
                    closing_cost = (matching_trade["price"] - price_per_unit) * matching_trade["quantity"] * matching_trade["leverage"]
                    self.test_balance += closing_cost

                self.test_trades.remove(matching_trade)
                QMessageBox.information(self, "Test Mode", f"Position closed for {symbol} in test mode.")
            else:
                QMessageBox.warning(self, "Test Mode", "No open position to close.")
        except Exception as e:
            QMessageBox.warning(self, "Simulation Error", f"Error in simulating close position: {str(e)}")

    def refresh_open_orders(self):
        """Refresh the list of open orders."""
        try:
            self.open_orders_list.clear()
            if self.test_mode_checkbox.isChecked():
                # Display test trades
                for trade in self.test_trades:
                    item_text = f"Symbol: {trade['symbol']} | Side: {trade['side']} | Quantity: {trade['quantity']} | Leverage: {trade['leverage']}"
                    self.open_orders_list.addItem(item_text)
            else:
                # Display real trades
                open_orders = self.bc.get_open_orders(self.symbol_input.text())
                for order in open_orders:
                    item_text = f"Order ID: {order['orderId']} | Symbol: {order['symbol']} | Side: {order['side']} | Quantity: {order['origQty']}"
                    self.open_orders_list.addItem(item_text)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh open orders: {str(e)}")

    def cancel_selected_order(self):
        """Cancel the selected order from the open orders list."""
        try:
            selected_item = self.open_orders_list.currentItem()
            if selected_item:
                if self.test_mode_checkbox.isChecked():
                    # In test mode, simply remove the test order from the list
                    row = self.open_orders_list.row(selected_item)
                    del self.test_trades[row]
                    self.update_trade_history_table()
                else:
                    # Extract the order ID from the selected item and cancel on Binance
                    order_id = int(selected_item.text().split("|")[0].split(":")[1].strip())
                    symbol = self.symbol_input.text()
                    result = self.bc.cancel_order(symbol, order_id)
                    if result:
                        QMessageBox.information(self, "Order Canceled", f"Order {order_id} canceled.")
                        self.refresh_open_orders()
                    else:
                        QMessageBox.warning(self, "Error", "Failed to cancel order.")
            else:
                QMessageBox.warning(self, "No Selection", "Please select an order to cancel.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to cancel order: {str(e)}")

    def update_balance_display(self):
        """Update the balance display based on mode."""
        try:
            if self.test_mode_checkbox.isChecked():
                # Display test balance
                balance = self.test_balance
            else:
                # Fetch real balance from Binance
                try:
                    balance = self.bc.get_balance()  # Ensure get_balance is implemented in BinanceConnect
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to fetch balance: {str(e)}")
                    balance = 0

            self.balance_label.setText(f"Balance: ${balance:.2f}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error updating balance display: {str(e)}")
