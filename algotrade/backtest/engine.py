"""Backtesting engine: integrates signal modules, feature engineering, and strategy logic."""
import pandas as pd
from typing import Callable, Dict, Any, Optional

class BacktestEngine:
    def __init__(self, data: pd.DataFrame, signal_func: Callable, position_sizer: Optional[Callable] = None, fee: float = 0.0):
        """
        data: DataFrame with OHLCV (and any required features)
        signal_func: function returning signal Series (+1/-1/0)
        position_sizer: function returning position size Series (optional)
        fee: per-trade commission/slippage (as decimal, e.g., 0.001)
        """
        self.data = data.copy()
        self.signal_func = signal_func
        self.position_sizer = position_sizer
        self.fee = fee
        self.results = None

    def run(self, initial_equity: float = 10000.0, risk_per_trade: float = 0.01) -> pd.DataFrame:
        df = self.data.copy()
        signals = self.signal_func(df)
        df['signal'] = signals
        df['position'] = df['signal'].shift(1).fillna(0)
        if self.position_sizer:
            df['size'] = self.position_sizer(df)
        else:
            df['size'] = 1
        df['returns'] = df['close'].pct_change().fillna(0)
        df['strategy_return'] = df['position'] * df['returns'] * df['size']
        df['strategy_return'] -= abs(df['position'].diff().fillna(0)) * self.fee
        df['equity'] = (1 + df['strategy_return']).cumprod() * initial_equity
        self.results = df
        return df

    def stats(self) -> Dict[str, Any]:
        if self.results is None:
            raise RuntimeError("Run the backtest first!")
        total_return = self.results['equity'].iloc[-1] / self.results['equity'].iloc[0] - 1
        max_drawdown = ((self.results['equity'].cummax() - self.results['equity']) / self.results['equity'].cummax()).max()
        sharpe = self.results['strategy_return'].mean() / self.results['strategy_return'].std() * (252 ** 0.5)
        return {
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'sharpe': sharpe,
            'final_equity': self.results['equity'].iloc[-1]
        }

# Example usage (for test/demo):
if __name__ == "__main__":
    import numpy as np
    # Fake OHLCV data
    df = pd.DataFrame({
        'close': np.random.randn(100).cumsum() + 100,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 100,
        'low': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(100, 1000, 100)
    })
    def dummy_signal(df):
        return (df['close'] > df['close'].rolling(5).mean()).astype(int)
    engine = BacktestEngine(df, dummy_signal, fee=0.001)
    results = engine.run()
    print(engine.stats())
    print(results.tail())
