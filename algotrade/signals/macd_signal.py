"""Production-grade MACD-based buy/sell/hold signal generator."""
import pandas as pd
from typing import Union
from algotrade.signals.macd import macd

def macd_signal(series: Union[pd.Series, pd.DataFrame], fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    """+1 (bullish), -1 (bearish), 0 (neutral) based on MACD/Signal crossover."""
    macd_line, signal_line, _ = macd(series, fast, slow, signal)
    cross = (macd_line > signal_line).astype(int) - (macd_line < signal_line).astype(int)
    return cross

# Example usage (for test/demo):
if __name__ == "__main__":
    data = pd.Series([45.15, 46.23, 45.78, 46.10, 46.50, 47.00, 46.80, 47.20, 47.30, 47.10, 47.50, 47.90, 48.00, 48.20, 48.50, 48.80, 49.00, 49.20, 49.50, 49.80, 50.00, 50.20, 50.50, 50.80, 51.00, 51.20, 51.50])
    sig = macd_signal(data)
    print(sig)
