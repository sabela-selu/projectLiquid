"""
Unit tests for signal generators and strategy logic in algotrade.signals and recipes/ch03_signals.
Covers: RSI signal, MACD signal, ATR breakout, Stochastic, Crossover, Bollinger breakout, Composite MA+RSI, ML, DL, MetaStrategy.
"""
import pandas as pd
import numpy as np
import pytest
from algotrade.signals import (
    rsi_signal, macd_signal, atr_breakout, stochastic, crossover, bollinger_breakout, composite_ma_rsi, ml_signal, dl_signal, meta_strategy
)

def test_rsi_signal():
    data = pd.Series([30, 40, 50, 60, 70, 80, 90, 80, 70, 60, 50, 40, 30])
    signal = rsi_signal.rsi_signal(data, window=3, overbought=70, oversold=30)
    assert set(signal.unique()).issubset({-1, 0, 1})
    assert len(signal) == len(data)

def test_macd_signal():
    data = pd.Series(np.linspace(1, 100, 100))
    signal = macd_signal.macd_signal(data)
    assert set(signal.unique()).issubset({-1, 0, 1})
    assert len(signal) == len(data)

def test_atr_breakout_signal():
    close = pd.Series(np.linspace(100, 200, 100))
    high = close + 2
    low = close - 2
    signal = atr_breakout.atr_breakout_signal(close, high, low)
    assert set(signal.unique()).issubset({-1, 0, 1})
    assert len(signal) == len(close)

def test_stochastic_signal():
    close = pd.Series([45, 46, 47, 48, 47, 46, 45, 44, 43, 44, 45, 46, 47, 48, 49])
    low = pd.Series([44, 45, 46, 47, 46, 45, 44, 43, 42, 43, 44, 45, 46, 47, 48])
    high = pd.Series([46, 47, 48, 49, 48, 47, 46, 45, 44, 45, 46, 47, 48, 49, 50])
    signal = stochastic.stochastic_signal(close, low, high)
    assert set(signal.unique()).issubset({-1, 0, 1})
    assert len(signal) == len(close)

def test_crossover_signal():
    data = pd.Series(np.arange(1, 300))
    signal = crossover.crossover_signal(data, fast=5, slow=20)
    assert set(signal.unique()).issubset({-1, 0, 1})
    assert len(signal) == len(data)

def test_bollinger_breakout_signal():
    data = pd.Series(np.random.randn(100).cumsum() + 100)
    signal = bollinger_breakout.bollinger_breakout_signal(data)
    assert set(signal.unique()).issubset({-1, 0, 1})
    assert len(signal) == len(data)

def test_composite_ma_rsi_signal():
    data = pd.Series(np.random.randn(100).cumsum() + 100)
    signal = composite_ma_rsi.composite_ma_rsi_signal(data)
    assert set(signal.unique()).issubset({0, 1})
    assert len(signal) == len(data)

def test_ml_signal_generator():
    X = pd.DataFrame(np.random.randn(100, 3), columns=["f1", "f2", "f3"])
    y = pd.Series((X["f1"] + X["f2"] > 0).astype(int))
    ml_sig = ml_signal.MLSignalGenerator(X, y)
    acc = ml_sig.fit()
    assert 0 <= acc <= 1
    preds = ml_sig.predict(X)
    assert set(preds.unique()).issubset({0, 1})
    assert len(preds) == len(X)

def test_dl_signal_generator():
    try:
        X = np.random.randn(20, 5, 2)
        y = (X.mean(axis=(1,2)) > 0).astype(int)
        dl_sig = dl_signal.DLSignalGenerator(input_shape=(5, 2))
        dl_sig.fit(X, y, epochs=1)
        preds = dl_sig.predict(X)
        assert set(preds).issubset({0, 1})
        assert len(preds) == len(X)
    except ImportError:
        pytest.skip("TensorFlow/Keras not installed, skipping DL test.")

def test_meta_strategy():
    # Dummy signals: alternating +1/-1
    df = pd.DataFrame({'a': [1, -1, 1, -1], 'b': [1, 1, -1, -1]})
    def s1(d): return d['a']
    def s2(d): return d['b']
    meta = meta_strategy.MetaStrategy([s1, s2], voting='majority')
    out = meta.generate(df)
    assert set(out.unique()).issubset({0, 1})
    assert len(out) == len(df)
