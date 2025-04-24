"""
Binance Live Trader: Minimal framework for live trading BTC/USDT using your strategy signals.
- Fetches real-time data from Binance
- Applies your signal logic
- Places live orders (market buy/sell)
- Includes dry-run mode for safety
"""
import os
import time
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
import pandas as pd

# === CONFIGURATION ===
API_KEY = os.getenv("BINANCE_API_KEY", "YOUR_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET", "YOUR_API_SECRET")
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
STRATEGIES = {
    "BTCUSDT": "rsi",      # Use RSI for BTC
    "ETHUSDT": "atr_breakout"  # Use ATR breakout for ETH
}
RISK_PER_TRADE = 0.01  # 1% of account balance per trade
LEVERAGE = 1       # No leverage by default
ATR_WINDOW = 14
STOP_LOSS_ATR_MULT = 1.5   # e.g. 1.5x ATR below entry (default)
TAKE_PROFIT_ATR_MULT = 3.0 # e.g. 3x ATR above entry (default)
TRAIL_ATR_MULT = 1.0       # Trailing stop: 1x ATR
TRAIL_PCT = 0.01           # Or 1% trailing stop (alternative)
ATR_VOL_THRESHOLD = 0.02   # If ATR/price > 2%, treat as high volatility
INTERVAL = "4h"   # Candle interval
TRAIL_CHECK_INTERVAL = 60  # seconds between trailing stop checks
TRAIL_MIN_MOVE = 0.001     # Only move stop if price increases by at least this fraction
DRY_RUN = True     # Set False to enable real trading

# === INIT BINANCE ===
client = Client(API_KEY, API_SECRET)

# === LOAD SIGNAL LOGIC ===
from algotrade.signals import rsi_signal

