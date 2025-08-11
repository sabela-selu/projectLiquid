import os
import ccxt
import pandas as pd
import logging
from datetime import datetime, timedelta, timezone
import pytz
import config

from strategies.bos_fvg_strategy import BOSFVGStrategy

# --- Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backtest_results.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuration ---
ASSETS_TO_TEST = {
    'binance': ['ETH/USDT', 'BTC/USDT', 'BNB/USDT'],
    'bybit': ['NDXUSDT']  # Nasdaq 100 Futures symbol on Bybit
}
TIMEFRAME = '5m'
ACCOUNT_BALANCE = 10000
BACKTEST_DAYS = 180

# --- Exchange Connection ---
def get_exchange(exchange_name, api_key, api_secret):
    """Initializes and returns a CCXT exchange instance using provided API keys."""
    if not api_key or not api_secret:
        logger.error(f"API keys were not provided for {exchange_name}.")
        return None
    
    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({
            'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True
        })
        
        # Set sandbox mode if available (supported by binance, not all exchanges)
        if exchange_name in ['binance'] and hasattr(exchange, 'set_sandbox_mode'):
            exchange.set_sandbox_mode(True)
            
        logger.info(f"Successfully connected to {exchange_name}.")
        return exchange
    except Exception as e:
        logger.error(f"Error connecting to {exchange_name}: {e}")
        return None

def fetch_historical_data(exchange, symbol, timeframe, days):
    """Fetches historical OHLCV data for the specified period."""
    logger.info(f"[{symbol}] Fetching {days} days of {timeframe} data...")
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
        logger.error(f"[{symbol}] Error fetching data: {e}")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
    df.set_index('timestamp', inplace=True)
    logger.info(f"[{symbol}] Fetched {len(df)} candles.")
    return df.astype(float)

# --- Backtesting Engine ---
def run_backtest_for_asset(symbol, exchange):
    """Main function to run the backtesting simulation for a single asset."""
    logger.info(f"[{symbol}] Starting backtest...")

    strategy_params = {
        'risk_per_trade': 1.0, 'reward_ratio': 2.0,
        'trading_start_time': '09:30', 'opening_range_end_time': '10:30',
        'trading_end_time': '16:00', 'timezone': 'America/New_York',
    }
    strategy = BOSFVGStrategy(symbol=symbol, params=strategy_params, account_balance=ACCOUNT_BALANCE)
    
    # Fetch main and HTF data
    logger.info(f"[{symbol}] Fetching main timeframe ({TIMEFRAME}) data...")
    data = fetch_historical_data(exchange, symbol, TIMEFRAME, BACKTEST_DAYS)
    logger.info(f"[{symbol}] Fetching higher timeframe (1h) data...")
    htf_data = fetch_historical_data(exchange, symbol, '1h', BACKTEST_DAYS)
    if data.empty or htf_data.empty:
        logger.error(f"[{symbol}] No data for backtesting. Skipping.")
        return

    logger.info(f"[{symbol}] Setting strategy data...")
    strategy.set_data(data, htf_data)
    logger.info(f"[{symbol}] Strategy data set. Processed data length: {len(strategy.data)}.")
    trades_log = []

    logger.info(f"[{symbol}] Starting evaluation loop...")
    # Iterate through the strategy's processed data length
    for i in range(1, len(strategy.data)):
        signal = strategy.evaluate(index=i)
        if signal:
            trade_result = 'ongoing'
            # Simulate trade execution from the signal point forward
            for j in range(i + 1, len(strategy.data)):
                future_low, future_high = strategy.data['low'].iloc[j], strategy.data['high'].iloc[j]
                if signal['direction'] == 'long':
                    if future_low <= signal['stop_loss']:
                        trade_result = 'loss'
                        break
                    if future_high >= signal['take_profit']:
                        trade_result = 'win'
                        break
                elif signal['direction'] == 'short':
                    if future_high >= signal['stop_loss']:
                        trade_result = 'loss'
                        break
                    if future_low <= signal['take_profit']:
                        trade_result = 'win'
                        break
            
            trade_pnl = 0
            if trade_result == 'win':
                pnl_calc = (signal['take_profit'] - signal['entry_price']) if signal['direction'] == 'long' else (signal['entry_price'] - signal['take_profit'])
                trade_pnl = pnl_calc * signal['size']
            elif trade_result == 'loss':
                pnl_calc = (signal['stop_loss'] - signal['entry_price']) if signal['direction'] == 'long' else (signal['entry_price'] - signal['stop_loss'])
                trade_pnl = pnl_calc * signal['size']

            trades_log.append({
                'timestamp': signal['timestamp'], 'direction': signal['direction'],
                'entry_price': signal['entry_price'], 'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'], 'result': trade_result, 'pnl': trade_pnl
            })

    logger.info(f"[{symbol}] Evaluation loop finished. Generating summary...")
    print_summary(trades_log, symbol)

