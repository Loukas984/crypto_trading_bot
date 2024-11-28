
from typing import Dict
import pandas as pd

class Portfolio:
    def __init__(self, initial_balance: float):
        self.positions: Dict[str, float] = {}
        self.balance: float = initial_balance
        self.trade_history: list = []
        self.value_history: list = [initial_balance]

    def update_status(self, exchange_data):
        total_value = self.balance
        for symbol, amount in self.positions.items():
            latest_price = exchange_data.get_latest_price(symbol)
            if latest_price is not None:
                total_value += amount * latest_price
        self.trade_history.append({'timestamp': pd.Timestamp.now(), 'total_value': total_value})
        self.value_history.append(total_value)
        
    def execute_trade(self, order):
        symbol = order['symbol']
        amount = order['amount']
        price = order['price']
        side = order['side']
        if side == 'BUY':
            cost = amount * price
            if cost <= self.balance:
                self.positions[symbol] = self.positions.get(symbol, 0) + amount
                self.balance -= cost
            else:
                raise ValueError("Insufficient balance for this trade")
        elif side == 'SELL':
            current_position = self.positions.get(symbol, 0)
            if amount <= current_position:
                self.positions[symbol] = current_position - amount
                self.balance += amount * price
            else:
                raise ValueError("Insufficient position for this trade")
        self.trade_history.append({'timestamp': pd.Timestamp.now(), 'action': side, 'symbol': symbol, 'amount': amount, 'price': price})
        self.update_value_history()

    def get_position(self, symbol):
        return self.positions.get(symbol, 0)

    def get_balance(self):
        return self.balance

    def calculate_returns(self):
        if len(self.value_history) < 2:
            return pd.Series()
        returns = pd.Series(self.value_history).pct_change()
        return returns.dropna()

    def get_total_value(self):
        return self.value_history[-1] if self.value_history else self.balance

    def calculate_drawdown(self):
        if not self.value_history:
            return 0
        peak = max(self.value_history)
        current_value = self.value_history[-1]
        return (peak - current_value) / peak

    def update_value_history(self, exchange_data=None):
        total_value = self.balance
        for symbol, amount in self.positions.items():
            if exchange_data:
                latest_price = exchange_data.get_latest_price(symbol)
            elif self.trade_history and self.trade_history[-1]['symbol'] == symbol:
                latest_price = self.trade_history[-1]['price']
            else:
                latest_price = None
            
            if latest_price is not None:
                total_value += amount * latest_price
        self.value_history.append(total_value)

    def get_metrics(self):
        returns = self.calculate_returns()
        sharpe_ratio = returns.mean() / returns.std() if len(returns) > 0 else 0
        max_drawdown = self.calculate_drawdown()
        total_return = (self.value_history[-1] / self.value_history[0]) - 1 if len(self.value_history) > 1 else 0
        
        return {
            'total_value': self.value_history[-1],
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }

    async def update(self, trade_info):
        self.execute_trade(trade_info)
        self.update_value_history()
