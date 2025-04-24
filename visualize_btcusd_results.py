import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf

# Load data
df = pd.read_csv('results/btcusd_1h_results.csv', parse_dates=['date', 'close time'])

# Set date as index for plotting
if 'date' in df.columns:
    df.set_index('date', inplace=True)

# Prepare OHLC data for mplfinance
ohlc_cols = ['open', 'high', 'low', 'close', 'volume']
mpf_df = df[ohlc_cols].copy()

# Prepare moving averages
sma_col = 'sma_10' if 'sma_10' in df.columns else None
ema_col = 'ema_10' if 'ema_10' in df.columns else None

# Prepare RSI
def plot_rsi(ax, rsi, overbought=70, oversold=30):
    ax.plot(rsi, color='purple', label='RSI (14)')
    ax.axhline(y=overbought, color='red', linestyle='--', linewidth=1, label='Overbought')
    ax.axhline(y=oversold, color='green', linestyle='--', linewidth=1, label='Oversold')
    ax.set_ylabel('RSI')
    ax.legend(loc='upper left')

# Prepare buy/sell markers
signal_col = 'signal'
buy_signals = df[df[signal_col] == 1]
sell_signals = df[df[signal_col] == -1]

# Prepare equity curve
equity_col = 'equity' if 'equity' in df.columns else None

# Create subplots
gs_kw = {'height_ratios': [3, 1, 1, 1]}
fig, axes = plt.subplots(4, 1, figsize=(16, 14), sharex=True, gridspec_kw=gs_kw)

# 1. Candlestick + MA + Buy/Sell
mpf.plot(mpf_df, ax=axes[0], type='candle', volume=False, show_nontrading=True)
if sma_col:
    axes[0].plot(df[sma_col], label='SMA 10', color='blue', linewidth=1)
if ema_col:
    axes[0].plot(df[ema_col], label='EMA 10', color='orange', linewidth=1)
axes[0].scatter(buy_signals.index, buy_signals['close'], marker='^', color='green', label='Buy', s=60, zorder=5)
axes[0].scatter(sell_signals.index, sell_signals['close'], marker='v', color='red', label='Sell', s=60, zorder=5)
axes[0].set_ylabel('BTC/USD Price')
axes[0].legend(loc='upper left')
axes[0].set_title('BTC/USD Price, MA, Buy/Sell Signals')

# 2. Volume
axes[1].bar(df.index, df['volume'], color='gray', width=0.03)
axes[1].set_ylabel('Volume (BTC)')
axes[1].set_title('Volume per Hour')

# 3. RSI
if 'rsi_14' in df.columns:
    plot_rsi(axes[2], df['rsi_14'])
    axes[2].set_title('RSI (14)')
else:
    axes[2].set_visible(False)

# 4. Equity curve
if equity_col:
    axes[3].plot(df[equity_col], color='black', label='Equity Curve')
    axes[3].set_ylabel('Equity')
    axes[3].set_title('Strategy Equity Curve')
    axes[3].legend()
else:
    axes[3].set_visible(False)

# Add a legend/annotation for signal meanings
signal_explanation = (
    "Signal Legend:\n"
    "+1 = Buy (Bullish)\n"
    "-1 = Sell (Bearish)\n"
    "0 = Hold / Neutral\n\n"
    "RSI: +1=Oversold, -1=Overbought\n"
    "Bollinger: +1=Breakout, -1=Breakdown\n"
    "MACD: +1=Bullish X, -1=Bearish X\n"
    "MA Cross: +1=Fast>Slow, -1=Fast<Slow\n"
    "Stochastic: +1=Oversold, -1=Overbought\n"
    "ML: Model output\n"
    "Meta: Consensus of above\n"
)
# Place the explanation as a textbox on the figure
fig.text(0.01, 0.01, signal_explanation, fontsize=10, va='bottom', ha='left', bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.show()
