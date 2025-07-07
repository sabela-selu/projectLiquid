import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from live_bos_fvg_ccxt import check_higher_tf_liquidity_sweep, setup_quality_filter

# --- Mock Data Generation ---
def generate_mock_ohlcv(periods=100, base_price=50000, volatility=0.01):
    """Generate mock OHLCV data with some structure."""
    np.random.seed(42)  # For reproducibility
    
    # Generate random price movements
    returns = np.random.normal(0, volatility, periods)
    prices = base_price * (1 + np.cumsum(returns))
    
    # Create OHLC structure
    df = pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=periods, freq='5min'),
        'open': prices * (1 + np.random.uniform(-0.001, 0.001, periods)),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.002, periods))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.002, periods))),
        'close': prices,
        'volume': np.random.uniform(10, 100, periods)
    })
    
    # Ensure high > low and high > open,close
    df['high'] = df[['open', 'high', 'close']].max(axis=1) * 1.0001
    df['low'] = df[['open', 'low', 'close']].min(axis=1) * 0.9999
    
    return df

# --- Mock Exchange Class ---
class MockExchange:
    def __init__(self, data):
        self.data = data
    
    def fetch_ohlcv(self, symbol, timeframe, limit=100):
        # Simulate higher timeframe data (e.g., 1h = 12 * 5min bars)
        tf_multiplier = {'5m': 1, '1h': 12, '4h': 48}[timeframe]
        df = self.data.iloc[::tf_multiplier].copy()
        
        # Convert to CCXT format: [timestamp, open, high, low, close, volume]
        ohlcv = df[['open', 'high', 'low', 'close', 'volume']].values
        ohlcv = np.column_stack((df['timestamp'].astype('int64') // 10**6, ohlcv))
        
        return ohlcv[-limit:]

# --- Test Setup ---
print("=== Testing Higher Timeframe Liquidity Sweep Filter ===\n")

# Generate mock data
print("Generating mock price data...")
mock_data = generate_mock_ohlcv(periods=500)
current_price = mock_data['close'].iloc[-1]
current_time = mock_data['timestamp'].iloc[-1]

# Simulate a trade signal (1 for long, -1 for short)
signal = pd.Series([0] * (len(mock_data) - 1) + [1], index=mock_data.index)

# Initialize mock exchange
mock_exchange = MockExchange(mock_data)

# --- Test 1: Check Higher Timeframe Sweep Directly ---
print("\n--- Testing Higher Timeframe Sweep Detection ---")
for tf in ["1h", "4h"]:
    sweep_detected = check_higher_tf_liquidity_sweep(
        mock_exchange, 'BTC/USDT', current_price, 1, tf, 50
    )
    print(f"{tf} Sweep Detected: {sweep_detected}")

# --- Test 2: Run Full Setup Quality Filter ---
print("\n--- Testing Full Setup Quality Filter ---")
should_trade = setup_quality_filter(
    df=mock_data,
    signal=signal,
    timestamp=current_time,
    exchange=mock_exchange,
    symbol='BTC/USDT',
    current_price=current_price
)

# --- Print Results ---
print("\n=== Test Results ===")
if should_trade:
    print("✅ Trade PASSED all filters")
else:
    print("❌ Trade FILTERED OUT")

print("\nNote: This test uses randomly generated data. For real trading, use actual market data.")