def print_summary(trades_log, symbol):
    """Prints a detailed summary of the backtest results for a given symbol."""
    header = f"--- Backtest Summary for {symbol} ---"
    logger.info("\n" + "="*len(header))
    logger.info(header)
    logger.info("="*len(header))

    if not trades_log:
        logger.info(f"[{symbol}] No trades were executed.")
        return

    trades_df = pd.DataFrame(trades_log)
    wins = len(trades_df[trades_df['result'] == 'win'])
    losses = len(trades_df[trades_df['result'] == 'loss'])
    win_rate = (wins / len(trades_df)) * 100 if trades_df.shape[0] > 0 else 0
    total_pnl = trades_df['pnl'].sum()
    final_balance = ACCOUNT_BALANCE + total_pnl
    net_return_percent = (total_pnl / ACCOUNT_BALANCE) * 100

    logger.info(f"[{symbol}] Initial Balance: ${ACCOUNT_BALANCE:,.2f}")
    logger.info(f"[{symbol}] Final Balance:   ${final_balance:,.2f}")
    logger.info(f"[{symbol}] Net Return:      ${total_pnl:,.2f} ({net_return_percent:.2f}%)")
    logger.info(f"[{symbol}] Total Trades:    {len(trades_df)}")
    logger.info(f"[{symbol}] Win Rate:        {win_rate:.2f}% (Wins: {wins}, Losses: {losses})")
    logger.info(f"\n--- [{symbol}] Detailed Trade Log ---")
    logger.info(trades_df.to_string())

if __name__ == "__main__":
    logger.info("Starting backtests for all configured exchanges and assets...")
    
    for exchange_name, assets in ASSETS_TO_TEST.items():
        logger.info(f"\n--- Exchange: {exchange_name.upper()} ---")

        # Load API keys from config.py
        api_key_name = f"{exchange_name.upper()}_API_KEY"
        api_secret_name = f"{exchange_name.upper()}_API_SECRET"
        api_key = getattr(config, api_key_name, None)
        api_secret = getattr(config, api_secret_name, None)

        # Detailed checks for API keys
        if not api_key:
            logger.error(f"'{api_key_name}' not found in config.py. Skipping {exchange_name}.")
            continue
        if 'YOUR_' in api_key:
            logger.error(f"'{api_key_name}' in config.py still contains the placeholder value. Please replace it with your actual key.")
            continue
        if not api_secret:
            logger.error(f"'{api_secret_name}' not found in config.py. Skipping {exchange_name}.")
            continue
        if 'YOUR_' in api_secret:
            logger.error(f"'{api_secret_name}' in config.py still contains the placeholder value. Please replace it with your actual secret.")
            continue

        exchange = get_exchange(exchange_name, api_key, api_secret)
        
        if not exchange:
            logger.warning(f"Skipping backtests for {exchange_name} due to connection failure.")
            continue
            
        logger.info(f"Starting sequential backtests for: {', '.join(assets)}")
        for asset in assets:
            try:
                run_backtest_for_asset(asset, exchange)
                logger.info(f"Backtest for {asset} completed successfully.")
            except Exception as exc:
                logger.error(f'{asset} backtest generated an exception: {exc}')
                
    logger.info("All backtests have been completed.")
