import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
from libs.binanceConnectionLock import BinanceFileLock
from libs.taapiConnectionLock import TAAPIFileLock
from PyQt6.QtGui import QIcon

class LockStatusApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Ana pencere ayarları
        self.setWindowTitle("Lock Status Checker")
        self.setGeometry(100, 100, 400, 200)

        # Kilit durumlarını kontrol et
        self.binance_lock = BinanceFileLock()
        self.taapi_lock = TAAPIFileLock()

        binance_status = self.check_lock(self.binance_lock)
        taapi_status = self.check_lock(self.taapi_lock)
        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

        # Layout ve widget'ları oluştur
        layout = QVBoxLayout()

        self.binance_label = QLabel(f"Binance Lock Status: {binance_status}")
        self.taapi_label = QLabel(f"TAAPI Lock Status: {taapi_status}")

        # Font boyutunu ayarla
        font = self.binance_label.font()
        font.setPointSize(12)
        self.binance_label.setFont(font)
        self.taapi_label.setFont(font)

        # Layout'a etiketleri ekle
        layout.addWidget(self.binance_label)
        layout.addWidget(self.taapi_label)

        # Ana widget'ı ayarla
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
    def update_ui(self):
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
        # Kilit durumunu kontrol et ve string olarak döndür
        if lock.is_locked():
            return "Locked"
        else:
            return "Unlocked"

def main():
    app = QApplication(sys.argv)
    if not os.path.exists(".coindashbord_config"):
        os.mkdir(".coindashbord_config")
    app.setWindowIcon(QIcon("/usr/share/coindashboard/icon.ico"))
    window = LockStatusApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
