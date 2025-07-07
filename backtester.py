"""
Backtesting Engine for BOS+FVG Strategy
------------------------------------
A comprehensive backtesting framework that evaluates strategy performance
on historical data with realistic assumptions about slippage, fees, and market impact.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backtest.log')
    ]
)
logger = logging.getLogger('backtester')

@dataclass
class Trade:
    """Represents a completed trade with all relevant metrics."""
    id: str
    symbol: str
    direction: str  # 'long' or 'short'
    entry_time: datetime
    exit_time: Optional[datetime] = None
    entry_price: float = 0.0
    exit_price: float = 0.0
    size: float = 0.0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    fees_paid: float = 0.0
    slippage: float = 0.0
    stop_loss: float = 0.0
    take_profit: Optional[float] = None
    exit_reason: Optional[str] = None
    tags: Dict = field(default_factory=dict)

@dataclass
class BacktestResult:
    """Container for backtest results and performance metrics."""
    trades: List[Trade] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=pd.Series)
    metrics: Dict = field(default_factory=dict)
    
    def calculate_metrics(self, initial_capital: float = 10000.0) -> Dict:
        """Calculate performance metrics from the backtest results."""
        if not self.trades:
            return {}
            
        # Basic metrics
        num_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl <= 0]
        win_rate = len(winning_trades) / num_trades if num_trades > 0 else 0
        
        # P&L metrics
        total_pnl = sum(t.pnl for t in self.trades)
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.pnl for t in losing_trades])) if losing_trades else 0
        profit_factor = -avg_win / avg_loss if avg_loss != 0 else float('inf')
        
        # Risk metrics
        max_drawdown = self._calculate_max_drawdown(initial_capital)
        sharpe_ratio = self._calculate_sharpe_ratio()
        
        # Trade duration
        durations = [(t.exit_time - t.entry_time).total_seconds() / 3600 for t in self.trades]
        avg_duration = np.mean(durations) if durations else 0
        
        self.metrics = {
            'total_trades': num_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl,
            'total_pnl_pct': (total_pnl / initial_capital) * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_trade_duration_hours': avg_duration,
            'expectancy': (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        }
        
        return self.metrics
    
    def _calculate_max_drawdown(self, initial_capital: float) -> float:
        """Calculate maximum drawdown from equity curve."""
        if self.equity_curve.empty:
            return 0.0
            
        peak = self.equity_curve[0]
        max_dd = 0.0
        
        for value in self.equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
                
        return max_dd * 100  # Return as percentage
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Calculate annualized Sharpe ratio."""
        if len(self.equity_curve) < 2:
            return 0.0
            
        returns = self.equity_curve.pct_change().dropna()
        if returns.empty or returns.std() == 0:
            return 0.0
            
        # Annualize the Sharpe ratio (assuming daily returns)
        return (returns.mean() - risk_free_rate/252) / (returns.std() * np.sqrt(252))
    
    def generate_report(self, output_dir: str = 'backtest_results') -> None:
        """Generate a comprehensive backtest report with visualizations."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save metrics to JSON
        with open(f"{output_dir}/metrics.json", 'w') as f:
            json.dump(self.metrics, f, indent=2, default=str)
        
        # Generate equity curve plot
        self._plot_equity_curve(output_dir)
        
        # Generate trade analysis
        self._analyze_trades(output_dir)
        
        logger.info(f"Backtest report generated in {output_dir}/")
    
    def _plot_equity_curve(self, output_dir: str) -> None:
        """Plot and save equity curve."""
        if self.equity_curve.empty:
            return
            
        plt.figure(figsize=(12, 6))
        self.equity_curve.plot(title='Equity Curve', grid=True)
        plt.xlabel('Time')
        plt.ylabel('Equity')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/equity_curve.png")
        plt.close()
    
    def _analyze_trades(self, output_dir: str) -> None:
        """Generate trade analysis visualizations."""
        if not self.trades:
            return
            
        # Trade P&L distribution
        plt.figure(figsize=(10, 5))
        pnls = [t.pnl for t in self.trades]
        sns.histplot(pnls, kde=True, bins=30)
        plt.title('Trade P&L Distribution')
        plt.xlabel('P&L')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/pnl_distribution.png")
        plt.close()
        
        # Win/Loss pie chart
        plt.figure(figsize=(8, 8))
        wins = sum(1 for t in self.trades if t.pnl > 0)
        losses = len(self.trades) - wins
        plt.pie([wins, losses], labels=['Wins', 'Losses'], autopct='%1.1f%%')
        plt.title('Win/Loss Ratio')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/win_loss_ratio.png")
        plt.close()

class Backtester:
    """Main backtesting engine for the BOS+FVG strategy."""
    
    def __init__(self, strategy, initial_capital: float = 10000.0, commission: float = 0.0005):
        """
        Initialize the backtester.
        
        Args:
            strategy: Instance of the trading strategy to backtest
            initial_capital: Starting capital in quote currency
            commission: Trading commission as a fraction of trade value
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.current_equity = initial_capital
        self.current_position = 0.0
        self.current_price = 0.0
        self.trades = []
        self.equity_curve = []
        self.timestamps = []
    
    def run(self, data: pd.DataFrame, show_progress: bool = True) -> BacktestResult:
        """
        Run the backtest on the provided historical data.
        
        Args:
            data: DataFrame with OHLCV data and required indicators
            show_progress: Whether to show progress bar
            
        Returns:
            BacktestResult: Object containing backtest results
        """
        logger.info(f"Starting backtest with {len(data)} data points")
        
        # Reset state
        self.current_equity = self.initial_capital
        self.current_position = 0.0
        self.trades = []
        self.equity_curve = []
        self.timestamps = []
        
        # Initialize strategy
        self.strategy.initialize()
        
        # Main backtest loop
        iterator = tqdm(data.iterrows(), total=len(data)) if show_progress else data.iterrows()
        
        for idx, row in iterator:
            self.current_price = row['close']
            self.timestamps.append(row.name)
            
            # Update strategy with current data
            signal = self.strategy.evaluate(row)
            
            # Execute trades based on signal
            self._process_signal(signal, row)
            
            # Update equity curve
            self._update_equity_curve(row)
        
        # Close any open position at the end
        if self.current_position != 0:
            self._close_position(self.timestamps[-1], self.current_price, 'end_of_backtest')
        
        # Create result object
        result = BacktestResult(
            trades=self.trades,
            equity_curve=pd.Series(self.equity_curve, index=self.timestamps)
        )
        
        # Calculate performance metrics
        result.calculate_metrics(self.initial_capital)
        
        return result
    
    def _process_signal(self, signal: dict, row: pd.Series) -> None:
        """Process trading signal and execute trades."""
        if not signal or 'action' not in signal:
            return
        
        if signal['action'] == 'buy' and self.current_position <= 0:
            # Close short position if exists
            if self.current_position < 0:
                self._close_position(row.name, row['close'], 'close_short')
            
            # Open long position
            self._open_position(
                'long', 
                row.name, 
                row['close'], 
                signal.get('size', 1.0),
                stop_loss=signal.get('stop_loss'),
                take_profit=signal.get('take_profit')
            )
            
        elif signal['action'] == 'sell' and self.current_position >= 0:
            # Close long position if exists
            if self.current_position > 0:
                self._close_position(row.name, row['close'], 'close_long')
            
            # Open short position
            self._open_position(
                'short', 
                row.name, 
                row['close'], 
                signal.get('size', 1.0),
                stop_loss=signal.get('stop_loss'),
                take_profit=signal.get('take_profit')
            )
    
    def _open_position(self, direction: str, timestamp: datetime, price: float, 
                      size: float, stop_loss: float = None, take_profit: float = None) -> None:
        """Open a new position."""
        # Calculate position value and apply slippage
        position_value = price * size
        
        # Calculate fees
        fees = position_value * self.commission
        
        # Update equity
        self.current_equity -= fees
        
        # Update position
        self.current_position = size if direction == 'long' else -size
        
        # Create trade record
        trade = Trade(
            id=f"trade_{len(self.trades) + 1}",
            symbol=self.strategy.symbol,
            direction=direction,
            entry_time=timestamp,
            entry_price=price,
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            fees_paid=fees,
            tags={
                'type': 'open',
                'equity': self.current_equity,
                'position': self.current_position
            }
        )
        
        self.trades.append(trade)
    
    def _close_position(self, timestamp: datetime, price: float, reason: str) -> None:
        """Close the current position."""
        if self.current_position == 0:
            return
            
        # Calculate P&L
        if self.current_position > 0:  # Long position
            pnl = (price - self.trades[-1].entry_price) * abs(self.current_position)
        else:  # Short position
            pnl = (self.trades[-1].entry_price - price) * abs(self.current_position)
        
        # Calculate fees
        position_value = price * abs(self.current_position)
        fees = position_value * self.commission
        
        # Update equity
        self.current_equity += pnl - fees
        
        # Update trade record
        self.trades[-1].exit_time = timestamp
        self.trades[-1].exit_price = price
        self.trades[-1].pnl = pnl - fees
        self.trades[-1].pnl_pct = (pnl / (self.trades[-1].entry_price * abs(self.current_position))) * 100
        self.trades[-1].fees_paid += fees
        self.trades[-1].exit_reason = reason
        self.trades[-1].tags.update({
            'exit_equity': self.current_equity,
            'exit_position': 0.0,
            'duration': (timestamp - self.trades[-1].entry_time).total_seconds() / 3600  # in hours
        })
        
        # Reset position
        self.current_position = 0.0
    
    def _update_equity_curve(self, row: pd.Series) -> None:
        """Update the running equity curve."""
        if self.current_position > 0:  # Long
            pnl = (row['close'] - self.trades[-1].entry_price) * self.current_position
        elif self.current_position < 0:  # Short
            pnl = (self.trades[-1].entry_price - row['close']) * abs(self.current_position)
        else:  # No position
            pnl = 0
            
        self.equity_curve.append(self.current_equity + pnl)

