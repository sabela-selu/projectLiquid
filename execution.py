"""
Advanced Trade Execution Module
-----------------------------
Handles order execution, position management, and risk controls.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
import time

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Order:
    """Represents a trading order."""
    symbol: str
    side: OrderSide
    order_type: OrderType
    amount: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    params: Dict = field(default_factory=dict)
    id: Optional[str] = None
    status: str = "open"
    filled: float = 0.0
    remaining: float = 0.0
    cost: float = 0.0
    fee: Dict = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    datetime: str = field(default_factory=lambda: pd.Timestamp.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert order to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.value,
            'type': self.order_type.value,
            'amount': self.amount,
            'price': self.price,
            'stop_price': self.stop_price,
            'status': self.status,
            'filled': self.filled,
            'remaining': self.remaining,
            'cost': self.cost,
            'fee': self.fee,
            'timestamp': self.timestamp,
            'datetime': self.datetime
        }

class ExecutionEngine:
    """Handles order execution with advanced risk controls."""
    
    def __init__(self, exchange, max_position_size: float = 0.1, max_daily_loss: float = 0.02):
        """Initialize execution engine.
        
        Args:
            exchange: CCXT exchange instance
            max_position_size: Maximum position size as fraction of portfolio
            max_daily_loss: Maximum daily loss as fraction of portfolio
        """
        self.exchange = exchange
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.positions = {}
        self.orders = {}
        self.trade_history = []
        self.daily_pnl = 0.0
        self.daily_starting_balance = 0.0
        self._order_counter = 0
        
    def calculate_position_size(self, entry_price: float, stop_loss: float, risk_pct: float = 0.01) -> float:
        """Calculate position size based on risk parameters.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_pct: Percentage of portfolio to risk (0-1)
            
        Returns:
            Position size in base currency
        """
        balance = self.get_balance()
        risk_amount = balance * risk_pct
        
        # Calculate position size based on stop loss
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share <= 0:
            return 0.0
            
        position_size = risk_amount / risk_per_share
        
        # Apply position size limits
        max_size = balance * self.max_position_size / entry_price
        return min(position_size, max_size)
    
    def get_balance(self) -> float:
        """Get available balance in quote currency."""
        # In a real implementation, this would fetch from exchange
        return 10000  # Default for paper trading
    
    def create_order(self, symbol: str, order_type: OrderType, side: OrderSide, 
                    amount: float, price: Optional[float] = None, 
                    stop_price: Optional[float] = None, params: Optional[Dict] = None) -> Order:
        """Create a new order.
        
        Args:
            symbol: Trading pair symbol
            order_type: Type of order (market, limit, etc.)
            side: buy or sell
            amount: Order amount in base currency
            price: Limit price (for limit orders)
            stop_price: Stop price (for stop orders)
            params: Additional parameters
            
        Returns:
            Order object
        """
        order = Order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            amount=amount,
            price=price,
            stop_price=stop_price,
            params=params or {}
        )
        
        # Generate order ID (in real implementation, this would come from exchange)
        self._order_counter += 1
        order.id = f"order_{self._order_counter}"
        
        # Store order
        self.orders[order.id] = order
        
        # In paper trading, execute immediately
        if order_type == OrderType.MARKET:
            self.execute_order(order)
            
        return order
    
    def execute_order(self, order: Order) -> bool:
        """Execute an order (simulated for paper trading).
        
        Args:
            order: Order to execute
            
        Returns:
            bool: True if execution was successful
        """
        # In a real implementation, this would call the exchange API
        # For paper trading, we'll simulate execution
        
        # Get current price (in real trading, this would be the execution price)
        ticker = self.exchange.fetch_ticker(order.symbol)
        
        # Simulate execution
        order.filled = order.amount
        order.remaining = 0
        order.status = 'closed'
        order.price = ticker['last']  # Use last price for simulation
        order.cost = order.filled * order.price
        
        # Calculate fees (simplified)
        order.fee = {
            'currency': order.symbol.split('/')[1],
            'cost': order.cost * 0.001,  # 0.1% fee
            'rate': 0.001
        }
        
        # Update position
        self._update_position(order)
        
        # Add to trade history
        self.trade_history.append(order)
        
        return True
    
    def _update_position(self, order: Order):
        """Update position based on filled order."""
        symbol = order.symbol
        if symbol not in self.positions:
            self.positions[symbol] = {
                'amount': 0.0,
                'cost': 0.0,
                'entry_price': 0.0,
                'realized_pnl': 0.0,
                'unrealized_pnl': 0.0,
                'leverage': 1.0
            }
            
        position = self.positions[symbol]
        
        if order.side == OrderSide.BUY:
            # Calculate new average entry price
            total_cost = (position['amount'] * position['entry_price']) + (order.filled * order.price)
            total_amount = position['amount'] + order.filled
            position['entry_price'] = total_cost / total_amount if total_amount > 0 else 0
            position['amount'] += order.filled
            position['cost'] += order.cost
        else:  # SELL
            # Calculate P&L for the closed portion
            pnl = (order.price - position['entry_price']) * order.filled
            position['realized_pnl'] += pnl
            position['amount'] -= order.filled
            position['cost'] = position['amount'] * position['entry_price']
            
            # Update daily P&L
            self.daily_pnl += pnl
            
            # Remove position if fully closed
            if abs(position['amount']) < 1e-8:  # Account for floating point errors
                del self.positions[symbol]
    
    def check_risk_limits(self) -> bool:
        """Check if any risk limits have been breached.
        
        Returns:
            bool: True if within limits, False if limits breached
        """
        # Check daily loss limit
        if self.daily_pnl < -abs(self.daily_starting_balance * self.max_daily_loss):
            return False
            
        # Check position size limits
        for symbol, pos in self.positions.items():
            if abs(pos['amount'] * pos['entry_price']) > self.get_balance() * self.max_position_size:
                return False
                
        return True
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for a symbol."""
        return self.positions.get(symbol)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders, optionally filtered by symbol."""
        return [
            order for order in self.orders.values()
            if order.status == 'open' and (symbol is None or order.symbol == symbol)
        ]
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order."""
        if order_id in self.orders and self.orders[order_id].status == 'open':
            self.orders[order_id].status = 'canceled'
            return True
        return False
    
    def cancel_all_orders(self, symbol: Optional[str] = None) -> List[bool]:
        """Cancel all open orders, optionally filtered by symbol."""
        canceled = []
        for order_id, order in list(self.orders.items()):
            if order.status == 'open' and (symbol is None or order.symbol == symbol):
                canceled.append(self.cancel_order(order_id))
        return canceled
