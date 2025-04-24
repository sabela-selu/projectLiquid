"""
Recipe: Download historical OHLCV data from Yahoo Finance as per Cookbook Chapter 1.
"""
import pandas as pd
import yfinance as yf
from datetime import datetime

def download_yahoo_ohlcv(symbol: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance."""
    df = yf.download(symbol, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
    df.index.name = "date"
    return df

if __name__ == "__main__":
    # Example usage: download AAPL 2020-2021
    df = download_yahoo_ohlcv("AAPL", "2020-01-01", "2021-01-01")
    print(df.head())