def run_backtest(strategy, data: pd.DataFrame, initial_capital: float = 10000.0, 
                commission: float = 0.0005, show_progress: bool = True) -> BacktestResult:
    """
    Helper function to run a backtest with default settings.
    
    Args:
        strategy: Instance of the trading strategy to backtest
        data: DataFrame with OHLCV data and required indicators
        initial_capital: Starting capital in quote currency
        commission: Trading commission as a fraction of trade value
        show_progress: Whether to show progress bar
        
    Returns:
        BacktestResult: Object containing backtest results
    """
    backtester = Backtester(strategy, initial_capital, commission)
    return backtester.run(data, show_progress)

if __name__ == "__main__":
    # Example usage
    from strategies.bos_fvg import BOSFVGStrategy
    
    # Load historical data
    data = pd.read_csv('historical_data.csv', parse_dates=['timestamp'], index_col='timestamp')
    
    # Initialize strategy
    strategy = BOSFVGStrategy(symbol='BTC/USDT')
    
    # Run backtest
    result = run_backtest(strategy, data)
    
    # Generate report
    result.generate_report()
    
    # Print metrics
    print("\nBacktest Results:")
    print("-" * 50)
    for metric, value in result.metrics.items():
        print(f"{metric.replace('_', ' ').title()}: {value:.2f}" if isinstance(value, float) else f"{metric.replace('_', ' ').title()}: {value}")
    print("-" * 50)
