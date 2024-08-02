import os
import time

class TAAPIFileLock:
    def __init__(self, lock_file_path=".coindashbord_config/.taapi_connection_lock"):
        self.lock_file_path = lock_file_path

    def acquire(self, timeout=None, wait_interval=1):
        """
        Kilidi edinmeye çalışır. Eğer kilit mevcutsa ve timeout verilmişse, 
        belirli aralıklarla kilidin serbest bırakılmasını bekler.

        :param timeout: Kilidi edinmek için maksimum bekleme süresi (saniye cinsinden).
                        Eğer None ise, kilit serbest bırakılana kadar sonsuz bekler.
        :param wait_interval: Bekleme sırasında kontrol edilen aralık (saniye cinsinden).
        """
        # Kilidi edinin
        with open(self.lock_file_path, 'w') as lock_file:
            lock_file.write("True")
        print("Lock acquired.")

    def release(self):
        """Kilit dosyasını silerek kilidi serbest bırakır."""
        if self.is_locked():
            os.remove(self.lock_file_path)
            print("Lock released.")
        else:
            print("No lock to release.")

    def is_locked(self):
        """Kilit durumunu kontrol eder."""
        if os.path.exists(self.lock_file_path):
            with open(self.lock_file_path, 'r') as lock_file:
                lock_status = lock_file.read().strip()
                return lock_status == "True"
        return False

    def __enter__(self):
        """Context manager girişi: Kilidi edin."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager çıkışı: Kilidi serbest bırak."""
        self.release()