"""Production-grade composite MA+RSI filter signal generator."""
import pandas as pd
from typing import Union
from algotrade.signals.ma import sma
from algotrade.signals.rsi import rsi

def composite_ma_rsi_signal(series: Union[pd.Series, pd.DataFrame], ma_window: int = 50, rsi_window: int = 14, rsi_thresh: float = 30) -> pd.Series:
    """+1 if price > MA and RSI < threshold, else 0."""
    ma_val = sma(series, ma_window)
    rsi_val = rsi(series, rsi_window)
    signal = ((series > ma_val) & (rsi_val < rsi_thresh)).astype(int)
    return signal

# Example usage (for test/demo):
if __name__ == "__main__":
    data = pd.Series(range(1, 100))
    sig = composite_ma_rsi_signal(data, 10, 5, 40)
    print(sig.tail())
