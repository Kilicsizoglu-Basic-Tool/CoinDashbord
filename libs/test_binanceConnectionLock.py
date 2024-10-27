import unittest
import os
import time
from libs.binanceConnectionLock import BinanceFileLock

class TestBinanceFileLock(unittest.TestCase):

    def setUp(self):
        """Set up test environment."""
        self.lock = BinanceFileLock()
        # Ensure the lock file does not exist before each test
        if os.path.exists(self.lock.lock_file_path):
            os.remove(self.lock.lock_file_path)

    def tearDown(self):
        """Clean up test environment."""
        # Ensure the lock file is removed after each test
        if os.path.exists(self.lock.lock_file_path):
            os.remove(self.lock.lock_file_path)

    def test_acquire_lock(self):
        """Test acquiring the lock."""
        self.lock.acquire()
        self.assertTrue(self.lock.is_locked(), "Lock should be acquired.")
        self.lock.release()

    def test_release_lock(self):
        """Test releasing the lock."""
        self.lock.acquire()
        self.lock.release()
        self.assertFalse(self.lock.is_locked(), "Lock should be released.")

    def test_acquire_with_timeout(self):
        """Test acquiring the lock with a timeout."""
        self.lock.acquire()
        with self.assertRaises(TimeoutError):
            self.lock.acquire(timeout=2)
        self.lock.release()

    def test_context_manager(self):
        """Test using the lock as a context manager."""
        with BinanceFileLock() as lock:
            self.assertTrue(lock.is_locked(), "Lock should be acquired within context manager.")
        self.assertFalse(lock.is_locked(), "Lock should be released after context manager.")

    def test_is_locked(self):
        """Test checking the lock status."""
        self.assertFalse(self.lock.is_locked(), "Lock should not be acquired initially.")
        self.lock.acquire()
        self.assertTrue(self.lock.is_locked(), "Lock should be acquired.")
        self.lock.release()
        self.assertFalse(self.lock.is_locked(), "Lock should be released.")

if __name__ == '__main__':
    unittest.main()