# Advanced Algorithmic Trading Platform

This project is an advanced, multi-asset algorithmic trading platform designed to develop, backtest, and deploy sophisticated trading strategies. The current focus is on a strategy utilizing Break of Structure (BOS) and Fair Value Gaps (FVG) on multiple timeframes.

## Project Goal

The primary objective is to build a robust and profitable automated trading system that can be deployed across various asset classes, including cryptocurrencies and stock index futures. The platform is designed for modularity, allowing for easy integration of new strategies, exchanges, and risk management modules.

## Current Status

The project has successfully moved from initial development to a functional backtesting framework with proven results on select assets.

-   **Core Strategy**: A multi-timeframe strategy using **Break of Structure (BOS)** for trend confirmation and **Fair Value Gaps (FVG)** for high-probability entries has been implemented. The strategy operates on a 5-minute main timeframe and uses a 1-hour higher timeframe for trend alignment.
-   **Multi-Exchange Support**: The backtesting engine has been refactored to support multiple exchanges. It is currently configured for **Binance** (for cryptocurrencies) and **Bybit** (for stock index futures).
-   **Trade Visualization**: A Python script (`visualize_trades.py`) is available to plot trade entries and exits on a candlestick chart, providing a clear visual confirmation of the strategy's performance.

### Backtesting Performance

The strategy has been backtested over a 180-day period with the following results:

| Pair      | Net Return | Win Rate | Total Trades | Exchange |
| :-------- | :--------- | :------- | :----------- | :------- |
| BTC/USDT  | +13.00%    | 87.5%    | 8            | Binance  |
| ETH/USDT  | +3.00%     | 66.67%   | 3            | Binance  |
| SOL/USDT  | 0.00%      | 0%       | 0            | Binance  |
| BNB/USDT  | -2.00%     | 20%      | 5            | Binance  |

**Note**: The strategy's performance varies significantly across different assets, indicating that further parameter tuning is required for universal application.

## Project Roadmap

### Completed Milestones

-   [x] **Core Strategy Development**: Implemented the BOS/FVG signal generation logic.
-   [x] **Multi-Timeframe Analysis**: Integrated 1-hour data to filter trades based on the higher-timeframe trend.
-   [x] **Backtesting Framework**: Built a robust engine to simulate trades and evaluate strategy performance on historical data.
-   [x] **Multi-Asset Backtesting**: Successfully ran backtests on BTC/USDT, ETH/USDT, SOL/USDT, and BNB/USDT.
-   [x] **Performance Analysis**: Generated detailed logs, trade summaries, and key performance indicators (KPIs) like PnL and win rate.
-   [x] **Multi-Exchange Integration**: Refactored the codebase to support both Binance and Bybit.
-   [x] **Trade Visualization**: Created a script to plot backtest results for visual analysis.

### Next Steps (Immediate Priorities)

-   [ ] **Nasdaq 100 Backtest**: Execute the backtest for Nasdaq 100 futures (`NQ100_USDT`) on Bybit once API keys are configured.
-   [ ] **Strategy Optimization**: 
    -   Analyze the underperformance on BNB/USDT and SOL/USDT to identify areas for improvement.
    -   Experiment with adjusting the time window filter (currently 8am-12pm NY session) to capture more trading opportunities.
    -   Tune risk management parameters, such as risk-per-trade and reward ratio, for each asset class.
-   [ ] **Code Refinement**:
    -   Enhance the modularity of the strategy logic to allow for easier modifications and experimentation.
    -   Improve the visualization script to support dynamic asset selection via command-line arguments.

### Future Goals (Long-Term Vision)

-   [ ] **Live Trading Integration**: Develop a `live_trader.py` module to execute trades in real-time based on the strategy's signals.
-   [ ] **Advanced Risk Management**: Implement more sophisticated risk models, such as dynamic position sizing based on market volatility (e.g., using ATR).
-   [ ] **Expanded Asset Classes**: Add support for other markets, such as forex and commodities, by integrating with additional brokers.
-   [ ] **Machine Learning Integration**: Explore the use of machine learning models to filter trade signals, predict market regimes, or optimize strategy parameters.
-   [ ] **Web Dashboard**: Create a simple web-based dashboard to monitor real-time performance, review trade history, and manage the trading bot's configuration.

## Getting Started

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure API Keys**:
    -   Create a `.env` file in the root directory.
    -   Add your API keys for the desired exchanges:
        ```
        BINANCE_API_KEY=your_binance_api_key
        BINANCE_API_SECRET=your_binance_api_secret
        
        BYBIT_API_KEY=your_bybit_api_key
        BYBIT_API_SECRET=your_bybit_api_secret
        ```
3.  **Run a Backtest**:
    ```bash
    python3 backtest.py
    ```
4.  **Visualize Results**:
    ```bash
    python3 visualize_trades.py
    ```
