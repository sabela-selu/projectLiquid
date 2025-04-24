"""Production-grade Stochastic Oscillator signal generator."""
import pandas as pd
from typing import Union

def stochastic_k(close: Union[pd.Series, pd.DataFrame], low: Union[pd.Series, pd.DataFrame], high: Union[pd.Series, pd.DataFrame], window: int = 14) -> pd.Series:
    lowest_low = low.rolling(window=window).min()
    highest_high = high.rolling(window=window).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    return k

def stochastic_signal(close: Union[pd.Series, pd.DataFrame], low: Union[pd.Series, pd.DataFrame], high: Union[pd.Series, pd.DataFrame], window: int = 14, overbought: float = 80, oversold: float = 20) -> pd.Series:
    k = stochastic_k(close, low, high, window)
    signal = pd.Series(0, index=close.index)
    signal[k < oversold] = 1
    signal[k > overbought] = -1
    return signal

# Example usage (for test/demo):
if __name__ == "__main__":
    close = pd.Series([45, 46, 47, 48, 47, 46, 45, 44, 43, 44, 45, 46, 47, 48, 49])
    low = pd.Series([44, 45, 46, 47, 46, 45, 44, 43, 42, 43, 44, 45, 46, 47, 48])
    high = pd.Series([46, 47, 48, 49, 48, 47, 46, 45, 44, 45, 46, 47, 48, 49, 50])
    sig = stochastic_signal(close, low, high)
    print(sig)
