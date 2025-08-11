
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import ccxt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# --- Setup ---
load_dotenv()

# --- Exchange Connection ---
def get_exchange():
    """Initializes and returns a CCXT exchange instance for fetching data."""
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        print("API keys not found.")
        return None
    try:
        exchange = ccxt.binance({
            'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True
        })
        exchange.set_sandbox_mode(True)
        return exchange
    except Exception as e:
        print(f"Error connecting to Binance: {e}")
        return None

def fetch_historical_data(exchange, symbol, timeframe, days):
    """Fetches historical OHLCV data for the specified period."""
    print(f"[{symbol}] Fetching {days} days of {timeframe} data...")
    since = exchange.parse8601((datetime.now(timezone.utc) - timedelta(days=days)).isoformat())
    all_ohlcv = []
    try:
        while True:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            if not ohlcv:
                break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1
    except Exception as e:
        print(f"[{symbol}] Error fetching data: {e}")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
    df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
    return df

# --- Main Visualization Logic ---

# Configuration
SYMBOL = 'BTC/USDT'
TIMEFRAME = '5m'
BACKTEST_DAYS = 180

# Fetch data
exchange = get_exchange()
if exchange:
    btc_data = fetch_historical_data(exchange, SYMBOL, TIMEFRAME, BACKTEST_DAYS)

    if not btc_data.empty:
        # Manually define the trade log from the backtest results for BTC/USDT
        trades = [
            {'timestamp': '2025-07-02 15:15:00+00:00', 'direction': 'long', 'entry_price': 108110.20, 'result': 'win'},
            {'timestamp': '2025-07-03 15:25:00+00:00', 'direction': 'short', 'entry_price': 109795.08, 'result': 'win'},
            {'timestamp': '2025-07-07 14:45:00+00:00', 'direction': 'short', 'entry_price': 108191.00, 'result': 'win'},
            {'timestamp': '2025-07-09 15:00:00+00:00', 'direction': 'short', 'entry_price': 109201.63, 'result': 'win'},
            {'timestamp': '2025-07-10 15:20:00+00:00', 'direction': 'long', 'entry_price': 111394.31, 'result': 'win'},
            {'timestamp': '2025-07-11 14:35:00+00:00', 'direction': 'long', 'entry_price': 113395.73, 'result': 'win'},
            {'timestamp': '2025-07-15 15:00:00+00:00', 'direction': 'long', 'entry_price': 117208.94, 'result': 'loss'},
            {'timestamp': '2025-07-16 15:05:00+00:00', 'direction': 'long', 'entry_price': 118321.40, 'result': 'win'}
        ]
        trades_df = pd.DataFrame(trades)
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])

        # Create the candlestick chart
        fig = make_subplots(rows=1, cols=1)

        fig.add_trace(
            go.Candlestick(
                x=btc_data['timestamp'],
                open=btc_data['open'],
                high=btc_data['high'],
                low=btc_data['low'],
                close=btc_data['close'],
                name='Candlesticks'
            ),
            row=1, col=1
        )

        # Add trade markers to the chart
        for _, trade in trades_df.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=[trade['timestamp']],
                    y=[trade['entry_price']],
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up' if trade['direction'] == 'long' else 'triangle-down',
                        color='green' if trade['result'] == 'win' else 'red',
                        size=10
                    ),
                    name=f"{trade['direction'].capitalize()} ({trade['result']})"
                ),
                row=1, col=1
            )

        # Update layout
        fig.update_layout(
            title='BTC/USDT Backtest Trades',
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False
        )

        fig.show()
    else:
        print("Failed to fetch data for visualization.")
else:
    print("Failed to initialize exchange.")
