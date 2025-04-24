"""
Recipe: Calculate Simple and Exponential Moving Averages (SMA, EMA) as per Cookbook Chapter 2.
"""
import pandas as pd

def calculate_sma(series: pd.Series, window: int) -> pd.Series:
    """Calculate simple moving average."""
    return series.rolling(window=window).mean()

def calculate_ema(series: pd.Series, window: int) -> pd.Series:
    """Calculate exponential moving average."""
    return series.ewm(span=window, adjust=False).mean()

if __name__ == "__main__":
    # Example usage
    data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print("SMA:")
    print(calculate_sma(data, 3))
    print("EMA:")
    print(calculate_ema(data, 3))
