import pandas as pd
from algotrade.strategies.bos_fvg import bos_fvg_backtest

def main():
    # Load 4h BTC data
    df = pd.read_csv(
        "/Users/user/Downloads/btc_4h_data_2018_to_2025.csv",
        parse_dates=["Open time"],
        index_col="Open time"
    )
    # Ensure index is sorted and in datetime
    df = df.sort_index()
    df.columns = [c.lower() for c in df.columns]
    # Run BOS+FVG backtest
    trades = bos_fvg_backtest(df)
    print(trades)
    print(f"Total trades: {len(trades)}")
    if not trades.empty:
        print(f"First 5 trades:\n{trades.head()}")
        print(f"Last 5 trades:\n{trades.tail()}")

if __name__ == "__main__":
    main()
