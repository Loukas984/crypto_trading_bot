
from typing import Dict

class RiskManager:
    def __init__(self, config: Dict):
        self.max_position_size = config.get('max_position_size', 100)  # in USDT
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.01)  # 1% of account balance
        self.max_open_positions = config.get('max_open_positions', 3)
        self.account_balance = 0

    async def update_account_balance(self, balance: float):
        self.account_balance = balance

    async def calculate_position_size(self, price: float, stop_loss: float) -> float:
        risk_amount = self.account_balance * self.max_risk_per_trade
        position_size = risk_amount / (price - stop_loss)
        return min(position_size, self.max_position_size / price)

    async def can_open_position(self, open_positions: int) -> bool:
        return open_positions < self.max_open_positions

    async def validate_order(self, order_size: float, current_exposure: float) -> bool:
        return (current_exposure + order_size) <= (self.account_balance * self.max_risk_per_trade)
