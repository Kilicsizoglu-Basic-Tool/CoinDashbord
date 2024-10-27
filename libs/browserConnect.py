import webbrowser

class BrowserConnect:
    """
    A class to handle browser connections for opening cryptocurrency trading pages.

    Methods
    -------
    open_coin_in_browser(symbol: str) -> None
        Opens the trading page for the given cryptocurrency symbol in the browser.
    """
    def open_coin_in_browser(self, symbol):
        url = f"binance://open_trade?symbol={symbol}"
        webbrowser.open(url)