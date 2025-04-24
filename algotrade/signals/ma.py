"""Production-grade moving average (SMA, EMA) indicator functions."""
import pandas as pd
from typing import Union

def sma(series: Union[pd.Series, pd.DataFrame], window: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window).mean()

def ema(series: Union[pd.Series, pd.DataFrame], window: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=window, adjust=False).mean()

# Example usage (for test/demo):
if __name__ == "__main__":
    data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print("SMA:")
    print(sma(data, 3))
    print("EMA:")
    print(ema(data, 3))
