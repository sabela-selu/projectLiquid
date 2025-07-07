import pandas as pd
import matplotlib.pyplot as plt
from algotrade.strategies.rsi import rsi_strategy

def plot_rsi(df):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8), sharex=True)
    ax1.plot(df.index, df['close'], label='Close Price', color='black')
    ax1.set_ylabel('Price')
    ax2.plot(df.index, df['rsi'], label='RSI', color='purple')
    ax2.axhline(70, color='red', linestyle='--', label='Overbought')
    ax2.axhline(30, color='green', linestyle='--', label='Oversold')
    # Plot buy/sell signals
    buy_signals = df[df['signal'] == 1]
    sell_signals = df[df['signal'] == -1]
    ax1.scatter(buy_signals.index, buy_signals['close'], color='green', marker='^', s=80, label='Buy Signal')
    ax1.scatter(sell_signals.index, sell_signals['close'], color='red', marker='v', s=80, label='Sell Signal')
    ax1.legend()
    ax2.legend()
    plt.show()

def main():
    df = pd.read_csv(
        '/Users/user/Downloads/projectLiquid/algotrade/data/BTCUSD_1h_Binance.csv',
        parse_dates=['Open time'],
        index_col='Open time'
    )
    df = df.sort_index()
    df.columns = [c.lower() for c in df.columns]
    result = rsi_strategy(df)
    df = pd.concat([df, result], axis=1)
    print(df[['close', 'rsi', 'signal']].tail(20))
    plot_rsi(df)

if __name__ == '__main__':
    main()
