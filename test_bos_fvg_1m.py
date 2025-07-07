import pandas as pd
from algotrade.strategies.bos_fvg import bos_fvg_backtest
import matplotlib.pyplot as plt

def plot_bos_fvg(df, trades, session_highs=None, session_lows=None):
    fig, ax = plt.subplots(figsize=(18, 8))
    ax.plot(df.index, df['close'], label='Close', color='black', lw=0.7)
    if session_highs is not None:
        ax.plot(session_highs.index, session_highs, label='Session High', color='green', lw=1, alpha=0.6)
    if session_lows is not None:
        ax.plot(session_lows.index, session_lows, label='Session Low', color='red', lw=1, alpha=0.6)
    for _, row in trades.iterrows():
        if row['direction'] == 1:
            ax.scatter(row['entry_time'], row['entry_price'], color='lime', marker='^', s=80, label='Long Entry')
            ax.scatter(row['exit_time'], row['exit_price'], color='blue', marker='o', s=60, label='Long Exit')
        else:
            ax.scatter(row['entry_time'], row['entry_price'], color='salmon', marker='v', s=80, label='Short Entry')
            ax.scatter(row['exit_time'], row['exit_price'], color='orange', marker='o', s=60, label='Short Exit')
    ax.set_title('BTCUSD 1-Minute BOS+FVG Trades')
    ax.set_ylabel('Price')
    ax.legend(loc='best')
    plt.tight_layout()
    plt.show()

def main():
    df = pd.read_csv(
        '/Users/user/Downloads/projectLiquid/algotrade/data/btcusd_1-min_data.csv',
        parse_dates=['datetime'],
        index_col='datetime'
    )
    df = df.sort_index()
    df.columns = [c.lower() for c in df.columns]
    # Choose BOS reference mode: 'session' or 'rolling'
    mode = 'session'  # Change to 'rolling' for rolling window
    session_start = "04:00"
    session_end = "09:30"
    print(f"Using BOS+FVG mode: {mode}")
    from algotrade.strategies.bos_fvg import bos_fvg_signal
    signal = bos_fvg_signal(
        df,
        lookback=1440,
        lookahead=3,
        min_break_pct=0.001,
        mode=mode,
        session_start=session_start,
        session_end=session_end
    )
    print(f"Signal value counts:\n{signal.value_counts()}")
    # Optionally, call your backtest runner if you want trade statistics
    try:
        trades = bos_fvg_backtest(df)
        # Filter out any trades with NaT or non-Timestamp entry_time or exit_time
        if not trades.empty:
            trades = trades[trades['entry_time'].apply(lambda x: isinstance(x, pd.Timestamp) and not pd.isna(x))]
            trades = trades[trades['exit_time'].apply(lambda x: isinstance(x, pd.Timestamp) and not pd.isna(x))]
            trades = trades.reset_index(drop=True)
        print(trades)
        print(f"Total trades: {len(trades)}")
        if not trades.empty:
            print(f"First 5 trades:\n{trades.head()}")
            print(f"Last 5 trades:\n{trades.tail()}")
            # Calculate trade returns
            trades['return'] = (trades['exit_price'] - trades['entry_price']) * trades['direction'] / trades['entry_price']
            win_rate = (trades['return'] > 0).mean()
            avg_return = trades['return'].mean()
            print(f"Win rate: {win_rate:.2%}")
            print(f"Average return per trade: {avg_return:.4f}")
            # Try to print drawdown from BacktestEngine if possible
            try:
                from algotrade.backtest.engine import BacktestEngine
                # Only use trades with valid entry_time for reindexing
                valid_trades = trades[trades['entry_time'].apply(lambda x: isinstance(x, pd.Timestamp) and not pd.isna(x))]
                if valid_trades['entry_time'].isnull().any() or valid_trades.empty:
                    print("Skipping BacktestEngine stats: trades have invalid or missing entry_time.")
                else:
                    engine = BacktestEngine(df, lambda d: valid_trades.set_index('entry_time')['direction'].reindex(d.index, fill_value=0), fee=0.0)
                    engine.run()
                    stats = engine.stats()
                    print(f"Max drawdown: {stats.get('max_drawdown', 'N/A')}")
            except Exception as e:
                print(f"Drawdown calculation error: {e}")
            plot_bos_fvg(df, trades)
    except Exception as e:
        print(f"Backtest runner error: {e}")

if __name__ == '__main__':
    main()
