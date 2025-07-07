import ccxt
import pandas as pd
import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from strategies.bos_fvg_strategy import BOSFVGStrategy
from ai.ai_analyzer import AIAnalyzer
from ai.providers import OpenAICompatibleProvider

# --- Setup ---
load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- Configuration ---
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1m'
ACCOUNT_BALANCE = 10000
BACKTEST_DAYS = 30 # Number of days to backtest
AI_CONFIDENCE_THRESHOLD = 60
USE_AI_ANALYZER = False # Set to True to enable AI confidence check

# --- Exchange Connection ---
def get_exchange():
    """Initializes and returns a CCXT exchange instance for fetching data."""
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("BINANCE_API_KEY and/or BINANCE_API_SECRET not found in .env file.")
        return None

    try:
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        exchange.set_sandbox_mode(True)
        exchange.load_markets()
        logger.info("Successfully connected to Binance sandbox.")
        return exchange
    except Exception as e:
        logger.error(f"Error connecting to Binance: {e}")
        return None

def fetch_historical_data(exchange, symbol, timeframe, days):
    """Fetches historical OHLCV data for the specified period."""
    logger.info(f"Starting historical data fetch for {days} days...")
    since = exchange.parse8601((datetime.utcnow() - timedelta(days=days)).isoformat())
    all_ohlcv = []
    batch_num = 1
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            if not ohlcv:
                break
            logger.info(f"Fetched batch {batch_num} with {len(ohlcv)} candles.")
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1
            batch_num += 1
        except Exception as e:
            logger.error(f"Error fetching data batch: {e}")
            break
    
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
    df.set_index('timestamp', inplace=True)
    logger.info(f"Fetched {len(df)} candles for backtesting.")
    return df.astype(float)

# --- Backtesting Engine ---
def run_backtest():
    """Main function to run the backtesting simulation."""
    exchange = get_exchange()
    if not exchange:
        logger.error("Failed to initialize exchange. Exiting backtest.")
        return

    # Initialize Strategy and AI Analyzer
    strategy_params = {
        'risk_per_trade': 1.0,
        'reward_ratio': 2.0,
        'trading_start_time': '09:30',
        'opening_range_end_time': '10:30',
        'trading_end_time': '16:00',
        'timezone': 'America/New_York',
    }
    strategy = BOSFVGStrategy(symbol=SYMBOL, params=strategy_params, account_balance=ACCOUNT_BALANCE)
    
    ai_analyzer = None
    if USE_AI_ANALYZER:
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            ai_provider = OpenAICompatibleProvider(
                api_key=api_key,
                model="mistralai/mistral-7b-instruct:free", # Or any other valid model
                base_url="https://openrouter.ai/api/v1"
            )
            ai_analyzer = AIAnalyzer(provider=ai_provider)
            logger.info("AI Analyzer initialized successfully.")
        except ValueError as e:
            logger.error(f"Failed to initialize AI Analyzer: {e}")
            return

    # Fetch data
    data = fetch_historical_data(exchange, SYMBOL, TIMEFRAME, BACKTEST_DAYS)
    if data.empty:
        logger.error("No data for backtesting. Exiting.")
        return

    logger.info(f"Fetched {len(data)} candles. Data head:\n{data.head()}")
    logger.info(f"Data tail:\n{data.tail()}")

    # Save data to CSV for inspection
    try:
        data.to_csv('fetched_data.csv')
        logger.info("Saved fetched data to fetched_data.csv")
    except Exception as e:
        logger.error(f"Failed to save data to CSV: {e}")

    # Set the historical data on the strategy once to pre-calculate indicators
    strategy.set_data(data)

    trades_log = []

    # Loop through historical data, starting from index 1
    for i in range(1, len(data)):
        signal = strategy.evaluate(index=i)

        if signal:
            logger.info(f"[{data.index[i]}] Strategy generated signal: {signal['direction']}")
            
            confidence = 100 # Default to 100 if AI is disabled
            if USE_AI_ANALYZER:
                # Get AI confidence score
                market_context = data.iloc[i-10:i].to_string()
                confidence = ai_analyzer.get_trade_confidence(market_context, signal)
                logger.info(f"AI Confidence Score: {confidence}")

            if confidence >= AI_CONFIDENCE_THRESHOLD:
                logger.info("Trade approved. Simulating trade...")
                # Simulate the trade to see outcome
                trade_result = 'ongoing'

                # Look ahead to see if SL or TP was hit
                for j in range(i + 1, len(data)):
                    future_low = data['low'].iloc[j]
                    future_high = data['high'].iloc[j]

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
                
                # Correct PnL calculation using trade size from signal
                trade_pnl = 0
                if trade_result == 'win':
                    if signal['direction'] == 'long':
                        trade_pnl = (signal['take_profit'] - signal['entry_price']) * signal['size']
                    else: # short
                        trade_pnl = (signal['entry_price'] - signal['take_profit']) * signal['size']
                elif trade_result == 'loss':
                    if signal['direction'] == 'long':
                        trade_pnl = (signal['stop_loss'] - signal['entry_price']) * signal['size']
                    else: # short
                        trade_pnl = (signal['entry_price'] - signal['stop_loss']) * signal['size']

                trade_details = {
                    'timestamp': signal['timestamp'],
                    'direction': signal['direction'],
                    'entry_price': signal['entry_price'],
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit'],
                    'result': trade_result,
                    'pnl': trade_pnl
                }
                trades_log.append(trade_details)
                logger.info(f"Trade Result: {trade_result.upper()}, PnL: ${trade_pnl:,.2f}")
                # Prevent more trades today is handled within the strategy
            else:
                logger.info("Trade rejected by AI.")

    # --- Summary ---
    print_summary(trades_log)

