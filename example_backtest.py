"""
Example Backtest Script for BOS+FVG Strategy
-------------------------------------------
This script demonstrates how to backtest the BOS+FVG strategy
using historical data.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from strategies.bos_fvg_strategy import BOSFVGStrategy
from backtester import run_backtest

# Configuration
SYMBOL = 'BTC-USD'
TIMEFRAME = '1d'
START_DATE = '2022-01-01'
END_DATE = '2023-01-01'
INITIAL_CAPITAL = 10000.0
COMMISSION = 0.001  # 0.1% commission per trade

def download_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Download historical price data.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC-USD')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        
    Returns:
        pd.DataFrame: OHLCV data
    """
    print(f"Downloading {symbol} data from {start_date} to {end_date}...")
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)
    
    # Rename columns to match our convention
    data = data.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Ensure the index is a DatetimeIndex
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)
    
    return data

def run_strategy_backtest(data: pd.DataFrame, symbol: str, 
                         initial_capital: float, commission: float) -> dict:
    """
    Run a backtest for the BOS+FVG strategy.
    
    Args:
        data: OHLCV data
        symbol: Trading pair symbol
        initial_capital: Starting capital
        commission: Trading commission as a fraction
        
    Returns:
        dict: Backtest results
    """
    # Initialize strategy
    strategy = BOSFVGStrategy(
        symbol=symbol,
        params={
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'atr_period': 14,
            'risk_per_trade': 1.0,  # 1% risk per trade
            'reward_ratio': 2.0,    # 2:1 reward/risk ratio
            'bos_lookback': 20,
            'volume_ma_period': 20,
            'min_volume_ratio': 1.5
        }
    )
    
    # Run backtest
    result = run_backtest(
        strategy=strategy,
        data=data,
        initial_capital=initial_capital,
        commission=commission,
        show_progress=True
    )
    
    return result

def plot_equity_curve(equity_curve: pd.Series, title: str = 'Equity Curve') -> None:
    """Plot the equity curve."""
    plt.figure(figsize=(12, 6))
    equity_curve.plot(title=title, grid=True)
    plt.xlabel('Date')
    plt.ylabel('Equity ($)')
    plt.tight_layout()
    plt.show()

def analyze_trades(trades: list) -> None:
    """Analyze and print trade statistics."""
    if not trades:
        print("No trades were executed.")
        return
    
    # Convert trades to DataFrame
    trades_df = pd.DataFrame([{
        'entry_time': t.entry_time,
        'exit_time': t.exit_time,
        'direction': t.direction,
        'entry_price': t.entry_price,
        'exit_price': t.exit_price,
        'pnl': t.pnl,
        'pnl_pct': t.pnl_pct,
        'exit_reason': t.exit_reason,
        'duration': (t.exit_time - t.entry_time).total_seconds() / 3600  # in hours
    } for t in trades])
    
    # Calculate metrics
    num_trades = len(trades_df)
    winning_trades = trades_df[trades_df['pnl'] > 0]
    losing_trades = trades_df[trades_df['pnl'] <= 0]
    win_rate = len(winning_trades) / num_trades * 100
    
    avg_win = winning_trades['pnl'].mean() if not winning_trades.empty else 0
    avg_loss = losing_trades['pnl'].mean() if not losing_trades.empty else 0
    profit_factor = -avg_win / avg_loss if avg_loss != 0 else float('inf')
    
    # Print summary
    print("\n=== Trade Analysis ===")
    print(f"Total Trades: {num_trades}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Average Win: ${avg_win:.2f}")
    print(f"Average Loss: ${avg_loss:.2f}")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Total P&L: ${trades_df['pnl'].sum():.2f}")
    print(f"Average Trade Duration: {trades_df['duration'].mean():.1f} hours")
    
    # Plot P&L distribution
    plt.figure(figsize=(10, 5))
    plt.hist(trades_df['pnl'], bins=30, edgecolor='black')
    plt.title('P&L Distribution per Trade')
    plt.xlabel('P&L ($)')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def main():
    # Download data
    data = download_data(SYMBOL, START_DATE, END_DATE)
    
    # Run backtest
    result = run_strategy_backtest(
        data=data,
        symbol=SYMBOL,
        initial_capital=INITIAL_CAPITAL,
        commission=COMMISSION
    )
    
    # Plot equity curve
    plot_equity_curve(result.equity_curve, f'{SYMBOL} BOS+FVG Strategy Equity Curve')
    
    # Analyze trades
    analyze_trades(result.trades)
    
    # Print metrics
    print("\n=== Performance Metrics ===")
    for metric, value in result.metrics.items():
        if isinstance(value, float):
            print(f"{metric.replace('_', ' ').title()}: {value:.2f}")
        else:
            print(f"{metric.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    main()
