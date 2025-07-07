# BOS+FVG Trading Strategy

## Overview
This strategy combines Break of Structure (BOS) and Fair Value Gap (FVG) concepts to identify high-probability trading opportunities in trending markets. The strategy is implemented in Python using pandas, pandas_ta, and a custom backtesting framework.

## Strategy Logic

### Entry Conditions
1. **Break of Structure (BOS)**: 
   - For Long: Price breaks above recent high with higher high and higher low
   - For Short: Price breaks below recent low with lower high and lower low

2. **Fair Value Gap (FVG)**:
   - For Long: Bullish FVG (price gapped up)
   - For Short: Bearish FVG (price gapped down)

3. **Confirmation**:
   - RSI not in overbought/oversold territory
   - Volume above average (configurable threshold)

### Exit Conditions
1. **Take Profit**: Multi-level take profit (30% at 1R, 30% at 2R, 20% at 3R, 20% trailing)
2. **Stop Loss**: Initial stop below recent swing low/high
3. **Trailing Stop**: ATR-based trailing stop after breakeven
4. **Time Exit**: Close position after maximum holding period

## Files
- `strategies/bos_fvg_strategy.py`: Core strategy implementation
- `strategies/base_strategy.py`: Base class for all strategies
- `backtester.py`: Backtesting engine
- `example_backtest.py`: Example script to run backtest
- `requirements.txt`: Required Python packages

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd projectLiquid
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Backtest

1. Run the example backtest script:
   ```bash
   python example_backtest.py
   ```

   This will:
   - Download historical data for BTC-USD
   - Run the BOS+FVG strategy
   - Display performance metrics and equity curve

## Configuration

You can customize the strategy parameters in `example_backtest.py`:

```python
strategy = BOSFVGStrategy(
    symbol=symbol,
    params={
        'rsi_period': 14,
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'atr_period': 14,
        'risk_per_trade': 1.0,  # 1% risk per trade
        'reward_ratio': 2.0,    # 2:1 reward/risk ratio
        'bos_lookback': 20,     # Lookback for BOS detection
        'volume_ma_period': 20, # Period for volume MA
        'min_volume_ratio': 1.5 # Minimum volume ratio vs MA
    }
)
```

## Backtest Results

The backtest generates several performance metrics:
- Win rate
- Profit factor
- Sharpe ratio
- Maximum drawdown
- Average win/loss
- Trade duration statistics

## Next Steps

1. **Optimization**: Use grid search or genetic algorithms to find optimal parameters
2. **Walk-Forward Analysis**: Validate strategy on out-of-sample data
3. **Live Trading**: Implement live trading with exchange API integration
4. **Risk Management**: Add position sizing based on volatility and correlation

## License

MIT License

## Disclaimer

This software is for educational purposes only. Use at your own risk. Past performance is not indicative of future results.
