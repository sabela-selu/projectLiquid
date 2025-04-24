"""Production-grade ATR (Average True Range) volatility breakout signal generator."""
import pandas as pd
from typing import Union

def atr(high: Union[pd.Series, pd.DataFrame], low: Union[pd.Series, pd.DataFrame], close: Union[pd.Series, pd.DataFrame], window: int = 14) -> pd.Series:
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    atr_val = tr.rolling(window=window).mean()
    return atr_val

def atr_breakout_signal(close: Union[pd.Series, pd.DataFrame], high: Union[pd.Series, pd.DataFrame], low: Union[pd.Series, pd.DataFrame], window: int = 14, atr_mult: float = 1.5) -> pd.Series:
    atr_val = atr(high, low, close, window)
    breakout = close > (close.shift(1) + atr_mult * atr_val)
    breakdown = close < (close.shift(1) - atr_mult * atr_val)
    signal = pd.Series(0, index=close.index)
    signal[breakout] = 1
    signal[breakdown] = -1
    return signal

# Example usage (for test/demo):
if __name__ == "__main__":
    close = pd.Series([45, 46, 47, 48, 47, 46, 45, 44, 43, 44, 45, 46, 47, 48, 49])
    high = pd.Series([46, 47, 48, 49, 48, 47, 46, 45, 44, 45, 46, 47, 48, 49, 50])
    low = pd.Series([44, 45, 46, 47, 46, 45, 44, 43, 42, 43, 44, 45, 46, 47, 48])
    sig = atr_breakout_signal(close, high, low)
    print(sig)
