"""
Base Strategy Class
-----------------
Provides a common interface for all trading strategies.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd

class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, symbol: str, params: Optional[Dict[str, Any]] = None):
        """
        Initialize the strategy.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            params: Dictionary of strategy parameters
        """
        self.symbol = symbol
        self.params = params or {}
        self.initialized = False
        self.data = None
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the strategy with any required setup."""
        pass
    
    @abstractmethod
    def evaluate(self, data: pd.Series) -> Optional[Dict]:
        """
        Evaluate the current market conditions and return trading signals.
        
        Args:
            data: Current market data point
            
        Returns:
            dict: Trading signal with 'action' and other parameters
        """
        pass
    
    def update_params(self, params: Dict[str, Any]) -> None:
        """
        Update strategy parameters.
        
        Args:
            params: Dictionary of parameters to update
        """
        self.params.update(params)
    
    def set_data(self, data: pd.DataFrame) -> None:
        """
        Set the historical data for the strategy.
        
        Args:
            data: DataFrame with historical market data
        """
        self.data = data
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                              risk_percent: float = 1.0, account_balance: float = 10000.0) -> float:
        """
        Calculate position size based on risk parameters.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_percent: Risk as percentage of account balance
            account_balance: Current account balance
            
        Returns:
            float: Position size in base currency
        """
        if entry_price == stop_loss:
            return 0.0
            
        risk_amount = account_balance * (risk_percent / 100)
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return 0.0
            
        return risk_amount / risk_per_share
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, 
                                   take_profit: float) -> float:
        """
        Calculate the risk/reward ratio for a trade.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            float: Risk/reward ratio
        """
        if entry_price == stop_loss:
            return 0.0
            
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk == 0:
            return 0.0
            
        return reward / risk
    
    def get_required_columns(self) -> list:
        """
        Get the list of required columns for the strategy.
        
        Returns:
            list: List of required column names
        """
        return ['open', 'high', 'low', 'close', 'volume']
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that the provided data has all required columns.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        required_cols = set(self.get_required_columns())
        data_cols = set(data.columns)
        return required_cols.issubset(data_cols)
