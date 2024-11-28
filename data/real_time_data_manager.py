
import asyncio
from typing import List, Dict
from core.exchange_handler import ExchangeHandler
from utils.logging_config import setup_logging

class RealTimeDataManager:
    def __init__(self, exchange_handler: ExchangeHandler, symbols: List[str]):
        self.logger = setup_logging()
        self.exchange_handler = exchange_handler
        self.symbols = symbols
        self.running = False
        self.latest_data: Dict[str, Dict] = {}

    async def start(self):
        self.logger.info("Démarrage du gestionnaire de données en temps réel")
        self.running = True
        while self.running:
            try:
                for symbol in self.symbols:
                    data = await self.exchange_handler.fetch_ticker(symbol)
                    self.latest_data[symbol] = data
                    self.logger.debug(f"Données en temps réel pour {symbol}: {data}")
                await asyncio.sleep(1)  # Attendre 1 seconde avant la prochaine mise à jour
            except Exception as e:
                self.logger.error(f"Erreur lors de la récupération des données en temps réel : {e}")

    def stop(self):
        self.running = False
        self.logger.info("Arrêt du gestionnaire de données en temps réel")

    def get_latest_data(self, symbol: str) -> Dict:
        return self.latest_data.get(symbol, {})
