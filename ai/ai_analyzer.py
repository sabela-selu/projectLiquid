from .providers import AIProvider

class AIAnalyzer:
    """Analyzes trading signals using a configurable AI provider."""
    def __init__(self, provider: AIProvider):
        self.provider = provider

    def get_trade_confidence(self, market_data: str, trade_signal: dict) -> int:
        """
        Uses the configured AI provider to get a confidence score for a trade.

        Args:
            market_data: A string representation of recent market data.
            trade_signal: A dictionary containing the details of the trade signal.

        Returns:
            An integer representing the confidence score (e.g., 1-100).
        """
        return self.provider.get_confidence_score(market_data, trade_signal)
