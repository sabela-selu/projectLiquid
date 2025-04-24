"""
Recipe: RSI-based buy/sell signal as per Cookbook Chapter 3.
"""
import pandas as pd
from recipes.ch02_indicators.rsi import calculate_rsi

def generate_rsi_signal(series: pd.Series, window: int = 14, overbought: float = 70, oversold: float = 30) -> pd.Series:
    """+1 (buy), -1 (sell), 0 (hold) based on RSI thresholds."""
    rsi = calculate_rsi(series, window)
    signal = pd.Series(0, index=series.index)
    signal[rsi < oversold] = 1
    signal[rsi > overbought] = -1
    return signal

if __name__ == "__main__":
    data = pd.Series([45.15, 46.23, 45.78, 46.10, 46.50, 47.00, 46.80, 47.20, 47.30, 47.10, 47.50, 47.90, 48.00, 48.20, 48.50])
    sig = generate_rsi_signal(data, 5, 60, 40)
    print(sig)