def print_summary(trades_log):
    """Prints a detailed summary of the backtest results."""
    logger.info("\n--- Backtest Summary ---")
    if not trades_log:
        logger.info("No trades were executed.")
        return

    trades_df = pd.DataFrame(trades_log)
    
    wins = len(trades_df[trades_df['result'] == 'win'])
    losses = len(trades_df[trades_df['result'] == 'loss'])
    win_rate = (wins / len(trades_df)) * 100 if trades_df.shape[0] > 0 else 0
    
    total_pnl = trades_df['pnl'].sum()
    final_balance = ACCOUNT_BALANCE + total_pnl
    net_return_percent = (total_pnl / ACCOUNT_BALANCE) * 100

    logger.info(f"Initial Balance: ${ACCOUNT_BALANCE:,.2f}")
    logger.info(f"Final Balance:   ${final_balance:,.2f}")
    logger.info(f"Net Return:      ${total_pnl:,.2f} ({net_return_percent:.2f}%)")
    logger.info(f"Total Trades:    {len(trades_df)}")
    logger.info(f"Wins:            {wins}")
    logger.info(f"Losses:          {losses}")
    logger.info(f"Win Rate:        {win_rate:.2f}%")

    trades_df['pnl_percent'] = (trades_df['pnl'] / ACCOUNT_BALANCE) * 100
    logger.info("\n--- Detailed Trade Log ---")
    # Format float columns for better readability
    trades_df['entry_price'] = trades_df['entry_price'].map('{:,.2f}'.format)
    trades_df['stop_loss'] = trades_df['stop_loss'].map('{:,.2f}'.format)
    trades_df['take_profit'] = trades_df['take_profit'].map('{:,.2f}'.format)
    trades_df['pnl'] = trades_df['pnl'].map('${:,.2f}'.format)
    trades_df['pnl_percent'] = trades_df['pnl_percent'].map('{:,.2f}%'.format)
    
    logger.info(trades_df.to_string())

if __name__ == "__main__":
    run_backtest()
