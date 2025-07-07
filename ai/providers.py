from abc import ABC, abstractmethod
import os
import openai

class AIProvider(ABC):
    """Abstract base class for AI providers."""
    @abstractmethod
    def get_confidence_score(self, market_data: str, trade_signal: dict) -> int:
        """Analyzes market data and a trade signal to return a confidence score."""
        pass

class OpenAICompatibleProvider(AIProvider):
    """AI Provider for OpenAI-compatible APIs like OpenRouter."""
    def __init__(self, api_key: str, model: str, base_url: str = None):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_confidence_score(self, market_data: str, trade_signal: dict) -> int:
        """Constructs a prompt and gets a confidence score from OpenAI."""
        prompt = self._build_prompt(market_data, trade_signal)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a trading analyst. Your task is to provide a confidence score from 1 to 100 for a given trade signal based on market context. CRITICAL: Your entire response must be ONLY the integer score and nothing else. Do not add any explanatory text."}, 
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=10
            )
            score_text = response.choices[0].message.content.strip()
            return int(score_text)
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return 0 # Return a neutral/error score

    def _build_prompt(self, market_data: str, trade_signal: dict) -> str:
        """Builds the prompt string to send to the LLM."""
        return f"""
        Market Context:
        {market_data}

        Trade Signal:
        - Direction: {trade_signal.get('direction')}
        - Entry Price: {trade_signal.get('entry_price')}
        - Stop Loss: {trade_signal.get('stop_loss')}
        - Take Profit: {trade_signal.get('take_profit')}

        Based on the provided market context and trade signal, what is your confidence score (1-100) for this trade's success?
        """
