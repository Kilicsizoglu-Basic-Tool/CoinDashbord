import unittest
from unittest.mock import patch
from libs.browserConnect import BrowserConnect

class TestBrowserConnect(unittest.TestCase):

    @patch('webbrowser.open')
    def test_open_coin_in_browser(self, mock_open):
        browser_connect = BrowserConnect()
        symbol = "BTCUSDT"
        expected_url = f"binance://open_trade?symbol={symbol}"
        
        browser_connect.open_coin_in_browser(symbol)
        
        mock_open.assert_called_once_with(expected_url)

if __name__ == '__main__':
    unittest.main()