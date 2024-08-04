import os
import time

class BinanceFileLock:
    def __init__(self):
        # Ensure the directory exists
        self.lock_file_path = ".coindashbord_config/.binance_connection_lock"
        os.makedirs(os.path.dirname(self.lock_file_path), exist_ok=True)

    def acquire(self, timeout=None, wait_interval=1):
        """
        Attempts to acquire the lock. If the lock is already acquired, it waits 
        for the lock to be released, respecting the timeout if specified.

        :param timeout: Maximum wait time to acquire the lock (in seconds). 
                        If None, wait indefinitely.
        :param wait_interval: The interval between checks for lock release (in seconds).
        """
        start_time = time.time()

        while True:
            # Try to create the lock file if it does not exist
            if not self.is_locked():
                with open(self.lock_file_path, 'w') as lock_file:
                    lock_file.write("True")
                print("Lock acquired.")
                return

            # If timeout is specified, check if time has run out
            if timeout is not None and (time.time() - start_time) > timeout:
                raise TimeoutError("Failed to acquire lock within the specified timeout.")
            
            # Wait for the specified interval before retrying
            time.sleep(wait_interval)

    def release(self):
        """Releases the lock by deleting the lock file."""
        if self.is_locked():
            os.remove(self.lock_file_path)
            print("Lock released.")
        else:
            print("No lock to release.")

    def is_locked(self):
        """Checks the lock status."""
        return os.path.exists(self.lock_file_path)

    def __enter__(self):
        """Context manager entry: acquire the lock."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: release the lock."""
        self.release()

# Example usage:
if __name__ == "__main__":
    try:
        with BinanceFileLock() as lock:
            print("Do some work with the lock acquired.")
            time.sleep(5)  # Simulate some work
    except TimeoutError as e:
        print(e)
