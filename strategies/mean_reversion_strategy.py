
from typing import Dict
from .base_strategy import BaseStrategy
from crypto_trading_bot.core.exchange_handler import ExchangeHandler
from crypto_trading_bot.core.risk_manager import RiskManager
from crypto_trading_bot.utils.logger import BotLogger
import numpy as np
import pandas as pd

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, symbol: str, config: Dict, exchange_handler: ExchangeHandler = None, risk_manager: RiskManager = None):
        super().__init__(symbol, config)
        self.exchange_handler = exchange_handler
        self.risk_manager = risk_manager
        self.window_size = config.get('window_size', 60)  # 30 minutes (60 * 30 seconds)
        self.std_dev_threshold = config.get('std_dev_threshold', 2.0)
        self.max_position_size = config.get('max_position_size', 1000)  # Maximum position size
        self.position = 0
        self.prices = []
        self.logger = BotLogger().get_logger()
        self.rapid_change_threshold = 0.08  # 8% threshold for rapid price changes
        self.last_log_time = None
        self.log_interval = pd.Timedelta(minutes=5)
        self.trades_per_day = 0
        self.max_trades_per_day = config.get('max_trades_per_day', 50)  # Limit the number of trades per day

    def process(self, data: Dict) -> Dict:
        current_price = data['close']
        current_time = data.get('timestamp', pd.Timestamp.now())
        self.prices.append(current_price)
        
        self.logger.debug(f"Processing - Current price: {current_price}, Position: {self.position}")
        
        if len(self.prices) > self.window_size:
            self.prices.pop(0)
        
        action = None
        if len(self.prices) == self.window_size:
            mean = np.mean(self.prices)
            std_dev = np.std(self.prices)
            z_score = (current_price - mean) / std_dev

            self.logger.debug(f"Current price: {current_price}, Z-score: {z_score}")

            # Check for rapid price changes
            if len(self.prices) > 1:
                price_change = (current_price - self.prices[-2]) / self.prices[-2]
                if abs(price_change) > self.rapid_change_threshold:
                    if self.last_log_time is None or current_time - self.last_log_time >= self.log_interval:
                        self.logger.warning(f"Rapid price change detected: {price_change:.2%}")
                        self.last_log_time = current_time
                    return None  # Skip trading on rapid price changes

            if self.position == 0 and self.trades_per_day < self.max_trades_per_day:
                if z_score > self.std_dev_threshold:
                    # Price is high, consider selling
                    position_size = self.calculate_position_size(current_price)
                    action = {'side': 'sell', 'amount': position_size, 'symbol': self.symbol}
                    self.trades_per_day += 1
                    self.logger.debug(f"Opening short position: {action}")
                elif z_score < -self.std_dev_threshold:
                    # Price is low, consider buying
                    position_size = self.calculate_position_size(current_price)
                    action = {'side': 'buy', 'amount': position_size, 'symbol': self.symbol}
                    self.trades_per_day += 1
                    self.logger.debug(f"Opening long position: {action}")
            elif self.position != 0:
                # Check if we should close the position
                if (self.position > 0 and z_score >= 0) or (self.position < 0 and z_score <= 0):
                    close_amount = min(abs(self.position), self.max_position_size)
                    action = {'side': 'sell' if self.position > 0 else 'buy', 'amount': close_amount, 'symbol': self.symbol}
                    self.logger.debug(f"Closing position: {action}")

        return action

    def calculate_position_size(self, price: float) -> float:
        if self.risk_manager:
            return min(self.risk_manager.calculate_position_size(price, price * 0.98), self.max_position_size)  # 2% stop loss
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
