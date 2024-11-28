
from typing import Dict
from .base_strategy import BaseStrategy
from core.exchange_handler import ExchangeHandler
from portfolio_management.risk_management import RiskManager
from utils.logging_config import setup_logging
import numpy as np

class GridTradingStrategy(BaseStrategy):
    def __init__(self, symbol: str, config: Dict, exchange_handler: ExchangeHandler = None, risk_manager: RiskManager = None):
        super().__init__(symbol, config)
        self.exchange_handler = exchange_handler
        self.risk_manager = risk_manager
        self.logger = setup_logging()
        
        self.grid_levels = config.get('grid_levels', 10)
        self.grid_size = config.get('grid_size', 0.01)  # 1% between each grid level
        self.total_investment = config.get('total_investment', 1000)  # Total investment in quote currency
        
        self.lower_price = None
        self.upper_price = None
        self.grid = []
        self.positions = {}

    def initialize_grid(self, current_price: float):
        self.lower_price = current_price * (1 - self.grid_size * self.grid_levels / 2)
        self.upper_price = current_price * (1 + self.grid_size * self.grid_levels / 2)
        
        self.grid = np.linspace(self.lower_price, self.upper_price, self.grid_levels)
        self.investment_per_level = self.total_investment / self.grid_levels
        
        self.logger.info(f"Grid initialized: {self.grid}")

    def process(self, data: Dict) -> Dict:
        current_price = data['close']
        
        if not self.grid:
            self.initialize_grid(current_price)
            return None
        
        action = None
        
        # Find the two closest grid levels
        lower_level = self.grid[self.grid < current_price][-1] if any(self.grid < current_price) else self.grid[0]
        upper_level = self.grid[self.grid > current_price][0] if any(self.grid > current_price) else self.grid[-1]
        
        if current_price <= lower_level and lower_level not in self.positions:
            # Buy at lower level
            amount = self.investment_per_level / current_price
            action = {'side': 'buy', 'amount': amount, 'symbol': self.symbol}
            self.positions[lower_level] = amount
            self.logger.info(f"Buying at grid level: {lower_level}")
        elif current_price >= upper_level and upper_level in self.positions:
            # Sell at upper level
            amount = self.positions[upper_level]
            action = {'side': 'sell', 'amount': amount, 'symbol': self.symbol}
            del self.positions[upper_level]
            self.logger.info(f"Selling at grid level: {upper_level}")
        
        return action

    def adjust_grid(self, current_price: float):
        if current_price < self.lower_price or current_price > self.upper_price:
            self.logger.info("Adjusting grid...")
            self.initialize_grid(current_price)

    async def execute_trade(self, action: Dict):
        try:
            if action['side'] == 'buy':
                order = await self.exchange_handler.create_market_buy_order(self.symbol, action['amount'])
            else:
                order = await self.exchange_handler.create_market_sell_order(self.symbol, action['amount'])
            self.logger.info(f"Executed {action['side']} order: {order}")
        except Exception as e:
            self.logger.error(f"Error executing {action['side']} order: {e}")

