"""Production-grade moving average crossover signal generator."""
import pandas as pd
from typing import Union
from algotrade.signals.ma import sma

def crossover_signal(series: Union[pd.Series, pd.DataFrame], fast: int = 50, slow: int = 200) -> pd.Series:
    """+1 (bull), -1 (bear), 0 (neutral) crossover signal."""
    fast_ma = sma(series, fast)
    slow_ma = sma(series, slow)
    signal = (fast_ma > slow_ma).astype(int) - (fast_ma < slow_ma).astype(int)
    return signal

# Example usage (for test/demo):
if __name__ == "__main__":
    data = pd.Series(range(1, 300))
    sig = crossover_signal(data, 5, 20)
    print(sig.tail())
