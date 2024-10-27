import os
"""
This module initializes and runs the CoinDashboard application.


Functions:
    main(): Initializes the QApplication, sets up the main window, and starts the event loop.

Usage:
    Run this module directly to start the CoinDashboard application.
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.desktop.MainWindow import MainWindow


def main():
    """
    Initializes and runs the CoinDashboard application.

    This function performs the following steps:
    1. Creates a QApplication instance.
    2. Checks if the configuration directory ".coindashboard_config" exists, and creates it if not.
    3. Sets the application window icon.
    4. Initializes and displays the main window of the application.
    5. Starts the application's event loop.

    Note:
        The function expects the necessary imports and definitions for QApplication, QIcon, MainWindow, 
        and other dependencies to be available in the module.

    Raises:
        SystemExit: Exits the application with the status code returned by the event loop.
    """
    app = QApplication(sys.argv)
    if not os.path.exists(".coindashboard_config"):
        os.mkdir(".coindashboard_config")
    app.setWindowIcon(QIcon("/usr/share/crypto-dashboard/icon.ico"))
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
