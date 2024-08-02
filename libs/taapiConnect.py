from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import requests

class taapiConnect:
    def get_stochrsi_values(secret, exchange, symbol, interval):
        url = f"https://api.taapi.io/stochrsi?secret={secret}&exchange={exchange}&symbol={symbol}&interval={interval}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            k_value = float(data['valueFastK'])
            d_value = float(data['valueFastD'])
            return k_value, d_value
        else:
            raise Exception(f"API request failed with status code: {response.status_code}")

    def convert_symbol(symbol):
        return symbol.replace("USDT", "/USDT")
        
    def get_rsi_values(secret, exchange, symbol, interval):
        url = f"https://api.taapi.io/rsi?secret={secret}&exchange={exchange}&symbol={symbol}&interval={interval}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Convert the value to float
            rsi_value = float(data['value'])
            return rsi_value
        else:
            raise Exception(f"API request failed with status code: {response.status_code}")
        
    def fetch(self, symbols, fetch_type="rsi", repeats=5, delay=15):
        """
        Verileri belirtilen semboller için belirli bir sayıda ve süre boyunca çeker.
        
        :param symbols: İşlem yapılacak sembollerin listesi.
        :param fetch_type: Çekilecek veri tipi ('rsi' veya 'stochrsi').
        :param repeats: Tekrar sayısı.
        :param delay: Her tekrar arasındaki bekleme süresi (saniye cinsinden).
        """
        results = []
        for i in range(repeats):
            print(f"Fetching data, iteration {i+1}/{repeats}...")
            with ThreadPoolExecutor(max_workers=len(symbols)) as executor:
                futures = []
                for symbol in symbols:
                    if fetch_type == "rsi":
                        futures.append(executor.submit(self.get_rsi_values, symbol))
                    elif fetch_type == "stochrsi":
                        futures.append(executor.submit(self.get_stochrsi_values, symbol))
                    else:
                        raise ValueError("Invalid fetch type. Use 'rsi' or 'stochrsi'.")

                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                        print(f"Result: {result}")
                    except Exception as e:
                        print(f"An error occurred: {e}")

            # Bekleme süresi
            if i < repeats - 1:
                datetime.time.sleep(delay)
        
        return results