import ccxt
import pandas as pd
import time
import logging
from strategies.bos_fvg_strategy import BOSFVGStrategy
from ai.ai_analyzer import AIAnalyzer
from ai.providers import OpenAICompatibleProvider
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# --- Configuration ---
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1m'  # The strategy logic is designed for 1-minute candles
ACCOUNT_BALANCE = 10000
FETCH_LIMIT = 100 # Number of candles to fetch for context

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- Exchange Connection ---
def get_exchange():
    """Initializes and returns a CCXT exchange instance."""
    try:
        exchange = ccxt.bybit({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        exchange.set_sandbox_mode(True) # Enable testnet
        exchange.load_markets()
        logger.info(f"Successfully connected to {exchange.id}.")
        return exchange
    except Exception as e:
        logger.error(f"Error connecting to exchange: {e}")
        return None

def fetch_ohlcv(exchange, symbol, timeframe, limit):
    """Fetches OHLCV data and returns a pandas DataFrame."""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
        df.set_index('timestamp', inplace=True)
        return df.astype(float)
    except Exception as e:
        logger.error(f"Error fetching OHLCV data: {e}")
        return None

# --- Main Execution Loop ---
def main():
    """Main loop to run the trading strategy."""
    exchange = get_exchange()
    if not exchange:
        return

    strategy_params = {
        'risk_per_trade': 1.0,
        'reward_ratio': 2.0,
        'trading_start_time': '09:30',
        'trading_end_time': '11:00',
        'timezone': 'America/New_York',
    }

    strategy = BOSFVGStrategy(
        symbol=SYMBOL,
        params=strategy_params,
        account_balance=ACCOUNT_BALANCE
    )

    logger.info(f"Starting paper trading for {SYMBOL} on {TIMEFRAME} timeframe.")
    logger.info(f"Trading session: {strategy.params['trading_start_time']} - {strategy.params['trading_end_time']} {strategy.params['timezone']}")

    # --- AI Analyzer Setup ---
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        ai_provider = OpenAICompatibleProvider(
            api_key=api_key,
            model="deepseek/deepseek-coder", # Using DeepSeek Coder model
            base_url="https://openrouter.ai/api/v1"
        )
        ai_analyzer = AIAnalyzer(provider=ai_provider)
        logger.info("AI Analyzer initialized successfully with OpenRouter and DeepSeek.")
    except ValueError as e:
        logger.error(f"Failed to initialize AI Analyzer: {e}")
        ai_analyzer = None

    while True:
        try:
            # Fetch the latest data
            data = fetch_ohlcv(exchange, SYMBOL, TIMEFRAME, limit=FETCH_LIMIT)
            if data is None or data.empty:
                time.sleep(60) # Wait before retrying if data fetch fails
                continue

            # Set data and evaluate the strategy
            strategy.set_data(data)
            signal = strategy.evaluate(index=len(data) - 1) # Evaluate the last complete candle

            if signal:
                logger.info(f"TRADE SIGNAL: {signal}")
                if ai_analyzer:
                    # Get AI confidence score
                    market_data_str = data.tail(10).to_string() # Use last 10 candles as context
                    confidence_score = ai_analyzer.get_trade_confidence(market_data_str, signal)
                    logger.info(f"AI Confidence Score: {confidence_score}")

                    if confidence_score >= 75: # Confidence threshold
                        logger.info("Trade approved by AI. Executing...")
                        # In a real scenario, you would place an order here
                    else:
                        logger.info("Trade rejected by AI due to low confidence.")
                else:
                    # Fallback if AI analyzer is not available
                    logger.warning("AI Analyzer not available. Skipping confidence check.")

            # Wait for the next candle
            logger.info("Waiting for the next candle...")
            time.sleep(60) # Wait for 1 minute

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
