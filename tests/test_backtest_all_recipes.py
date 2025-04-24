"""
Integration test: Run BacktestEngine with all major recipe signals on BTC 4H data.
Validates that each strategy runs without error and produces reasonable stats.
"""
import pandas as pd
import numpy as np
import pytest
from algotrade.backtest.engine import BacktestEngine
from algotrade.signals import rsi_signal, macd_signal, bollinger_breakout, crossover, stochastic, atr_breakout, composite_ma_rsi

data_path = "algotrade/data/btc_4h_data_2018_to_2025.csv"

def load_data():
    df = pd.read_csv(data_path)
    # Standardize columns for signals
    df = df.rename(columns={
        'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume',
        'Open time': 'datetime'
    })
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')
    return df

def run_and_assert(engine: BacktestEngine, min_trades=5):
    results = engine.run()
    stats = engine.stats()
    # Basic checks
    assert isinstance(stats['total_return'], float)
    assert isinstance(stats['max_drawdown'], float)
    assert isinstance(stats['sharpe'], float)
    assert results['equity'].notna().all()
    # Should be at least min_trades (for non-trivial signals)
    assert (results['position'].abs().sum() > min_trades)
    return stats

def test_rsi_signal():
    df = load_data()
    engine = BacktestEngine(df, lambda d: rsi_signal.rsi_signal(d['close']))
    stats = run_and_assert(engine)
    print('RSI stats:', stats)

def test_macd_signal():
    df = load_data()
    engine = BacktestEngine(df, lambda d: macd_signal.macd_signal(d['close']))
    stats = run_and_assert(engine)
    print('MACD stats:', stats)

def test_bollinger_breakout_signal():
    df = load_data()
    engine = BacktestEngine(df, lambda d: bollinger_breakout.bollinger_breakout_signal(d['close']))
    stats = run_and_assert(engine)
    print('Bollinger stats:', stats)

def test_crossover_signal():
    df = load_data()
    engine = BacktestEngine(df, lambda d: crossover.crossover_signal(d['close']))
    stats = run_and_assert(engine)
    print('Crossover stats:', stats)

def test_stochastic_signal():
    df = load_data()
    engine = BacktestEngine(df, lambda d: stochastic.stochastic_signal(d['close'], d['low'], d['high']))
    stats = run_and_assert(engine)
    print('Stochastic stats:', stats)

def test_atr_breakout_signal():
    df = load_data()
    engine = BacktestEngine(df, lambda d: atr_breakout.atr_breakout_signal(d['close'], d['high'], d['low']))
    stats = run_and_assert(engine)
    print('ATR Breakout stats:', stats)

def test_composite_ma_rsi_signal():
    df = load_data()
    engine = BacktestEngine(df, lambda d: composite_ma_rsi.composite_ma_rsi_signal(d['close']))
    stats = run_and_assert(engine)
    print('Composite MA+RSI stats:', stats)
