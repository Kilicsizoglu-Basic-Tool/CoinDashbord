import webbrowser

class BrowserConnect:
    def open_coin_in_browser(symbol):
        url = f"binance://open_trade?symbol={symbol}"
        webbrowser.open(url)