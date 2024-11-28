
from typing import Dict
from .base_strategy import BaseStrategy
from core.exchange_handler import ExchangeHandler
from portfolio_management.risk_management import RiskManager
from utils.logging_config import setup_logging
import pandas as pd
import numpy as np

class BreakoutStrategy(BaseStrategy):
    def __init__(self, symbol: str, config: Dict, exchange_handler: ExchangeHandler = None, risk_manager: RiskManager = None):
        super().__init__(symbol, config)
        self.exchange_handler = exchange_handler
        self.risk_manager = risk_manager
        self.logger = setup_logging()
        
        try:
            self.lookback_period = config.get('lookback_period', 20)
            self.breakout_threshold = config.get('breakout_threshold', 2)
            self.stop_loss_pct = config.get('stop_loss_pct', 0.02)
            self.take_profit_pct = config.get('take_profit_pct', 0.04)
            
            self.position = 0
            self.entry_price = None
            
            self.logger.info(f"BreakoutStrategy initialized with parameters: {config}")
        except Exception as e:
            self.logger.error(f"Error initializing BreakoutStrategy: {str(e)}")
            raise

    def calculate_bollinger_bands(self, data: pd.DataFrame, window: int = 20, num_std: float = 2):
        rolling_mean = data['close'].rolling(window=window).mean()
        rolling_std = data['close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band

    def process(self, data: Dict) -> Dict:
        df = pd.DataFrame(data)
        current_price = df['close'].iloc[-1]
        
        upper_band, lower_band = self.calculate_bollinger_bands(df, self.lookback_period, self.breakout_threshold)
        
        action = None
        
        if self.position == 0:
            if current_price > upper_band.iloc[-1]:
                # Bullish breakout
                action = {'side': 'buy', 'amount': self.calculate_position_size(current_price), 'symbol': self.symbol}
                self.position = 1
                self.entry_price = current_price
                self.logger.info(f"Bullish breakout detected. Buying at {current_price}")
            elif current_price < lower_band.iloc[-1]:
                # Bearish breakout
                action = {'side': 'sell', 'amount': self.calculate_position_size(current_price), 'symbol': self.symbol}
                self.position = -1
                self.entry_price = current_price
                self.logger.info(f"Bearish breakout detected. Selling at {current_price}")
        else:
            # Check for exit conditions
            if self.position > 0:
                if current_price <= self.entry_price * (1 - self.stop_loss_pct) or current_price >= self.entry_price * (1 + self.take_profit_pct):
                    action = {'side': 'sell', 'amount': abs(self.position), 'symbol': self.symbol}
                    self.position = 0
                    self.entry_price = None
                    self.logger.info(f"Closing long position at {current_price}")
            elif self.position < 0:
                if current_price >= self.entry_price * (1 + self.stop_loss_pct) or current_price <= self.entry_price * (1 - self.take_profit_pct):
                    action = {'side': 'buy', 'amount': abs(self.position), 'symbol': self.symbol}
                    self.position = 0
                    self.entry_price = None
                    self.logger.info(f"Closing short position at {current_price}")
        
        return action

    def calculate_position_size(self, price: float) -> float:
        if self.risk_manager:
            return self.risk_manager.calculate_position_size(price, price * self.stop_loss_pct)
        else:
            # Simplified position sizing
            return 100 / price  # Assume we're willing to risk $100 per trade

    async def execute_trade(self, action: Dict):
        try:
            if action['side'] == 'buy':
                order = await self.exchange_handler.create_market_buy_order(self.symbol, action['amount'])
            else:
                order = await self.exchange_handler.create_market_sell_order(self.symbol, action['amount'])
            self.logger.info(f"Executed {action['side']} order: {order}")
        except Exception as e:
            self.logger.error(f"Error executing {action['side']} order: {e}")

