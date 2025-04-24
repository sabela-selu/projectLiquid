"""Volatility-adjusted (ATR-based) position sizing utility."""
import pandas as pd
from typing import Union
from algotrade.signals.atr_breakout import atr

def atr_position_size(equity: float, risk_per_trade: float, high: Union[pd.Series, pd.DataFrame], low: Union[pd.Series, pd.DataFrame], close: Union[pd.Series, pd.DataFrame], window: int = 14) -> pd.Series:
    """
    Calculate position size based on ATR volatility.
    equity: account equity in quote currency
    risk_per_trade: fraction of equity to risk (e.g., 0.01 for 1%)
    Returns: position size (units of asset)
    """
    atr_val = atr(high, low, close, window)
    dollar_risk_per_trade = equity * risk_per_trade
    # ATR is in price units; position size is dollar_risk / ATR
    position_size = dollar_risk_per_trade / atr_val
    return position_size

# Example usage (for test/demo):
if __name__ == "__main__":
    close = pd.Series([45, 46, 47, 48, 47, 46, 45, 44, 43, 44, 45, 46, 47, 48, 49])
    high = pd.Series([46, 47, 48, 49, 48, 47, 46, 45, 44, 45, 46, 47, 48, 49, 50])
    low = pd.Series([44, 45, 46, 47, 46, 45, 44, 43, 42, 43, 44, 45, 46, 47, 48])
    pos_size = atr_position_size(10000, 0.01, high, low, close)
    print(pos_size)
