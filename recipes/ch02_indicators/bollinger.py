"""
Recipe: Calculate Bollinger Bands as per Cookbook Chapter 2.
"""
import pandas as pd

def calculate_bollinger(series: pd.Series, window: int = 20, num_std: float = 2.0):
    """Calculate Bollinger Bands (upper, middle, lower)."""
    middle = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower

if __name__ == "__main__":
    data = pd.Series([45.15, 46.23, 45.78, 46.10, 46.50, 47.00, 46.80, 47.20, 47.30, 47.10, 47.50, 47.90, 48.00, 48.20, 48.50, 48.80, 49.00, 49.20, 49.50, 49.80, 50.00, 50.20, 50.50, 50.80, 51.00, 51.20, 51.50])
    upper, middle, lower = calculate_bollinger(data)
    print("Upper Band:")
    print(upper)
    print("Middle Band:")
    print(middle)
    print("Lower Band:")
    print(lower)
