"""
Recipe: ATR (Average True Range) Volatility Breakout Signal as per Cookbook Chapter 3.
"""
import pandas as pd

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    return atr

def generate_atr_breakout_signal(close: pd.Series, high: pd.Series, low: pd.Series, window: int = 14, atr_mult: float = 1.5) -> pd.Series:
    atr = calculate_atr(high, low, close, window)
    breakout = close > (close.shift(1) + atr_mult * atr)
    breakdown = close < (close.shift(1) - atr_mult * atr)
    signal = pd.Series(0, index=close.index)
    signal[breakout] = 1
    signal[breakdown] = -1
    return signal

if __name__ == "__main__":
    close = pd.Series([45, 46, 47, 48, 47, 46, 45, 44, 43, 44, 45, 46, 47, 48, 49])
    high = pd.Series([46, 47, 48, 49, 48, 47, 46, 45, 44, 45, 46, 47, 48, 49, 50])
    low = pd.Series([44, 45, 46, 47, 46, 45, 44, 43, 42, 43, 44, 45, 46, 47, 48])
    sig = generate_atr_breakout_signal(close, high, low)
    print(sig)
