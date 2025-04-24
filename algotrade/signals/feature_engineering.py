"""Feature engineering utilities for ML/DL signals."""
import pandas as pd
import numpy as np
from typing import List, Optional, Dict

class FeatureEngineer:
    def __init__(self, features: Optional[List[str]] = None, add_ta: bool = True, add_returns: bool = True, add_lags: int = 3):
        self.features = features
        self.add_ta = add_ta
        self.add_returns = add_returns
        self.add_lags = add_lags

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        # Add log returns
        if self.add_returns and 'close' in out.columns:
            out['log_return'] = (out['close'] / out['close'].shift(1)).apply(lambda x: np.log(x) if x > 0 else 0)
        # Add lags
        for lag in range(1, self.add_lags + 1):
            for col in out.columns:
                out[f'{col}_lag{lag}'] = out[col].shift(lag)
        # Add TA features
        if self.add_ta and 'close' in out.columns:
            out['sma_10'] = out['close'].rolling(10).mean()
            out['ema_10'] = out['close'].ewm(span=10, adjust=False).mean()
            out['rsi_14'] = self._rsi(out['close'], 14)
        # Select subset if specified
        if self.features:
            out = out[self.features]
        return out.dropna()

    @staticmethod
    def _rsi(series: pd.Series, window: int = 14) -> pd.Series:
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window, min_periods=window).mean()
        avg_loss = loss.rolling(window=window, min_periods=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

# Example usage (for test/demo):
if __name__ == "__main__":
    import numpy as np
    data = pd.DataFrame({
        'close': np.random.randn(100).cumsum() + 100,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 100,
        'low': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(100, 1000, 100)
    })
    fe = FeatureEngineer(add_ta=True, add_returns=True, add_lags=2)
    features = fe.transform(data)
    print(features.head())
