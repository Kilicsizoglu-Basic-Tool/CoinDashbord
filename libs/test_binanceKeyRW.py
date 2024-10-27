import unittest
import os
from libs.binanceKeyRW import BinanceAPIKeys

class TestBinanceAPIKeys(unittest.TestCase):

    def setUp(self):
        """Set up a temporary CSV file for testing."""
        self.test_csv_file = 'test_binance_api_keys.csv'
        with open(self.test_csv_file, mode='w', newline='') as csvfile:
            fieldnames = ['api_key', 'api_secret']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'api_key': 'test_api_key', 'api_secret': 'test_api_secret'})

    def tearDown(self):
        """Remove the temporary CSV file after testing."""
        if os.path.exists(self.test_csv_file):
            os.remove(self.test_csv_file)

    def test_read_keys(self):
        """Test reading API keys from the CSV file."""
        keys = BinanceAPIKeys(csv_file_path=self.test_csv_file)
        self.assertEqual(keys.api_key, 'test_api_key')
        self.assertEqual(keys.api_secret, 'test_api_secret')

    def test_write_keys(self):
        """Test writing API keys to the CSV file."""
        keys = BinanceAPIKeys(csv_file_path=self.test_csv_file)
        keys.write_keys('new_api_key', 'new_api_secret')

        # Read the file again to check if the keys were updated
        keys.read_keys()
        self.assertEqual(keys.api_key, 'new_api_key')
        self.assertEqual(keys.api_secret, 'new_api_secret')

if __name__ == '__main__':
    unittest.main()