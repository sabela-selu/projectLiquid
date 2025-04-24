"""ML-based signal stub using scikit-learn classifier."""
import pandas as pd
from typing import Union, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

class MLSignalGenerator:
    def __init__(self, features: pd.DataFrame, target: pd.Series, model: Optional[object] = None):
        self.model = model or RandomForestClassifier(n_estimators=100, random_state=42)
        self.features = features
        self.target = target
        self.is_fitted = False

    def fit(self):
        X_train, X_test, y_train, y_test = train_test_split(self.features, self.target, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        self.is_fitted = True
        return self.model.score(X_test, y_test)

    def predict(self, features: pd.DataFrame) -> pd.Series:
        if not self.is_fitted:
            raise RuntimeError("Model not fitted!")
        return pd.Series(self.model.predict(features), index=features.index)

# Example usage (for test/demo):
if __name__ == "__main__":
    import numpy as np
    # Fake features: 100 samples, 3 features
    X = pd.DataFrame(np.random.randn(100, 3), columns=["f1", "f2", "f3"])
    y = pd.Series((X["f1"] + X["f2"] > 0).astype(int))
    ml_sig = MLSignalGenerator(X, y)
    acc = ml_sig.fit()
    print(f"Validation accuracy: {acc:.2f}")
    preds = ml_sig.predict(X)
    print(preds.head())
