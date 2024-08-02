import time
import pandas as pd
from binance.client import Client
from concurrent.futures import ThreadPoolExecutor, as_completed
import libs.binanceKeyRW

class BinanceConnect:
    def __init__(self):
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize the Binance client with API keys."""
        # Load API keys from CSV using the custom library
        api_keys = libs.binanceKeyRW.BinanceAPIKeys()
        if api_keys.api_key and api_keys.api_secret:
            print("API keys loaded successfully.")
            return Client(api_keys.api_key, api_keys.api_secret)
        else:
            raise Exception("API keys are not set. Please ensure the CSV file contains valid keys.")

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

    def get_klines(self, symbol, interval):
        """Fetch kline data for a given symbol and interval."""
        if not symbol.endswith('USDT'):
            return None

        try:
            print(f"Fetching klines for {symbol} with interval {interval}...")
            klines = self.client.futures_klines(symbol=symbol, interval=interval, limit=10)
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

            return df
        except Exception as e:
            print(f"Error fetching klines for {symbol}: {e}")
            return None

    def fetch_klines_for_symbols(self, symbols, interval):
        """Fetch klines for multiple symbols concurrently, with a limit of 20 requests per second."""
        results = {}

        # Divide symbols into batches of 10
        batch_size = 20
        batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]

        for batch_index, batch in enumerate(batches):
            print(f"Processing batch {batch_index + 1} of {len(batches)}...")
            
            # Use ThreadPoolExecutor to manage concurrent requests for each batch
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = {executor.submit(self.get_klines, symbol, interval): symbol for symbol in batch}

                # Process results as they complete
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        df = future.result()
                        if df is not None and not df.empty:  # Ensure df is a valid and non-empty result
                            results[symbol] = df
                            print(f"Fetched data for {symbol}.")
                    except Exception as e:
                        print(f"An error occurred for {symbol}: {e}")
            
            # Throttle requests: wait for 1 second before processing the next batch
            if batch_index < len(batches) - 1:
                print("Throttling: waiting for 1 second before processing the next batch...")
                time.sleep(1)

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
        try:
            order_book = self.client.futures_order_book(symbol=symbol, limit=limit)
            return order_book
        except Exception as e:
            print(f"Error fetching order book for {symbol}: {e}")
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
        results = {}

        # Divide symbols into batches of 10
        batch_size = 20
        batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]

        for batch_index, batch in enumerate(batches):
            print(f"Processing batch {batch_index + 1} of {len(batches)}...")
            
            # Use ThreadPoolExecutor to manage concurrent requests for each batch
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = {executor.submit(self.get_order_book, symbol): symbol for symbol in batch}

                # Process results as they complete
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        order_book = future.result()
                        if order_book is not None:  # Ensure order_book is a valid result
                            buy_sell_ratio = self.analyze_buy_sell_ratio(order_book)
                            results[symbol] = {
                                'symbol': symbol,
                                'buy_sell_ratio': buy_sell_ratio
                            }
                            print(f"Fetched buy-sell data for {symbol}.")
                    except Exception as e:
                        print(f"An error occurred for {symbol}: {e}")
            
            # Throttle requests: wait for 1 second before processing the next batch
            if batch_index < len(batches) - 1:
                print("Throttling: waiting for 1 second before processing the next batch...")
                time.sleep(1)

        return results