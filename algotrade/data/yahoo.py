"""Production Yahoo Finance data adapter."""
import pandas as pd
import yfinance as yf
from typing import Optional

class YahooDataAdapter:
    def __init__(self, symbol: str, start: str, end: str, interval: str = "1d"):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.interval = interval

    def fetch(self) -> pd.DataFrame:
        df = yf.download(self.symbol, start=self.start, end=self.end, interval=self.interval, auto_adjust=True, progress=False)
        df.index.name = "date"
        return df

# Example usage (for test/demo):
if __name__ == "__main__":
    adapter = YahooDataAdapter("AAPL", "2020-01-01", "2021-01-01")
    df = adapter.fetch()
    print(df.head())
