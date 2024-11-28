
from typing import Dict
from .base_strategy import BaseStrategy
from crypto_trading_bot.core.exchange_handler import ExchangeHandler
from crypto_trading_bot.core.risk_manager import RiskManager
from crypto_trading_bot.utils.logger import BotLogger
import pandas as pd

import numpy as np

class ScalpingStrategy(BaseStrategy):
    def __init__(self, symbol: str, config: Dict, exchange_handler: ExchangeHandler = None, risk_manager: RiskManager = None):
        super().__init__(symbol, config)
        self.exchange_handler = exchange_handler
        self.risk_manager = risk_manager
        self.last_price = None
        self.position = 0
        self.profit_threshold = config.get('profit_threshold', 0.015)  # 1.5% profit target
        self.stop_loss_threshold = config.get('stop_loss_threshold', 0.03)  # 3% stop loss
        self.max_position_size = config.get('max_position_size', 1000)  # Maximum position size
        self.logger = BotLogger().get_logger()
        self.rapid_change_threshold = 0.08  # 8% threshold for rapid price changes
        self.last_log_time = None
        self.log_interval = pd.Timedelta(minutes=5)
        self.trades_per_day = 0
        self.max_trades_per_day = config.get('max_trades_per_day', 50)  # Limit the number of trades per day
        self.volatility_window = config.get('volatility_window', 20)
        self.volatility_threshold = config.get('volatility_threshold', 0.02)
        self.price_history = []

    def process(self, data: Dict) -> Dict:
        current_price = data['close']
        current_time = data.get('timestamp', pd.Timestamp.now())

        self.logger.debug(f"Processing - Current price: {current_price}, Position: {self.position}")

        if self.last_price is None:
            self.last_price = current_price
            return None

        price_change = (current_price - self.last_price) / self.last_price

        # Check for rapid price changes
        if abs(price_change) > self.rapid_change_threshold:
            if self.last_log_time is None or current_time - self.last_log_time >= self.log_interval:
                self.logger.warning(f"Rapid price change detected: {price_change:.2%}")
                self.last_log_time = current_time
            return None  # Skip trading on rapid price changes

        action = None
        if self.position == 0 and self.trades_per_day < self.max_trades_per_day:
            if abs(price_change) > self.profit_threshold:
                position_size = self.calculate_position_size(current_price)
                if price_change > 0:
                    action = {'side': 'buy', 'amount': position_size, 'symbol': self.symbol}
                else:
                    action = {'side': 'sell', 'amount': position_size, 'symbol': self.symbol}
                self.trades_per_day += 1
                self.logger.debug(f"Opening new position: {action}")
        elif self.position != 0:
            if (self.position > 0 and price_change > self.profit_threshold) or                (self.position < 0 and price_change < -self.profit_threshold) or                abs(price_change) > self.stop_loss_threshold:
                sell_amount = min(abs(self.position), self.max_position_size)
                action = {'side': 'sell' if self.position > 0 else 'buy', 'amount': sell_amount, 'symbol': self.symbol}
                self.logger.debug(f"Closing position: {action}")

        self.last_price = current_price
        return action

    def calculate_position_size(self, price: float) -> float:
        if self.risk_manager:
            return min(self.risk_manager.calculate_position_size(price, price * (1 - self.stop_loss_threshold)), self.max_position_size)
        else:
            # Simplified position sizing for backtesting
            return min(100 / price, self.max_position_size)  # Assume we're willing to risk $100 per trade, but not more than max_position_size

    def update_position(self, amount: float, side: str):
        if side == 'buy':
            self.position += amount
        elif side == 'sell':
            self.position -= amount
        self.logger.debug(f"Position updated: {self.position}")

    async def open_long_position(self, amount: float):
        try:
            order = await self.exchange_handler.create_market_buy_order(self.symbol, amount)
            self.update_position(amount, 'buy')
            self.logger.info(f"Opened long position: {order}")
        except Exception as e:
            self.logger.error(f"Error opening long position: {e}")

    async def open_short_position(self, amount: float):
        try:
            order = await self.exchange_handler.create_market_sell_order(self.symbol, amount)
            self.update_position(amount, 'sell')
            self.logger.info(f"Opened short position: {order}")
        except Exception as e:
            self.logger.error(f"Error opening short position: {e}")

    async def close_position(self):
        try:
            if self.position > 0:
                order = await self.exchange_handler.create_market_sell_order(self.symbol, abs(self.position))
            else:
                order = await self.exchange_handler.create_market_buy_order(self.symbol, abs(self.position))
            self.logger.info(f"Closed position: {order}")
            self.position = 0
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
