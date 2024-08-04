import datetime
import requests
import threading
import time

class TaapiConnect:
    def get_stochrsi_values(self, secret, exchange, symbol, interval):
        """Fetch StochRSI values for a given symbol and interval."""
        k_value = 0.0
        d_value = 0.0
        url = f"https://api.taapi.io/stochrsi?secret={secret}&exchange={exchange}&symbol={symbol}&interval={interval}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            k_value = float(data['valueFastK'])
            d_value = float(data['valueFastD'])
        else:
            time.sleep(5)
            k_value, d_value = self.get_stochrsi_values(secret, exchange, symbol, interval)
        
        return symbol, k_value, d_value

    def convert_symbol(self, symbol):
        """Convert symbol format from 'USDT' to '/USDT'."""
        return symbol.replace("USDT", "/USDT")
        
    def get_rsi_values(self, secret, exchange, symbol, interval):
        """Fetch RSI values for a given symbol and interval."""
        rsi_value = 0.0
        url = f"https://api.taapi.io/rsi?secret={secret}&exchange={exchange}&symbol={symbol}&interval={interval}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Convert the value to float
            rsi_value = float(data['value'])
        else:
            time.sleep(5)
            rsi_value = self.get_rsi_values(secret, exchange, symbol, interval)
        
        return symbol, rsi_value

        
    def fetch(self, symbols, secret, exchange, interval, fetch_type="rsi", repeats=5, delay=15):
        """
        Fetch data for specified symbols a given number of times and delays.

        :param symbols: List of symbols to process.
        :param secret: API secret key.
        :param exchange: Exchange name.
        :param interval: Data interval.
        :param fetch_type: Type of data to fetch ('rsi' or 'stochrsi').
        :param repeats: Number of repetitions.
        :param delay: Delay between repetitions (in seconds).
        """
        results = []
        
        for i in range(repeats):
            print(f"Fetching data, iteration {i+1}/{repeats}...")
            threads = []
            thread_results = [None] * len(symbols)

            def fetch_symbol_data(index, symbol):
                """Thread function to fetch data for a single symbol."""
                try:
                    if fetch_type == "rsi":
                        result = self.get_rsi_values(secret, exchange, symbol, interval)
                    elif fetch_type == "stochrsi":
                        result = self.get_stochrsi_values(secret, exchange, symbol, interval)
                    else:
                        raise ValueError("Invalid fetch type. Use 'rsi' or 'stochrsi'.")
                    thread_results[index] = result
                    print(f"Result for {symbol}: {result}")
                except Exception as e:
                    print(f"An error occurred for {symbol}: {e}")

            for index, symbol in enumerate(symbols):
                thread = threading.Thread(target=fetch_symbol_data, args=(index, symbol))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            results.extend(filter(None, thread_results))

            # Wait between iterations
            if i < repeats - 1:
                time.sleep(delay)
        
        return results