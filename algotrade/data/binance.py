"""Production Binance data adapter."""
import pandas as pd
from binance.client import Client
import os
from typing import Optional

class BinanceDataAdapter:
    def __init__(self, symbol: str, start: str, end: str, interval: str = "1d"):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.interval = interval
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.client = Client(self.api_key, self.api_secret)

    def fetch(self) -> pd.DataFrame:
        klines = self.client.get_historical_klines(self.symbol, self.interval, self.start, self.end)
        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        df = df[["open_time", "open", "high", "low", "close", "volume"]]
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)
        df = df.astype(float)
        return df

# Example usage (for test/demo):
if __name__ == "__main__":
    adapter = BinanceDataAdapter("BTCUSDT", "1 Jan, 2021", "31 Jan, 2021", "1d")
    df = adapter.fetch()
    print(df.head())
