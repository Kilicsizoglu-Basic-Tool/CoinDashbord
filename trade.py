import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.FuturePositionWindow import FuturePositionWindow


def main():
    app = QApplication(sys.argv)
    if not os.path.exists(".coindashbord_config"):
        os.mkdir(".coindashbord_config")
    app.setWindowIcon(QIcon("/usr/share/coindashboard/icon.ico"))
    main_window = FuturePositionWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
