import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
from libs.binanceConnectionLock import BinanceFileLock
from libs.taapiConnectionLock import TAAPIFileLock
from PyQt6.QtGui import QIcon

class LockStatusApp(QMainWindow):
    """
    LockStatusApp is a QMainWindow application that checks and displays the lock status of Binance and TAAPI files.
    Attributes:
        binance_lock (BinanceFileLock): An instance of BinanceFileLock to check the lock status of Binance.
        taapi_lock (TAAPIFileLock): An instance of TAAPIFileLock to check the lock status of TAAPI.
        timer (QTimer): A QTimer instance to periodically update the UI.
        binance_label (QLabel): A QLabel to display the lock status of Binance.
        taapi_label (QLabel): A QLabel to display the lock status of TAAPI.
    Methods:
        __init__(): Initializes the LockStatusApp, sets up the main window, and starts the timer.
        update_ui(): Updates the UI with the current lock statuses of Binance and TAAPI.
        check_lock(lock): Checks the lock status of the given lock and returns "Locked" or "Unlocked".
    """
    def __init__(self):
        super().__init__()

        # Main window settings
        self.setWindowTitle("Lock Status Checker")
        self.setGeometry(100, 100, 400, 200)

        # Check lock statuses
        self.binance_lock = BinanceFileLock()
        self.taapi_lock = TAAPIFileLock()

        binance_status = self.check_lock(self.binance_lock)
        taapi_status = self.check_lock(self.taapi_lock)
        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

        # Create layout and widgets
        layout = QVBoxLayout()

        self.binance_label = QLabel(f"Binance Lock Status: {binance_status}")
        self.taapi_label = QLabel(f"TAAPI Lock Status: {taapi_status}")

        # Set font size
        font = self.binance_label.font()
        font.setPointSize(12)
        self.binance_label.setFont(font)
        self.taapi_label.setFont(font)

        # Add labels to layout
        layout.addWidget(self.binance_label)
        layout.addWidget(self.taapi_label)

        # Set main widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
    def update_ui(self):
        """
        Updates the user interface to reflect the lock status of Binance and TAAPI.

        This method checks the lock status of both Binance and TAAPI using the `check_lock` method.
        Depending on the lock status, it updates the corresponding labels (`binance_label` and `taapi_label`)
        to display whether each service is "Locked" or "Unlocked".
        """
        lock = self.check_lock(self.binance_lock)
        if lock == "Locked": 
            self.binance_label.setText(f"Binance Lock Status: Locked")
        elif lock == "Unlocked":
            self.binance_label.setText(f"Binance Lock Status: Unlocked")
        lock = self.check_lock(self.taapi_lock)
        if lock == "Locked": 
            self.taapi_label.setText(f"TAAPI Lock Status: Locked")
        elif lock == "Unlocked":
            self.taapi_label.setText(f"TAAPI Lock Status: Unlocked")

    def check_lock(self, lock):
        """
        Check the status of the given lock and return its status as a string.

        Args:
            lock: An object that has an `is_locked` method which returns a boolean.

        Returns:
            str: "Locked" if the lock is locked, otherwise "Unlocked".
        """
        # Check lock status and return as string
        if lock.is_locked():
            return "Locked"
        else:
            return "Unlocked"

def main():
    """
    Main function to initialize and run the Coin Dashboard application.

    This function performs the following steps:
    1. Creates a QApplication instance.
    2. Checks if the configuration directory ".coin_dashboard_config" exists, and creates it if not.
    3. Sets the application window icon.
    4. Initializes and displays the LockStatusApp window.
    5. Executes the application event loop.

    Note:
        Ensure that the required modules (sys, os, QApplication, QIcon, LockStatusApp) are imported before calling this function.
    """
    app = QApplication(sys.argv)
    if not os.path.exists(".coin_dashboard_config"):
        os.mkdir(".coin_dashboard_config")
    app.setWindowIcon(QIcon("/usr/share/crypto-dashboard/icon.ico"))
    window = LockStatusApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
