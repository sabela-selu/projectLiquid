"""Production-grade RSI-based buy/sell/hold signal generator."""
import pandas as pd
from typing import Union
from algotrade.signals.rsi import rsi

def rsi_signal(series: Union[pd.Series, pd.DataFrame], window: int = 14, overbought: float = 70, oversold: float = 30) -> pd.Series:
    """+1 (buy), -1 (sell), 0 (hold) based on RSI thresholds."""
    rsi_vals = rsi(series, window)
    signal = pd.Series(0, index=series.index)
    signal[rsi_vals < oversold] = 1
    signal[rsi_vals > overbought] = -1
    return signal

# Example usage (for test/demo):
if __name__ == "__main__":
    data = pd.Series([45.15, 46.23, 45.78, 46.10, 46.50, 47.00, 46.80, 47.20, 47.30, 47.10, 47.50, 47.90, 48.00, 48.20, 48.50])
    sig = rsi_signal(data, 5, 60, 40)
    print(sig)
