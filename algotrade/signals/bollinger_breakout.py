"""Production-grade Bollinger Band breakout signal generator."""
import pandas as pd
from typing import Union
from algotrade.signals.bollinger import bollinger_bands

def bollinger_breakout_signal(series: Union[pd.Series, pd.DataFrame], window: int = 20, num_std: float = 2.0) -> pd.Series:
    """+1 (breakout above upper), -1 (breakdown below lower), 0 (neutral)."""
    upper, middle, lower = bollinger_bands(series, window, num_std)
    signal = pd.Series(0, index=series.index)
    signal[series > upper] = 1
    signal[series < lower] = -1
    return signal

# Example usage (for test/demo):
if __name__ == "__main__":
    data = pd.Series([45.15, 46.23, 45.78, 46.10, 46.50, 47.00, 46.80, 47.20, 47.30, 47.10, 47.50, 47.90, 48.00, 48.20, 48.50, 48.80, 49.00, 49.20, 49.50, 49.80, 50.00, 50.20, 50.50, 50.80, 51.00, 51.20, 51.50])
    sig = bollinger_breakout_signal(data)
    print(sig)
