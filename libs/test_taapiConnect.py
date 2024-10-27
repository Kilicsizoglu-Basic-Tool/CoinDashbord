import unittest
from unittest.mock import patch, MagicMock
from libs.taapiConnect import TaapiConnect

class TestTaapiConnect(unittest.TestCase):

    @patch('libs.taapiConnect.requests.get')
    def test_get_stochrsi_values_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'valueFastK': '20.0',
            'valueFastD': '30.0'
        }
        mock_get.return_value = mock_response

        taapi = TaapiConnect()
        symbol, k_value, d_value = taapi.get_stochrsi_values('secret', 'exchange', 'symbol', 'interval')

        self.assertEqual(symbol, 'symbol')
        self.assertEqual(k_value, 20.0)
        self.assertEqual(d_value, 30.0)

    @patch('libs.taapiConnect.requests.get')
    def test_get_stochrsi_values_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        taapi = TaapiConnect()

        with patch.object(taapi, 'get_stochrsi_values', return_value=('symbol', 0.0, 0.0)) as mock_retry:
            symbol, k_value, d_value = taapi.get_stochrsi_values('secret', 'exchange', 'symbol', 'interval')
            self.assertEqual(symbol, 'symbol')
            self.assertEqual(k_value, 0.0)
            self.assertEqual(d_value, 0.0)
            mock_retry.assert_called_once()

    def test_convert_symbol(self):
        taapi = TaapiConnect()
        converted_symbol = taapi.convert_symbol('BTCUSDT')
        self.assertEqual(converted_symbol, 'BTC/USDT')

    @patch('libs.taapiConnect.requests.get')
    def test_get_rsi_values_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'value': '50.0'
        }
        mock_get.return_value = mock_response

        taapi = TaapiConnect()
        symbol, rsi_value = taapi.get_rsi_values('secret', 'exchange', 'symbol', 'interval')

        self.assertEqual(symbol, 'symbol')
        self.assertEqual(rsi_value, 50.0)

    @patch('libs.taapiConnect.requests.get')
    def test_get_rsi_values_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        taapi = TaapiConnect()

        with patch.object(taapi, 'get_rsi_values', return_value=('symbol', 0.0)) as mock_retry:
            symbol, rsi_value = taapi.get_rsi_values('secret', 'exchange', 'symbol', 'interval')
            self.assertEqual(symbol, 'symbol')
            self.assertEqual(rsi_value, 0.0)
            mock_retry.assert_called_once()

    @patch.object(TaapiConnect, 'get_rsi_values', return_value=('symbol', 50.0))
    @patch.object(TaapiConnect, 'get_stochrsi_values', return_value=('symbol', 20.0, 30.0))
    def test_fetch(self, mock_get_stochrsi_values, mock_get_rsi_values):
        taapi = TaapiConnect()
        symbols = ['symbol1', 'symbol2']
        results = taapi.fetch(symbols, 'secret', 'exchange', 'interval', fetch_type='rsi', repeats=1, delay=0)

        self.assertEqual(len(results), 2)
        self.assertIn(('symbol', 50.0), results)

        results = taapi.fetch(symbols, 'secret', 'exchange', 'interval', fetch_type='stochrsi', repeats=1, delay=0)

        self.assertEqual(len(results), 2)
        self.assertIn(('symbol', 20.0, 30.0), results)

if __name__ == '__main__':
    unittest.main()