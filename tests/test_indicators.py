"""Unit tests for indicator functions in algotrade.signals."""
import pandas as pd
from algotrade.signals import ma, rsi, macd, bollinger

def test_sma():
    data = pd.Series([1, 2, 3, 4, 5])
    result = ma.sma(data, 3)
    expected = pd.Series([None, None, 2.0, 3.0, 4.0])
    pd.testing.assert_series_equal(result.reset_index(drop=True), expected, check_names=False)

def test_ema():
    data = pd.Series([1, 2, 3, 4, 5])
    result = ma.ema(data, 3)
    expected = pd.Series([1.0, 1.5, 2.25, 3.125, 4.0625])
    pd.testing.assert_series_equal(result.reset_index(drop=True), expected, check_names=False, rtol=1e-4)

def test_rsi():
    data = pd.Series([1, 2, 3, 2, 1, 2, 3, 4, 5, 4, 3, 2, 1, 2, 3])
    result = rsi.rsi(data, 3)
    # Just check that output is correct length and within 0-100
    assert len(result) == len(data)
    assert ((result.dropna() >= 0) & (result.dropna() <= 100)).all()

def test_macd():
    data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    macd_line, signal_line, hist = macd.macd(data)
    assert len(macd_line) == len(data)
    assert len(signal_line) == len(data)
    assert len(hist) == len(data)

def test_bollinger():
    data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    upper, middle, lower = bollinger.bollinger_bands(data, 3)
    assert len(upper) == len(data)
    assert len(middle) == len(data)
    assert len(lower) == len(data)
    # Check that upper >= middle >= lower where not NaN
    mask = ~upper.isna() & ~middle.isna() & ~lower.isna()
    assert (upper[mask] >= middle[mask]).all()
    assert (middle[mask] >= lower[mask]).all()
