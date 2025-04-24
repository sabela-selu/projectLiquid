import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Load 4h data
# Load and standardize 4h data columns
df = pd.read_csv('algotrade/data/btc_4h_data_2018_to_2025.csv', parse_dates=['Open time', 'Close time'])
# Rename columns to standard format for plotting
rename_map = {
    'Open time': 'date',
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Close': 'close',
    'Volume': 'volume',
    'Close time': 'close_time',
    'Quote asset volume': 'quote_asset_volume',
    'Number of trades': 'number_of_trades',
    'Taker buy base asset volume': 'taker_buy_base_asset_volume',
    'Taker buy quote asset volume': 'taker_buy_quote_asset_volume',
    'Ignore': 'ignore'
}
df.rename(columns=rename_map, inplace=True)
df.set_index('date', inplace=True)

# Prepare signals for markers
signal_col = 'signal' if 'signal' in df.columns else None
buy_signals = df[df[signal_col] == 1] if signal_col else pd.DataFrame()
sell_signals = df[df[signal_col] == -1] if signal_col else pd.DataFrame()

# Create subplots: Price+MA, Volume, RSI, Equity
rows = 4
fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03,
    row_heights=[0.45, 0.15, 0.15, 0.25],
    subplot_titles=("BTC/USD 4h OHLC & Signals", "Volume", "RSI (14)", "Equity Curve"))

# 1. Candlestick chart
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['open'], high=df['high'], low=df['low'], close=df['close'],
    name='OHLC', showlegend=True
), row=1, col=1)

# 1b. Moving averages
if 'sma_10' in df.columns:
    fig.add_trace(go.Scatter(x=df.index, y=df['sma_10'], mode='lines', name='SMA 10', line=dict(color='blue')), row=1, col=1)
if 'ema_10' in df.columns:
    fig.add_trace(go.Scatter(x=df.index, y=df['ema_10'], mode='lines', name='EMA 10', line=dict(color='orange')), row=1, col=1)

# 1c. Buy/sell signals
if not buy_signals.empty:
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['close'], mode='markers',
        marker=dict(symbol='triangle-up', color='green', size=10), name='Buy Signal'), row=1, col=1)
if not sell_signals.empty:
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['close'], mode='markers',
        marker=dict(symbol='triangle-down', color='red', size=10), name='Sell Signal'), row=1, col=1)

# 2. Volume
fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume', marker_color='gray'), row=2, col=1)

# 3. RSI
if 'rsi_14' in df.columns:
    fig.add_trace(go.Scatter(x=df.index, y=df['rsi_14'], mode='lines', name='RSI 14', line=dict(color='purple')), row=3, col=1)
    fig.add_hline(y=70, line_dash='dash', line_color='red', row=3, col=1)
    fig.add_hline(y=30, line_dash='dash', line_color='green', row=3, col=1)

# 4. Equity curve
if 'equity' in df.columns:
    fig.add_trace(go.Scatter(x=df.index, y=df['equity'], mode='lines', name='Equity', line=dict(color='black')), row=4, col=1)

# Signal legend as annotation
signal_legend = (
    "<b>Signal Legend:</b><br>"
    "+1 = Buy (Bullish)<br>"
    "-1 = Sell (Bearish)<br>"
    "0 = Hold / Neutral<br>"
    "RSI: +1=Oversold, -1=Overbought<br>"
    "Bollinger: +1=Breakout, -1=Breakdown<br>"
    "MACD: +1=Bullish X, -1=Bearish X<br>"
    "MA Cross: +1=Fast>Slow, -1=Fast<Slow<br>"
    "Stochastic: +1=Oversold, -1=Overbought<br>"
    "ML: Model output<br>"
    "Meta: Consensus of above<br>"
)
fig.add_annotation(
    text=signal_legend,
    xref="paper", yref="paper",
    x=0.01, y=0.02, showarrow=False,
    align="left", font=dict(size=11),
    bordercolor="gray", borderwidth=1, bgcolor="white", opacity=0.85
)

fig.update_layout(
    height=1100, width=1400,
    title="BTC/USD 4h Strategy Visualization (Interactive)",
    xaxis_rangeslider_visible=False,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

fig.show()