def fetch_latest_ohlcv(symbol=SYMBOL, interval=INTERVAL, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'num_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    for col in ['open','high','low','close','volume']:
        df[col] = pd.to_numeric(df[col])
    df = df.set_index('close_time')
    return df

def get_signal(df):
    # Example: use RSI signal
    sig = rsi_signal.rsi_signal(df['close'])
    return sig.iloc[-1]

def get_account_balance(asset="USDT"):
    info = client.get_asset_balance(asset=asset)
    if info is None:
        raise RuntimeError(f"Could not fetch {asset} balance!")
    return float(info['free'])

def get_current_position(symbol=SYMBOL):
    # For spot trading, check BTC balance
    base_asset = symbol.replace('USDT','')
    info = client.get_asset_balance(asset=base_asset)
    if info is None:
        return 0.0
    return float(info['free'])

def calc_position_size(price, risk_per_trade=RISK_PER_TRADE, leverage=LEVERAGE):
    balance = get_account_balance()
    risk_amount = balance * risk_per_trade
    # For market order, size = risk_amount / price
    size = (risk_amount * leverage) / price
    # Binance min size for BTCUSDT is 0.0001 BTC
    return max(round(size, 6), 0.0001)

def compute_atr(df, window=ATR_WINDOW):
    high = df['high']
    low = df['low']
    close = df['close']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    atr_val = tr.rolling(window=window).mean()
    return atr_val.iloc[-1]

def dynamic_sl_tp(price, atr, df, signal_strength=None):
    # Volatility regime: ATR/price
    atr_pct = atr / price
    sl_mult = STOP_LOSS_ATR_MULT
    tp_mult = TAKE_PROFIT_ATR_MULT
    reason = []
    if atr_pct > ATR_VOL_THRESHOLD:
        sl_mult *= 1.5
        tp_mult *= 1.5
        reason.append(f"High volatility regime (ATR/price={atr_pct:.3f}) - using wider SL/TP")
    if signal_strength is not None and abs(signal_strength) > 10:
        tp_mult *= 1.2
        reason.append(f"Strong signal (strength={signal_strength:.2f}) - using more aggressive TP")
    return sl_mult, tp_mult, reason

def compute_trailing_levels(entry_price, atr, method="atr"):
    if method == "atr":
        trail = entry_price - TRAIL_ATR_MULT * atr
        return trail, f"Trailing stop: {TRAIL_ATR_MULT}x ATR below entry"
    elif method == "percent":
        trail = entry_price * (1 - TRAIL_PCT)
        return trail, f"Trailing stop: {TRAIL_PCT*100:.2f}% below entry"
    else:
        raise ValueError("Unknown trailing stop method")

import threading

def place_order(side, price, df, symbol=SYMBOL, risk_per_trade=RISK_PER_TRADE, leverage=LEVERAGE):
    quantity = calc_position_size(price, risk_per_trade, leverage)
    atr = compute_atr(df)
    # Example: use RSI distance from 50 as signal strength
    try:
        from algotrade.signals import rsi_signal
        rsi_val = rsi_signal.rsi_signal(df['close']).iloc[-1]
        signal_strength = abs(rsi_val - 50)
    except Exception:
        signal_strength = None
    sl_mult, tp_mult, reasons = dynamic_sl_tp(price, atr, df, signal_strength)
    sl = price - sl_mult * atr
    tp = price + tp_mult * atr
    trail_atr, trail_atr_reason = compute_trailing_levels(price, atr, method="atr")
    trail_pct, trail_pct_reason = compute_trailing_levels(price, atr, method="percent")
    if DRY_RUN:
        print(f"[DRY RUN] Would place {side} order for {quantity} {symbol} at {price}")
        if side == SIDE_BUY:
            print(f"[DRY RUN] ATR: {atr:.2f}, SL mult: {sl_mult}, TP mult: {tp_mult}")
            print(f"[DRY RUN] Stop loss at {sl:.2f}, take profit at {tp:.2f}")
            print(f"[DRY RUN] {trail_atr_reason}: {trail_atr:.2f}")
            print(f"[DRY RUN] {trail_pct_reason}: {trail_pct:.2f}")
            for r in reasons:
                print(f"[DRY RUN] {r}")
            # Simulate trailing stop monitoring
            simulate_trailing_stop(price, trail_atr, df, symbol, quantity)
        return None
    order = client.create_order(
        symbol=symbol,
        side=side,
        type=ORDER_TYPE_MARKET,
        quantity=quantity)
    print(f"Order placed: {order}")
    if side == SIDE_BUY:
        # Place OCO sell for stop loss and take profit (ATR-based, dynamic)
        sl_live = round(sl, 2)
        tp_live = round(tp, 2)
        try:
            oco = client.create_oco_order(
                symbol=symbol,
                side=SIDE_SELL,
                quantity=quantity,
                price=tp_live,  # take profit
                stopPrice=sl_live,  # stop loss trigger
                stopLimitPrice=sl_live,  # stop limit price
                stopLimitTimeInForce='GTC'
            )
            print(f"OCO order placed: {oco}")
            print(f"Trailing stop ATR: {trail_atr:.2f}, {trail_atr_reason}")
            print(f"Trailing stop %: {trail_pct:.2f}, {trail_pct_reason}")
            for r in reasons:
                print(f"{r}")
            # Start live trailing stop monitor in a background thread
            t = threading.Thread(target=trailing_stop_monitor, args=(symbol, price, trail_atr, quantity))
            t.daemon = True
            t.start()
        except Exception as e:
            print(f"Failed to place OCO order: {e}")
    return order

def live_trading_loop(symbol, strategy):
    last_signal = 0
    print(f"[LOOP] Starting trading loop for {symbol} using {strategy}")
    while True:
        df = fetch_latest_ohlcv(symbol=symbol)
        price = df['close'].iloc[-1]
        signal = get_signal(df, strategy)
        position = get_current_position(symbol)
        print(f"[{symbol}] Latest signal: {signal}, Last price: {price}, Position: {position}")
        # Position/risk management logic
        if signal == 1 and position < 0.0001:  # No position held, want to buy
            place_order(SIDE_BUY, price, df, symbol=symbol)
        elif signal == -1 and position > 0.0001:  # Position held, want to sell
            place_order(SIDE_SELL, price, df, symbol=symbol)
        else:
            print(f"[{symbol}] No action taken (either already in position or no signal change)")
        last_signal = signal
        time.sleep(60 * 60 * 4)  # Sleep for 4 hours (match interval)

def simulate_trailing_stop(entry, trail, df, symbol, quantity):
    print(f"[DRY RUN] Simulating trailing stop for {symbol}: entry={entry:.2f}, initial stop={trail:.2f}")
    # Simulate price rising
    prices = df['close'].iloc[-10:].tolist() + [entry + i*10 for i in range(1, 6)]
    stop = trail
    for price in prices:
        if price > entry and price - entry > TRAIL_MIN_MOVE * entry:
            new_stop = price - TRAIL_ATR_MULT * compute_atr(df)
            if new_stop > stop:
                print(f"[DRY RUN] Move trailing stop up to {new_stop:.2f} as price rises to {price:.2f}")
                stop = new_stop
        if price <= stop:
            print(f"[DRY RUN] Stop hit at {stop:.2f}, exit simulated position.")
            break
        else:
            print(f"[DRY RUN] Price={price:.2f}, stop={stop:.2f}")

def trailing_stop_monitor(symbol, entry, initial_stop, quantity):
    print(f"[TRAIL] Monitoring trailing stop for {symbol}: entry={entry:.2f}, initial stop={initial_stop:.2f}")
    stop = initial_stop
    while True:
        try:
            ticker = client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            if price > entry and price - entry > TRAIL_MIN_MOVE * entry:
                df = fetch_latest_ohlcv(symbol=symbol)
                new_stop = price - TRAIL_ATR_MULT * compute_atr(df)
                if new_stop > stop:
                    print(f"[TRAIL] Move trailing stop up to {new_stop:.2f} as price rises to {price:.2f}")
                    # Cancel previous OCO, place new OCO with updated stop
                    # (In production, you'd need to track order IDs and handle errors)
                    # For now, just log the action:
                    print(f"[TRAIL] Would cancel and replace OCO with stop at {new_stop:.2f}")
                    stop = new_stop
            if price <= stop:
                print(f"[TRAIL] Stop hit at {stop:.2f}, would exit position.")
                break
            else:
                print(f"[TRAIL] Price={price:.2f}, stop={stop:.2f}")
            time.sleep(TRAIL_CHECK_INTERVAL)
        except Exception as e:
            print(f"[TRAIL] Error in trailing stop monitor: {e}")
            time.sleep(TRAIL_CHECK_INTERVAL)

import threading

def start_multi_symbol_trading():
    threads = []
    for symbol in SYMBOLS:
        strategy = STRATEGIES.get(symbol, "rsi")
        t = threading.Thread(target=live_trading_loop, args=(symbol, strategy))
        t.daemon = True
        t.start()
        threads.append(t)
    print(f"[MAIN] Started {len(threads)} trading loops for symbols: {SYMBOLS}")
    for t in threads:
        t.join()

if __name__ == "__main__":
    start_multi_symbol_trading()
