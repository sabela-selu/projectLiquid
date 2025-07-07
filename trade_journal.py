"""
Trade Journal Module
-------------------
Handles trade recording, analysis, and reporting for the BOS+FVG strategy.
"""
import pandas as pd
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional

class TradeJournal:
    def __init__(self, output_dir: str = 'trades'):
        """Initialize trade journal with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.trades: List[Dict] = []
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'expectancy': 0.0,
            'average_win': 0.0,
            'average_loss': 0.0,
            'max_win': float('-inf'),
            'max_loss': float('inf')
        }
        
    def add_trade(self, trade: Dict):
        """Add a completed trade to the journal."""
        self.trades.append(trade)
        self._update_metrics()
        
    def _update_metrics(self):
        """Update performance metrics based on recorded trades."""
        if not self.trades:
            return
            
        df = pd.DataFrame(self.trades)
        df['win'] = df['pnl'] > 0
        
        self.metrics['total_trades'] = len(df)
        self.metrics['winning_trades'] = df['win'].sum()
        self.metrics['losing_trades'] = len(df) - self.metrics['winning_trades']
        self.metrics['total_pnl'] = df['pnl'].sum()
        self.metrics['win_rate'] = (self.metrics['winning_trades'] / len(df)) * 100 if df.size > 0 else 0
        
        winning_pnl = df[df['win']]['pnl'].sum()
        losing_pnl = abs(df[~df['win']]['pnl'].sum())
        self.metrics['profit_factor'] = winning_pnl / losing_pnl if losing_pnl > 0 else float('inf')
        
        # Calculate max drawdown
        cum_returns = df['pnl'].cumsum()
        running_max = cum_returns.cummax()
        drawdown = (cum_returns - running_max) / (running_max + 1e-10)  # Avoid division by zero
        self.metrics['max_drawdown'] = drawdown.min() * 100  # as percentage
        
        # Calculate Sharpe ratio (assuming 0% risk-free rate for simplicity)
        returns = df['pnl'] / df['entry_price'].abs()  # Simple return calculation
        self.metrics['sharpe_ratio'] = (returns.mean() / (returns.std() + 1e-10)) * np.sqrt(252)  # Annualized
        
        # Win/Loss metrics
        if not df[df['win']].empty:
            self.metrics['average_win'] = df[df['win']]['pnl'].mean()
            self.metrics['max_win'] = df[df['win']]['pnl'].max()
            
        if not df[~df['win']].empty:
            self.metrics['average_loss'] = df[~df['win']]['pnl'].mean()
            self.metrics['max_loss'] = df[~df['win']]['pnl'].min()
            
        # Calculate expectancy
        avg_win = self.metrics['average_win']
        avg_loss = abs(self.metrics['average_loss'])
        win_rate = self.metrics['win_rate'] / 100
        loss_rate = 1 - win_rate
        self.metrics['expectancy'] = (win_rate * avg_win) - (loss_rate * avg_loss)
    
    def generate_report(self):
        """Generate a comprehensive trade report."""
        if not self.trades:
            return "No trades recorded yet."
            
        report = {
            'summary': self.metrics,
            'trades': self.trades,
            'report_date': datetime.utcnow().isoformat()
        }
        
        # Save as JSON
        report_file = os.path.join(self.output_dir, f'trade_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate visualizations
        self._generate_visualizations()
        
        return report
    
    def _generate_visualizations(self):
        """Generate performance visualizations."""
        df = pd.DataFrame(self.trades)
        
        # Equity Curve
        plt.figure(figsize=(12, 6))
        df['cumulative_pnl'] = df['pnl'].cumsum()
        plt.plot(df['exit_time'], df['cumulative_pnl'])
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Cumulative P&L')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'equity_curve.png'))
        plt.close()
        
        # P&L Distribution
        plt.figure(figsize=(10, 6))
        plt.hist(df['pnl'], bins=30, alpha=0.7)
        plt.axvline(0, color='r', linestyle='--')
        plt.title('P&L Distribution')
        plt.xlabel('P&L')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'pnl_distribution.png'))
        plt.close()
        
        # Win/Loss Pie Chart
        plt.figure(figsize=(8, 8))
        win_loss = [self.metrics['winning_trades'], self.metrics['losing_trades']]
        plt.pie(win_loss, labels=['Wins', 'Losses'], autopct='%1.1f%%', startangle=90)
        plt.title('Win/Loss Distribution')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'win_loss_pie.png'))
        plt.close()
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get recent trade history."""
        return self.trades[-limit:]
    
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics."""
        return self.metrics
    
    def export_trades_csv(self, filename: str = 'trades_export.csv'):
        """Export trades to CSV file."""
        if not self.trades:
            return False
            
        df = pd.DataFrame(self.trades)
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath

# Singleton instance
trade_journal = TradeJournal()
