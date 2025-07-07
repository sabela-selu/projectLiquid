import pandas as pd
from algotrade.strategies.bos_fvg import bos_fvg_backtest
import matplotlib.pyplot as plt

def plot_bos_fvg(df, trades):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(df.index, df['close'], label='Close', color='black', lw=1)
    # Plot trades
    for _, row in trades.iterrows():
        if row['direction'] == 1:
            ax.scatter(row['entry_time'], row['entry_price'], color='green', marker='^', s=100, label='Long Entry')
            ax.scatter(row['exit_time'], row['exit_price'], color='blue', marker='o', s=80, label='Long Exit')
        else:
            ax.scatter(row['entry_time'], row['entry_price'], color='red', marker='v', s=100, label='Short Entry')
            ax.scatter(row['exit_time'], row['exit_price'], color='orange', marker='o', s=80, label='Short Exit')
    ax.set_title('BTCUSD 1H BOS+FVG Trades')
    ax.set_ylabel('Price')
    ax.legend(loc='best')
    plt.show()

def main():
    df = pd.read_csv(
        '/Users/user/Downloads/projectLiquid/algotrade/data/BTCUSD_1h_Binance.csv',
        parse_dates=['Open time'],
        index_col='Open time'
    )
    df = df.sort_index()
    df.columns = [c.lower() for c in df.columns]
    trades = bos_fvg_backtest(df)
    print(trades)
    print(f"Total trades: {len(trades)}")
    if not trades.empty:
        print(f"First 5 trades:\n{trades.head()}")
        print(f"Last 5 trades:\n{trades.tail()}")
        plot_bos_fvg(df, trades)

if __name__ == '__main__':
    main()
