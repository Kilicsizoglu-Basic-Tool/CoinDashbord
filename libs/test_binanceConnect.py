import unittest
from unittest.mock import patch, MagicMock
from libs.binanceConnect import BinanceConnect

class TestBinanceConnect(unittest.TestCase):

    @patch('libs.binanceConnect.Client')
    @patch('libs.binanceConnect.libs.binanceKeyRW.BinanceAPIKeys')
    def setUp(self, MockBinanceAPIKeys, MockClient):
        # Mock API keys
        self.mock_api_keys = MockBinanceAPIKeys.return_value
        self.mock_api_keys.api_key = 'test_api_key'
        self.mock_api_keys.api_secret = 'test_api_secret'
        
        # Mock Binance client
        self.mock_client = MockClient.return_value
        
        # Initialize BinanceConnect
        self.binance_connect = BinanceConnect()

    def test_get_balance(self):
        # Mock response
        self.mock_client.futures_account_balance.return_value = [
            {'asset': 'USDT', 'balance': '1000.0'}
        ]
        
        balance = self.binance_connect.get_balance()
        self.assertEqual(balance, 1000.0)
        self.mock_client.futures_account_balance.assert_called_once()

    def test_open_position(self):
        # Mock response
        self.mock_client.futures_create_order.return_value = {'orderId': '12345'}
        
        order = self.binance_connect.open_position('BTCUSDT', 1, 'BUY')
        self.assertEqual(order['orderId'], '12345')
        self.mock_client.futures_create_order.assert_called_once_with(
            symbol='BTCUSDT', side='BUY', type='MARKET', quantity=1
        )

    def test_set_stop_loss(self):
        # Mock response
        self.mock_client.futures_create_order.return_value = {'orderId': '12345'}
        
        self.mock_client.futures_position_information.return_value = [{'positionAmt': '1'}]
        
        stop_loss_order = self.binance_connect.set_stop_loss('BTCUSDT', 50000)
        self.assertEqual(stop_loss_order['orderId'], '12345')
        self.mock_client.futures_create_order.assert_called_once_with(
            symbol='BTCUSDT', side='SELL', type='STOP_MARKET', stopPrice=50000, closePosition=True
        )

    def test_set_take_profit(self):
        # Mock response
        self.mock_client.futures_create_order.return_value = {'orderId': '12345'}
        
        self.mock_client.futures_position_information.return_value = [{'positionAmt': '1'}]
        
        take_profit_order = self.binance_connect.set_take_profit('BTCUSDT', 60000)
        self.assertEqual(take_profit_order['orderId'], '12345')
        self.mock_client.futures_create_order.assert_called_once_with(
            symbol='BTCUSDT', side='SELL', type='TAKE_PROFIT_MARKET', stopPrice=60000, closePosition=True
        )

    def test_close_position(self):
        # Mock response
        self.mock_client.futures_position_information.return_value = [{'positionAmt': '1'}]
        self.mock_client.futures_create_order.return_value = {'orderId': '12345'}
        
        close_order = self.binance_connect.close_position('BTCUSDT')
        self.assertEqual(close_order['orderId'], '12345')
        self.mock_client.futures_create_order.assert_called_once_with(
            symbol='BTCUSDT', side='SELL', type='MARKET', quantity=1, reduceOnly=True
        )

    def test_cancel_order(self):
        # Mock response
        self.mock_client.futures_cancel_order.return_value = {'orderId': '12345'}
        
        cancel_result = self.binance_connect.cancel_order('BTCUSDT', '12345')
        self.assertEqual(cancel_result['orderId'], '12345')
        self.mock_client.futures_cancel_order.assert_called_once_with(symbol='BTCUSDT', orderId='12345')

    def test_get_open_orders(self):
        # Mock response
        self.mock_client.futures_get_open_orders.return_value = [{'orderId': '12345'}]
        
        orders = self.binance_connect.get_open_orders('BTCUSDT')
        self.assertEqual(orders, [{'orderId': '12345'}])
        self.mock_client.futures_get_open_orders.assert_called_once_with(symbol='BTCUSDT')

    def test_is_long(self):
        # Mock response
        self.mock_client.futures_position_information.return_value = [{'positionAmt': '1'}]
        
        is_long = self.binance_connect.is_long('BTCUSDT')
        self.assertTrue(is_long)
        self.mock_client.futures_position_information.assert_called_once_with(symbol='BTCUSDT')

    def test_get_24hr_ticker(self):
        # Mock response
        self.mock_client.futures_ticker.return_value = [{'symbol': 'BTCUSDT', 'priceChangePercent': '5.0'}]
        
        ticker = self.binance_connect.get_24hr_ticker()
        self.assertEqual(ticker, {'BTCUSDT': '5.0'})
        self.mock_client.futures_ticker.assert_called_once()

    def test_get_price(self):
        # Mock response
        self.mock_client.futures_symbol_ticker.return_value = {'price': '50000.0'}
        
        price = self.binance_connect.get_price('BTCUSDT')
        self.assertEqual(price, 50000.0)
        self.mock_client.futures_symbol_ticker.assert_called_once_with(symbol='BTCUSDT')

    def test_get_all_symbols(self):
        # Mock response
        self.mock_client.futures_exchange_info.return_value = {
            'symbols': [{'symbol': 'BTCUSDT', 'status': 'TRADING'}]
        }
        
        symbols = self.binance_connect.get_all_symbols()
        self.assertEqual(symbols, ['BTCUSDT'])
        self.mock_client.futures_exchange_info.assert_called_once()

    def test_get_interval_milliseconds(self):
        milliseconds = self.binance_connect.get_interval_milliseconds('1m')
        self.assertEqual(milliseconds, 60000)

    def test_get_binance_server_time(self):
        # Mock response
        self.mock_client.get_server_time.return_value = {'serverTime': 1620000000000}
        
        server_time = self.binance_connect.get_binance_server_time()
        self.assertEqual(server_time, 1620000000000)
        self.mock_client.get_server_time.assert_called_once()

    def test_get_klines_return(self):
        # Mock response
        self.mock_client.futures_klines.return_value = [
            [1620000000000, '50000.0', '51000.0', '49000.0', '50500.0', '1000', 1620003600000, '50500000.0', 100, '500', '25000000.0', '0']
        ]
        
        klines = self.binance_connect.get_klines_return('BTCUSDT', '1m')
        self.assertIn('BTCUSDT', klines)
        self.assertIsInstance(klines['BTCUSDT'], pd.DataFrame)

    def test_fetch_klines_for_symbols(self):
        # Mock response
        self.mock_client.futures_klines.return_value = [
            [1620000000000, '50000.0', '51000.0', '49000.0', '50500.0', '1000', 1620003600000, '50500000.0', 100, '500', '25000000.0', '0']
        ]
        
        symbols = ['BTCUSDT', 'ETHUSDT']
        klines = self.binance_connect.fetch_klines_for_symbols(symbols, '1m')
        self.assertIn('BTCUSDT', klines)
        self.assertIn('ETHUSDT', klines)
        self.assertIsInstance(klines['BTCUSDT'], pd.DataFrame)
        self.assertIsInstance(klines['ETHUSDT'], pd.DataFrame)

    def test_get_top_symbols_by_volume(self):
        # Mock response
        self.mock_client.futures_ticker.return_value = [
            {'symbol': 'BTCUSDT', 'quoteVolume': '1000000.0'},
            {'symbol': 'ETHUSDT', 'quoteVolume': '500000.0'}
        ]
        
        top_symbols = self.binance_connect.get_top_symbols_by_volume(limit=2)
        self.assertEqual(top_symbols, ['BTCUSDT', 'ETHUSDT'])

    def test_get_order_book(self):
        # Mock response
        self.mock_client.futures_order_book.return_value = {'bids': [['50000.0', '1']], 'asks': [['51000.0', '1']]}
        
        order_book = self.binance_connect.get_order_book('BTCUSDT')
        self.assertEqual(order_book, {'bids': [['50000.0', '1']], 'asks': [['51000.0', '1']]})

    def test_analyze_buy_sell_ratio(self):
        order_book = {'bids': [['50000.0', '1']], 'asks': [['51000.0', '1']]}
        ratio = self.binance_connect.analyze_buy_sell_ratio(order_book)
        self.assertEqual(ratio, 1.0)

    def test_fetch_buy_sell_data_for_symbols(self):
        # Mock response
        self.mock_client.futures_order_book.return_value = {'bids': [['50000.0', '1']], 'asks': [['51000.0', '1']]}
        
        symbols = ['BTCUSDT', 'ETHUSDT']
        data = self.binance_connect.fetch_buy_sell_data_for_symbols(symbols)
        self.assertIn('BTCUSDT', data)
        self.assertIn('ETHUSDT', data)
        self.assertIn('buy_sell_ratio', data['BTCUSDT'])
        self.assertIn('buy_sell_ratio', data['ETHUSDT'])

if __name__ == '__main__':
    unittest.main()