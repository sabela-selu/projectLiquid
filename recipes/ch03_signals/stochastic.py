"""
Recipe: Stochastic Oscillator Signal as per Cookbook Chapter 3.
"""
import pandas as pd

def calculate_stochastic_k(close: pd.Series, low: pd.Series, high: pd.Series, window: int = 14) -> pd.Series:
    lowest_low = low.rolling(window=window).min()
    highest_high = high.rolling(window=window).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    return k

def generate_stochastic_signal(close: pd.Series, low: pd.Series, high: pd.Series, window: int = 14, overbought: float = 80, oversold: float = 20) -> pd.Series:
    k = calculate_stochastic_k(close, low, high, window)
    signal = pd.Series(0, index=close.index)
    signal[k < oversold] = 1
    signal[k > overbought] = -1
    return signal

if __name__ == "__main__":
    close = pd.Series([45, 46, 47, 48, 47, 46, 45, 44, 43, 44, 45, 46, 47, 48, 49])
    low = pd.Series([44, 45, 46, 47, 46, 45, 44, 43, 42, 43, 44, 45, 46, 47, 48])
    high = pd.Series([46, 47, 48, 49, 48, 47, 46, 45, 44, 45, 46, 47, 48, 49, 50])
    sig = generate_stochastic_signal(close, low, high)
    print(sig)
