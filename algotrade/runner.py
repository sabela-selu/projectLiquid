"""Strategy runners for backtest and live trading modes."""
from pathlib import Path
from typing import Optional

def run_backtest(config: Path):
    """
    Run a back-test based on the YAML config file.
    Config should specify: data source, signal type, position sizing, fees, etc.
    """
    import yaml
    import pandas as pd
    from algotrade.backtest.engine import BacktestEngine
    from algotrade.signals import feature_engineering, ma, rsi, macd, bollinger, bollinger_breakout, stochastic, atr_breakout, composite_ma_rsi, ml_signal, dl_signal, meta_strategy
    from algotrade.portfolio import volatility_position_sizing

    with open(config, 'r') as f:
        cfg = yaml.safe_load(f)

    # Data loading (demo: CSV, extend for Yahoo/Binance etc.)
    if cfg['data']['source'] == 'csv':
        # Try to use 'date' column, else fallback to 'Open time' (Binance format)
        import pandas as pd
        cols = pd.read_csv(cfg['data']['path'], nrows=0).columns
        if 'date' in cols:
            df = pd.read_csv(cfg['data']['path'], parse_dates=['date'], index_col='date')
        elif 'Open time' in cols:
            df = pd.read_csv(cfg['data']['path'], parse_dates=['Open time'], index_col='Open time')
            df.index.name = 'date'  # For downstream compatibility
            df.columns = [c.lower() for c in df.columns]  # Standardize columns to lowercase
        else:
            raise ValueError("CSV must have 'date' or 'Open time' as a timestamp column!")
    else:
        raise NotImplementedError('Only CSV data loading implemented in demo')

    # Feature engineering
    if cfg.get('features'):
        fe = feature_engineering.FeatureEngineer(**cfg['features'])
        df = fe.transform(df)

    # Signal selection
    signal_map = {
        'sma_crossover': lambda df: ma.sma(df['close'], cfg['signal']['window']).diff().apply(lambda x: 1 if x>0 else -1 if x<0 else 0),
        'rsi': lambda df: rsi.rsi(df['close'], cfg['signal']['window']),
        'macd': lambda df: macd.macd(df['close'])[0],
        'bollinger_breakout': lambda df: bollinger_breakout.bollinger_breakout_signal(df['close']),
        'stochastic': lambda df: stochastic.stochastic_signal(df['close'], df['low'], df['high']),
        'atr_breakout': lambda df: atr_breakout.atr_breakout_signal(df['close'], df['high'], df['low']),
        'composite_ma_rsi': lambda df: composite_ma_rsi.composite_ma_rsi_signal(df['close']),
        'ml': lambda df: ml_signal.MLSignalGenerator(df[cfg['signal']['features']], df[cfg['signal']['target']]).fit() or ml_signal.MLSignalGenerator(df[cfg['signal']['features']], df[cfg['signal']['target']]).predict(df[cfg['signal']['features']]),
        'dl': lambda df: dl_signal.DLSignalGenerator(input_shape=(10, len(cfg['signal']['features']))),
        # Add more as needed
    }
    signal_func = signal_map[cfg['signal']['type']]

    # Position sizing
    if 'position_sizer' in cfg:
        sizer_map = {
            'atr': lambda df: volatility_position_sizing.atr_position_size(
                cfg['position_sizer']['equity'],
                cfg['position_sizer']['risk_per_trade'],
                df['high'], df['low'], df['close']),
            # Add more as needed
        }
        sizer_func = sizer_map[cfg['position_sizer']['type']]
    else:
        sizer_func = None

    # Backtest
    engine = BacktestEngine(df, signal_func, sizer_func, fee=cfg.get('fee', 0.0))
    results = engine.run(cfg.get('initial_equity', 10000.0))
    stats = engine.stats()

    # Experiment logging (demo: print, extend for file/MLflow)
    print('Backtest stats:', stats)
    print('Results tail:')
    print(results.tail())
    # Optionally save results
    if cfg.get('output'):
        results.to_csv(cfg['output'])

def run_live(config: Path, broker: Optional[str] = None):
    print(f"[TODO] Live trading not yet implemented. Would run live trading using {config} on broker {broker}")
