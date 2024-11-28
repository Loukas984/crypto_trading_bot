
import aiohttp
import json
from utils.logging_config import setup_logging

class SentimentAnalyzer:
    def __init__(self):
        self.logger = setup_logging()
        self.api_endpoint = "https://api.example.com/sentiment"  # Remplacez par une vraie API de sentiment

    async def analyze(self, symbol: str) -> float:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_endpoint}?symbol={symbol}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['sentiment_score']
                    else:
                        self.logger.error(f"Failed to get sentiment for {symbol}. Status: {response.status}")
                        return 0.0
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment for {symbol}: {str(e)}")
            return 0.0

    # Méthode de fallback si l'API n'est pas disponible
    def get_mock_sentiment(self, symbol: str) -> float:
        import random
        return random.uniform(-1, 1)
