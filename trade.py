import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.desktop.FuturePositionWindow import FuturePositionWindow


def main():
    """
    Entry point for the CoinDashboard application.

    This function initializes the QApplication, checks for the existence of the 
    configuration directory and creates it if it does not exist, sets the window 
    icon, creates the main window, and starts the application's event loop.

    Steps:
    1. Initialize the QApplication with command-line arguments.
    2. Check if the configuration directory ".coindashboard_config" exists.
       - If not, create the directory.
    3. Set the application window icon.
    4. Create and show the main window (FuturePositionWindow).
    5. Start the application's event loop and exit when done.

    Raises:
        SystemExit: When the application event loop exits.
    """
    app = QApplication(sys.argv)
    if not os.path.exists(".coindashboard_config"):
        os.mkdir(".coindashboard_config")
    app.setWindowIcon(QIcon("/usr/share/crypto-dashboard/icon.ico"))
    main_window = FuturePositionWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
