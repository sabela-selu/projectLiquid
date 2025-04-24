"""Meta-strategy: Ensemble/Voting/Stacking of multiple signal generators."""
import pandas as pd
from typing import List, Callable, Union

class MetaStrategy:
    def __init__(self, signal_generators: List[Callable[[pd.DataFrame], pd.Series]], voting: str = 'majority'):
        """
        signal_generators: list of callables that return a signal Series
        voting: 'majority', 'all', or 'any'
        """
        self.signal_generators = signal_generators
        self.voting = voting

    def generate(self, data: Union[pd.DataFrame, dict]) -> pd.Series:
        signals = [sg(data) for sg in self.signal_generators]
        signals_df = pd.concat(signals, axis=1)
        if self.voting == 'majority':
            return (signals_df.sum(axis=1) > 0).astype(int)
        elif self.voting == 'all':
            return (signals_df.min(axis=1) > 0).astype(int)
        elif self.voting == 'any':
            return (signals_df.max(axis=1) > 0).astype(int)
        else:
            raise ValueError(f"Unknown voting type: {self.voting}")

# Example usage (for test/demo):
if __name__ == "__main__":
    def dummy_signal1(df): return (df['a'] > 0).astype(int)
    def dummy_signal2(df): return (df['b'] > 0).astype(int)
    X = pd.DataFrame({'a': [1, -1, 1, -1], 'b': [1, 1, -1, -1]})
    meta = MetaStrategy([dummy_signal1, dummy_signal2], voting='majority')
    print(meta.generate(X))
