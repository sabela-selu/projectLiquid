"""
Recipe: Download historical OHLCV data from Binance as per Cookbook Chapter 1.
"""
import pandas as pd
from binance.client import Client
import os
from datetime import datetime

def download_binance_ohlcv(symbol: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    """Download OHLCV data from Binance using python-binance."""
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    client = Client(api_key, api_secret)
    klines = client.get_historical_klines(symbol, interval, start, end)
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

if __name__ == "__main__":
    # Example: BTCUSDT daily candles for Jan 2021
    df = download_binance_ohlcv("BTCUSDT", "1 Jan, 2021", "31 Jan, 2021", "1d")
    print(df.head())
