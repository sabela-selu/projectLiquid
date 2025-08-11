"""
BOS+FVG Trading Strategy
----------------------
Implements the Break of Structure (BOS) and Fair Value Gap (FVG) strategy.
"""
from typing import Dict, Any, Optional
import pandas as pd
import pytz
import pandas_ta as ta
import logging
from datetime import time

logger = logging.getLogger(__name__)

class BOSFVGStrategy:
    """A streamlined implementation of the BOS+FVG trading strategy based on the user's rules."""

    def __init__(self, symbol: str, params: Optional[Dict[str, Any]] = None, account_balance: float = 10000.0):
        default_params = {
            'risk_per_trade': 1.0,
            'reward_ratio': 2.0,
            'trading_start_time': '09:30',
            'opening_range_end_time': '10:30',
            'trading_end_time': '16:00',
            'timezone': 'America/New_York',
        }
        if params:
            default_params.update(params)
        
        self.symbol = symbol
        self.params = default_params
        self.account_balance = account_balance
        self.data = None

        # Strategy state
        self.hod = None  # Will be set to the opening range high
        self.lod = None  # Will be set to the opening range low
        self.opening_range_high = None
        self.opening_range_low = None
        self.bos_direction = None
        self.fvg_to_watch = None
        self.trade_taken_today = False
        self.current_day = None

        # Parse trading times
        self.start_time = time.fromisoformat(self.params['trading_start_time'])
        self.opening_range_end_time = time.fromisoformat(self.params['opening_range_end_time'])
        self.end_time = time.fromisoformat(self.params['trading_end_time'])
        self.tz = pytz.timezone(self.params['timezone'])

    def set_data(self, data: pd.DataFrame, htf_data: pd.DataFrame):
        """Sets and preprocesses the historical data, merging higher timeframe data."""
        # Calculate HTF indicator (e.g., 20-period EMA on 1h)
        htf_data['htf_ema'] = htf_data['close'].ewm(span=20, adjust=False).mean()

        # Merge HTF data into the main dataframe
        # Use merge_asof to find the latest HTF candle for each 5m candle
        self.data = pd.merge_asof(
            data.sort_index(),
            htf_data[['htf_ema']].sort_index(),
            left_index=True,
            right_index=True,
            direction='backward'
        ).copy()

        # Add ADX for trend strength filtering
        adx = self.data.ta.adx(length=14)
        self.data = pd.concat([self.data, adx], axis=1)

        # HOD/LOD is now calculated dynamically in the evaluate loop
        self._calculate_fvg()

    def _is_market_open(self, timestamp: pd.Timestamp) -> bool:
        """Check if the current time is within the allowed trading session."""
        local_time = timestamp.tz_convert(self.tz).time()
        return self.start_time <= local_time < self.end_time

    def _calculate_fvg(self):
        """Identifies Fair Value Gaps (FVG) after a Break of Structure."""
        if self.data is None: return
        df = self.data
        df.loc[:, 'fvg_bullish'] = df['low'] > df['high'].shift(2)
        df.loc[:, 'fvg_bearish'] = df['high'] < df['low'].shift(2)
        df.loc[:, 'fvg_bullish_top'] = df['high'].shift(2)
        df.loc[:, 'fvg_bullish_bottom'] = df['low']
        df.loc[:, 'fvg_bearish_top'] = df['high']
        df.loc[:, 'fvg_bearish_bottom'] = df['low'].shift(2)
        df.loc[:, 'fvg_middle_candle_low'] = df['low'].shift(1)
        df.loc[:, 'fvg_middle_candle_high'] = df['high'].shift(1)

    def _find_fvg(self, index, direction):
        """Finds the most recent FVG, returning its bottom, top, and stop-loss level."""
        logger.debug(f"Searching for FVG for a {direction} trade at index {index}.")
        # Look back up to 10 candles to find an FVG
        for i in range(index - 2, index - 10, -1):
            if i < 2:
                logger.debug("Not enough candles to find FVG.")
                return None, None, None # fvg_bottom, fvg_top, stop_loss

            c1 = self.data.iloc[i - 2]
            c2 = self.data.iloc[i - 1] # The middle candle
            c3 = self.data.iloc[i]

            logger.debug(f"Checking FVG at index {i}: c1_high={c1['high']:.2f}, c3_low={c3['low']:.2f} | c1_low={c1['low']:.2f}, c3_high={c3['high']:.2f}")

            # FVG Quality Filter: Check if the middle candle has a strong body
            candle_range = c2['high'] - c2['low']
            candle_body = abs(c2['open'] - c2['close'])
            if candle_range > 0 and (candle_body / candle_range) < 0.5:
                logger.debug(f"Skipping FVG at index {i} due to weak middle candle (body < 50% of range).")
                continue # Skip to the next iteration

            is_bullish_fvg = c1['high'] < c3['low']
            is_bearish_fvg = c1['low'] > c3['high']

            if direction == 'long' and is_bullish_fvg:
                fvg_bottom = c1['high']
                fvg_top = c3['low']
                stop_loss = c2['low'] # SL is the low of the middle candle
                logger.info(f"Found Bullish FVG at index {i}: Range ({fvg_bottom:.2f}, {fvg_top:.2f}), SL: {stop_loss:.2f}")
                return fvg_bottom, fvg_top, stop_loss
            
            if direction == 'short' and is_bearish_fvg:
                fvg_bottom = c3['high']
                fvg_top = c1['low']
                stop_loss = c2['high'] # SL is the high of the middle candle
                logger.info(f"Found Bearish FVG at index {i}: Range ({fvg_bottom:.2f}, {fvg_top:.2f}), SL: {stop_loss:.2f}")
                return fvg_bottom, fvg_top, stop_loss

        logger.debug("No FVG found in the lookback period.")
        return None, None, None

    def evaluate(self, index: int) -> Optional[Dict]:
        """Evaluates the strategy for a given data point (candle) using a state machine."""
        if self.data is None or index < 10: # Need enough lookback for FVG
            return None

        current_candle = self.data.iloc[index]
        
        # --- Time and State Management ---
        local_timestamp = current_candle.name.tz_convert(self.tz)
        local_date = local_timestamp.date()
        local_time = local_timestamp.time()

        if local_date != self.current_day:
            logger.debug(f"New day detected: {local_date}. Resetting daily state.")
            self.current_day = local_date
            self.hod = self.lod = self.bos_direction = self.fvg_to_watch = None
            self.opening_range_high = self.opening_range_low = None
            self.trade_taken_today = False

        # --- Phase 1: Determine Opening Range ---
        if self.start_time <= local_time < self.opening_range_end_time:
            if self.opening_range_high is None or current_candle['close'] > self.opening_range_high:
                self.opening_range_high = current_candle['close']
            if self.opening_range_low is None or current_candle['close'] < self.opening_range_low:
                self.opening_range_low = current_candle['close']
            return None

        # --- Lock in HOD/LOD and Check Trading Window ---
        if self.hod is None and local_time >= self.opening_range_end_time:
            self.hod = self.opening_range_high
            self.lod = self.opening_range_low
            if self.hod and self.lod:
                logger.info(f"Opening range complete for {local_date}. HOD={self.hod:.2f}, LOD={self.lod:.2f}")
            else:
                logger.warning(f"Could not determine opening range for {local_date}. Skipping day.")
                self.trade_taken_today = True
        
        if not (self.opening_range_end_time <= local_time < self.end_time) or self.hod is None or self.trade_taken_today:
            return None

        # --- State 1: Awaiting Break of Structure (BOS) ---
        if self.bos_direction is None:
            if current_candle['close'] > self.hod:
                self.bos_direction = 'up'
                logger.info(f"BOS CONFIRMED (UP) at {current_candle.name} (Close {current_candle['close']:.2f} > HOD {self.hod:.2f})")
            elif current_candle['close'] < self.lod:
                self.bos_direction = 'down'
                logger.info(f"BOS CONFIRMED (DOWN) at {current_candle.name} (Close {current_candle['close']:.2f} < LOD {self.lod:.2f})")
            return None # Wait for next candle to check for FVG

        # --- State 2: BOS Confirmed, Awaiting FVG ---
        if self.bos_direction and self.fvg_to_watch is None:
            direction = 'long' if self.bos_direction == 'up' else 'short'
            fvg_low, fvg_high, stop_loss = self._find_fvg(index, direction)
            
            if fvg_low is not None:
                self.fvg_to_watch = {
                    'type': direction,
                    'top': fvg_high,
                    'bottom': fvg_low,
                    'sl': stop_loss
                }
                logger.info(f"FVG WATCHING after {self.bos_direction} BOS: {self.fvg_to_watch}")
            else:
                logger.debug("No FVG found after BOS. Resetting to look for another BOS.")
                self.bos_direction = None # Reset to look for another BOS
            return None # Wait for price to tap into FVG

        # --- State 3: FVG Found, Awaiting Price Entry ---
        if self.fvg_to_watch:
            entry_price = None
            fvg_top = self.fvg_to_watch['top']
            fvg_bottom = self.fvg_to_watch['bottom']

            # Check if price has tapped the FVG zone
            if self.fvg_to_watch['type'] == 'long' and current_candle['low'] <= fvg_top:
                entry_price = fvg_top  # Enter at the top of the bullish FVG for a more conservative entry
                logger.info(f"FVG TAPPED for LONG at {current_candle.name}. Entry: {entry_price:.2f}")
            elif self.fvg_to_watch['type'] == 'short' and current_candle['high'] >= fvg_bottom:
                entry_price = fvg_bottom  # Enter at the bottom of the bearish FVG for a more conservative entry
                logger.info(f"FVG TAPPED for SHORT at {current_candle.name}. Entry: {entry_price:.2f}")

            if entry_price:
                signal = self._generate_signal(entry_price, self.fvg_to_watch, index)
                if signal:
                    self.trade_taken_today = True  # Set flag only on successful signal generation
                self.fvg_to_watch = None # Consume the FVG
                return signal

        return None

    def _generate_signal(self, entry_price: float, fvg_details: Dict, index: int) -> Optional[Dict]:
        """Generates a trade signal with risk management and ADX trend strength filtering."""
        stop_loss = fvg_details['sl']
        direction = fvg_details['type']
        current_adx = self.data.iloc[index]['ADX_14']
        timestamp = self.data.index[index]
        ny_time = timestamp.tz_convert('America/New_York')

        # --- Session Filter (8am-12pm NY Time) ---
        if not (8 <= ny_time.hour < 12):
            logger.info(f"Skipping signal; Time {ny_time.strftime('%H:%M')} is outside the 8am-12pm NY session.")
            return None

        # --- ADX Trend Strength Filter ---
        if current_adx < 25:
            logger.info(f"Skipping signal; ADX ({current_adx:.2f}) is below 25, indicating weak trend.")
            return None
        
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share == 0:
            logger.warning("Risk per share is zero. Cannot generate signal.")
            return None

        # Calculate Take Profit
        if direction == 'long':
            take_profit = entry_price + (risk_per_share * self.params['reward_ratio'])
        else: # short
            take_profit = entry_price - (risk_per_share * self.params['reward_ratio'])

        # Calculate Position Size
        risk_amount = (self.params['risk_per_trade'] / 100.0) * self.account_balance
        position_size = risk_amount / risk_per_share

        signal = {
            'action': 'buy' if direction == 'long' else 'sell',
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'size': position_size,
            'direction': direction,
            'timestamp': self.data.iloc[index].name,
        }
        logger.info(f"Generated Signal: {signal}")
        return signal
        """Get the list of required columns for the strategy."""
        return super().get_required_columns() + ['rsi', 'atr', 'volume_ma', 
                                              'bos_up', 'bos_down', 
                                              'fvg_bullish', 'fvg_bearish']
