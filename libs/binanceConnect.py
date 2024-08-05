import time
import pandas as pd
from binance.client import Client
import threading
import libs.binanceKeyRW
from collections import defaultdict

class BinanceConnect:
    def __init__(self):
        try:
            self.client = self._initialize_client()
            self.lock = threading.Semaphore(15)  # Limit to 15 concurrent requests
        except Exception as e:
            print(f"Initialization error: {e}")

    def _initialize_client(self):
        """Initialize the Binance client with API keys."""
        try:
            # Load API keys from CSV using the custom library
            api_keys = libs.binanceKeyRW.BinanceAPIKeys()
            if api_keys.api_key and api_keys.api_secret:
                print("API keys loaded successfully.")
                return Client(api_keys.api_key, api_keys.api_secret)
            else:
                raise Exception("API keys are not set. Please ensure the CSV file contains valid keys.")
        except Exception as e:
            print(f"Error initializing client: {e}")
            raise

    def get_balance(self):
        try:
            data = self.client.futures_account_balance()
            for d in data:
                if d['asset'] == 'USDT':
                    return float(d['balance'])
            return 0.0
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return 0.0

    def open_position(self, symbol, quantity, side, stop_loss=None, take_profit=None):
        """Open a new position with specified parameters."""
        try:
            # Example order placement
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )

            # Set stop loss and take profit if provided
            if stop_loss:
                self.set_stop_loss(symbol, order['orderId'], stop_loss)
            if take_profit:
                self.set_take_profit(symbol, order['orderId'], take_profit)

            print(f"Opened {side} position for {symbol}, Quantity: {quantity}")
            return order
        except Exception as e:
            print(f"Error opening position for {symbol}: {e}")
            return None

    def set_stop_loss(self, symbol, order_id, stop_price):
        """Set a stop loss order."""
        try:
            stop_loss_order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL' if self.is_long(symbol) else 'BUY',
                type='STOP_MARKET',
                stopPrice=stop_price,
                closePosition=True
            )
            print(f"Set stop loss for {symbol} at {stop_price}")
            return stop_loss_order
        except Exception as e:
            print(f"Error setting stop loss for {symbol}: {e}")
            return None

    def set_take_profit(self, symbol, order_id, take_profit_price):
        """Set a take profit order."""
        try:
            take_profit_order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL' if self.is_long(symbol) else 'BUY',
                type='TAKE_PROFIT_MARKET',
                stopPrice=take_profit_price,
                closePosition=True
            )
            print(f"Set take profit for {symbol} at {take_profit_price}")
            return take_profit_order
        except Exception as e:
            print(f"Error setting take profit for {symbol}: {e}")
            return None

    def close_position(self, symbol):
        """Close an existing position."""
        try:
            # Get the current position
            position_info = self.client.futures_position_information(symbol=symbol)
            for position in position_info:
                quantity = float(position['positionAmt'])
                if quantity != 0:
                    # Determine the side to close the position
                    side = 'SELL' if quantity > 0 else 'BUY'
                    close_order = self.client.futures_create_order(
                        symbol=symbol,
                        side=side,
                        type='MARKET',
                        quantity=abs(quantity),
                        reduceOnly=True
                    )
                    print(f"Closed {side} position for {symbol}, Quantity: {quantity}")
                    return close_order
            print(f"No open position for {symbol} to close.")
            return None
        except Exception as e:
            print(f"Error closing position for {symbol}: {e}")
            return None

    def cancel_order(self, symbol, order_id):
        """Cancel a specific open order."""
        try:
            cancel_result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            print(f"Canceled order {order_id} for {symbol}.")
            return cancel_result
        except Exception as e:
            print(f"Error canceling order {order_id} for {symbol}: {e}")
            return None

    def get_open_orders(self, symbol=None):
        """Get all open orders for a given symbol or all symbols if no symbol is specified."""
        try:
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol)
            else:
                orders = self.client.futures_get_open_orders()
            return orders
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            return []

    def is_long(self, symbol):
        """Check if the position is a long position."""
        try:
            # Retrieve position information
            position_info = self.client.futures_position_information(symbol=symbol)
            for position in position_info:
                if float(position['positionAmt']) > 0:
                    return True
            return False
        except Exception as e:
            print(f"Error checking if position is long for {symbol}: {e}")
            return None

    def get_24hr_ticker(self):
        """Fetch 24-hour ticker data for all symbols."""
        try:
            ticker = self.client.futures_ticker()
            data = {}
            for tick in ticker:
                data[tick['symbol']] = tick["priceChangePercent"]
            return data
        except Exception as e:
            print(f"Error fetching 24-hour ticker: {e}")
            return {}

    def get_price(self, symbol):
        """Fetch the current price for a trading pair."""
        try:
            price = self.client.futures_symbol_ticker(symbol=symbol)
            return float(price['price'])
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

    def get_all_symbols(self):
        """Fetch all trading pairs that are currently active."""
        try:
            exchange_info = self.client.futures_exchange_info()
            return [
                symbol['symbol']
                for symbol in exchange_info['symbols']
                if symbol['status'] == 'TRADING'
            ]
        except Exception as e:
            print(f"Error fetching trading pairs: {e}")
            return []

    def get_interval_milliseconds(self, interval):
        """Convert interval string to milliseconds."""
        seconds_per_unit = {
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800,
            'M': 2592000
        }

        unit = interval[-1]
        if unit not in seconds_per_unit:
            raise ValueError("Invalid interval format")

        try:
            amount = int(interval[:-1])
        except ValueError:
            raise ValueError("Invalid interval format")

        return amount * seconds_per_unit[unit] * 1000

    def get_binance_server_time(self):
        """Fetch the server time from Binance."""
        try:
            server_time = self.client.get_server_time()['serverTime']
            return server_time
        except Exception as e:
            print(f"Error fetching Binance server time: {e}")
            return None

    def get_klines_return(self, symbol, interval):
        """Fetch kline data for a given symbol and interval."""
        results = {}

        if not symbol.endswith('USDT'):
            return None

        try:
            print(f"Fetching klines for {symbol} with interval {interval}...")

            # Calculate the end time as the current time
            end_time = self.get_binance_server_time()
            if not end_time:
                raise Exception("Failed to get server time.")

            # Calculate the start time as 100 intervals before the end time
            interval_milliseconds = self.get_interval_milliseconds(interval)
            start_time = end_time - (100 * interval_milliseconds)

            # Fetch klines
            klines = self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=100
            )

            df = pd.DataFrame(
                klines,
                columns=[
                    'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                    'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                    'taker_buy_quote_asset_volume', 'ignore'
                ]
            )

            # Convert time columns from Unix timestamp to readable datetime
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

            # Convert relevant columns to float for numeric operations
            df[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']] = \
                df[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']].astype(float)

            results[symbol] = df
            print(f"Fetched data for {symbol}.")
        except Exception as e:
            print(f"Error fetching klines for {symbol}: {e}")
        return results

    def get_klines(self, symbol, interval, results):
        """Fetch kline data for a given symbol and interval."""
        if not symbol.endswith('USDT'):
            return None

        with self.lock:
            try:
                end_time = int(time.time() * 1000)  # Current time in milliseconds

                # Calculate the start time as 100 intervals before the end time
                interval_milliseconds = self.get_interval_milliseconds(interval)
                start_time = end_time - (100 * interval_milliseconds)

                # Fetch klines
                klines = self.client.futures_klines(
                    symbol=symbol,
                    interval=interval,
                    startTime=start_time,
                    endTime=end_time,
                    limit=100
                )

                df = pd.DataFrame(
                    klines,
                    columns=[
                        'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                        'taker_buy_quote_asset_volume', 'ignore'
                    ]
                )

                # Convert time columns from Unix timestamp to readable datetime
                df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
                df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

                # Convert relevant columns to float for numeric operations
                df[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']] = \
                    df[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume',
                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']].astype(float)

                results[symbol] = df
                print(f"Fetched data for {symbol}.")
            except Exception as e:
                print(f"Error fetching klines for {symbol}: {e}")
                time.sleep(0.1)

    def fetch_klines_for_symbols(self, symbols, interval):
        """Fetch klines for multiple symbols concurrently, respecting API limits."""
        results = {}
        threads = []

        for symbol in symbols:
            # Create a new thread for each symbol
            thread = threading.Thread(target=self.get_klines, args=(symbol, interval, results))
            threads.append(thread)
            thread.start()

        # Ensure all threads are completed
        for t in threads:
            t.join()

        return results

    def get_top_symbols_by_volume(self, limit=10):
        """Retrieve the top trading pairs by volume."""
        try:
            tickers = self.client.futures_ticker()
            sorted_tickers = sorted(tickers, key=lambda x: float(x['quoteVolume']), reverse=True)
            top_symbols = [ticker['symbol'] for ticker in sorted_tickers if ticker['symbol'].endswith('USDT')][:limit]
            return top_symbols
        except Exception as e:
            print(f"Error fetching top symbols by volume: {e}")
            return []

    def get_order_book(self, symbol, limit=20):
        """Fetch order book data for a given symbol."""
        with self.lock:
            try:
                order_book = self.client.futures_order_book(symbol=symbol, limit=limit)
                return order_book
            except Exception as e:
                print(f"Error fetching order book for {symbol}: {e}")
                time.sleep(0.1)
                return None

    def analyze_buy_sell_ratio(self, order_book):
        """Analyze the buy-sell ratio from the order book."""
        try:
            bids = sum(float(bid[1]) for bid in order_book['bids'])
            asks = sum(float(ask[1]) for ask in order_book['asks'])
            buy_sell_ratio = bids / asks if asks > 0 else float('inf')
            return buy_sell_ratio
        except Exception as e:
            print(f"Error analyzing buy-sell ratio: {e}")
            return None

    def fetch_buy_sell_data_for_symbols(self, symbols):
        """Fetch buy-sell data for multiple symbols concurrently."""
        results = defaultdict(dict)
        threads = []

        for symbol in symbols:
            # Create a new thread for each symbol
            thread = threading.Thread(target=self.fetch_buy_sell_data, args=(symbol, results))
            threads.append(thread)
            thread.start()

        # Ensure all threads are completed
        for t in threads:
            t.join()

        return results

    def fetch_buy_sell_data(self, symbol, results):
        """Fetch buy-sell data for a single symbol."""
        with self.lock:
            try:
                order_book = self.get_order_book(symbol, limit=20)
                if order_book:
                    buy_sell_ratio = self.analyze_buy_sell_ratio(order_book)
                    results[symbol] = {'buy_sell_ratio': buy_sell_ratio}
            except Exception as e:
                print(f"Error fetching buy-sell data for {symbol}: {e}")
                time.sleep(0.1)
