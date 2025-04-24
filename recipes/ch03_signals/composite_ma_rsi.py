"""
Recipe: Composite MA+RSI Filter Signal as per Cookbook Chapter 3.
"""
import pandas as pd
from recipes.ch02_indicators.sma_ema import calculate_sma
from recipes.ch02_indicators.rsi import calculate_rsi

def generate_composite_ma_rsi_signal(series: pd.Series, ma_window: int = 50, rsi_window: int = 14, rsi_thresh: float = 30) -> pd.Series:
    """+1 if price > MA and RSI < threshold, else 0."""
    ma = calculate_sma(series, ma_window)
    rsi = calculate_rsi(series, rsi_window)
    signal = ((series > ma) & (rsi < rsi_thresh)).astype(int)
    return signal

if __name__ == "__main__":
    data = pd.Series(range(1, 100))
    sig = generate_composite_ma_rsi_signal(data, 10, 5, 40)
    print(sig.tail())
