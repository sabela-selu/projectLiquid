"""
Recipe: Moving Average Crossover Signal (e.g., SMA50 vs SMA200) as per Cookbook Chapter 3.
"""
import pandas as pd
from recipes.ch02_indicators.sma_ema import calculate_sma

def generate_crossover_signal(series: pd.Series, fast: int = 50, slow: int = 200) -> pd.Series:
    """Generate +1 (bull), -1 (bear), 0 (neutral) crossover signal."""
    fast_ma = calculate_sma(series, fast)
    slow_ma = calculate_sma(series, slow)
    signal = (fast_ma > slow_ma).astype(int) - (fast_ma < slow_ma).astype(int)
    return signal

if __name__ == "__main__":
    data = pd.Series(range(1, 300))
    sig = generate_crossover_signal(data, 5, 20)
    print(sig.tail())
