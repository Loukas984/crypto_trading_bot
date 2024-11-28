
import asyncio
import ccxt.async_support as ccxt
from typing import Dict
from utils.logging_config import setup_logging

class ExchangeHandler:
    def __init__(self, exchange_config: Dict):
        self.logger = setup_logging()
        self.exchange_name = exchange_config['name']
        self.exchange = getattr(ccxt, self.exchange_name)({
            'apiKey': exchange_config['api_key'],
            'secret': exchange_config['secret_key'],
            'enableRateLimit': True,
        })
        self.markets = {}
        self.rate_limiter = asyncio.Semaphore(10)  # Limit to 10 requests per second

    async def initialize(self):
        self.logger.info(f"Initializing {self.exchange_name} exchange handler")
        self.markets = await self.exchange.load_markets()

    async def get_ticker(self, symbol: str) -> Dict:
        async with self.rate_limiter:
            try:
                return await self.exchange.fetch_ticker(symbol)
            except Exception as e:
                self.logger.error(f"Error fetching ticker for {symbol}: {e}")
                return {}

    async def get_order_book(self, symbol: str) -> Dict:
        async with self.rate_limiter:
            try:
                return await self.exchange.fetch_order_book(symbol)
            except Exception as e:
                self.logger.error(f"Error fetching order book for {symbol}: {e}")
                return {}

    async def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        async with self.rate_limiter:
            try:
                if price is None:
                    order = await self.exchange.create_market_order(symbol, side, amount)
                else:
                    order = await self.exchange.create_limit_order(symbol, side, amount, price)
                self.logger.info(f"Placed {side} order for {amount} {symbol} at {price}")
                return order
            except Exception as e:
                self.logger.error(f"Error placing {side} order for {symbol}: {e}")
                return {}

    async def get_balance(self) -> Dict:
        async with self.rate_limiter:
            try:
                return await self.exchange.fetch_balance()
            except Exception as e:
                self.logger.error(f"Error fetching balance: {e}")
                return {}

    async def get_open_orders(self, symbol: str = None) -> list:
        async with self.rate_limiter:
            try:
                return await self.exchange.fetch_open_orders(symbol)
            except Exception as e:
                self.logger.error(f"Error fetching open orders for {symbol}: {e}")
                return []

    async def cancel_order(self, order_id: str, symbol: str) -> Dict:
        async with self.rate_limiter:
            try:
                return await self.exchange.cancel_order(order_id, symbol)
            except Exception as e:
                self.logger.error(f"Error cancelling order {order_id} for {symbol}: {e}")
                return {}

    async def get_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = None) -> list:
        async with self.rate_limiter:
            try:
                return await self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            except Exception as e:
                self.logger.error(f"Error fetching OHLCV data for {symbol}: {e}")
                return []

    async def close(self):
        await self.exchange.close()

if __name__ == "__main__":
    # Example usage
    async def main():
        exchange_config = {
            'name': 'binance',
            'api_key': 'your_api_key',
            'secret_key': 'your_secret_key'
        }
        handler = ExchangeHandler(exchange_config)
        await handler.initialize()
        
        # Fetch ticker for BTC/USDT
        ticker = await handler.get_ticker('BTC/USDT')
        print(f"BTC/USDT ticker: {ticker}")
        
        # Place a limit buy order
        order = await handler.place_order('BTC/USDT', 'buy', 0.001, 30000)
        print(f"Placed order: {order}")
        
        await handler.close()

    asyncio.run(main())
