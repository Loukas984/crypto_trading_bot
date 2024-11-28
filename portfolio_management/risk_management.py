
from typing import Dict
from utils.logging_config import setup_logging
import numpy as np
from portfolio_management.portfolio import Portfolio

class RiskManager:
    def __init__(self, config: Dict):
        self.logger = setup_logging(__name__)
        self.max_position_size = config.get('max_position_size', 0.01)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.05)
        self.take_profit_pct = config.get('take_profit_pct', 0.10)
        self.max_drawdown_pct = config.get('max_drawdown_pct', 0.2)
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.02)
        self.original_max_position_size = self.max_position_size

    def check_risk(self, signal: Dict, portfolio: 'Portfolio') -> bool:
        symbol = signal['symbol']
        current_position = portfolio.get_position(symbol)
        
        # Check if the position size respects the limit
        if current_position['amount'] + signal['amount'] > self.max_position_size:
            self.logger.warning(f"Position size limit exceeded for {symbol}")
            return False

        # Check if the trade respects the risk management rules
        if not self.check_risk_reward_ratio(signal):
            self.logger.warning(f"Risk-reward ratio not met for {symbol}")
            return False

        # Check maximum drawdown
        if self.check_max_drawdown(portfolio):
            self.logger.warning(f"Maximum drawdown reached")
            return False

        # Check if the risk per trade is within limits
        if not self.check_risk_per_trade(signal, portfolio):
            self.logger.warning(f"Risk per trade limit exceeded for {symbol}")
            return False

        return True

    def check_risk_reward_ratio(self, signal: Dict) -> bool:
        entry_price = signal['price']
        stop_loss = self.calculate_stop_loss(entry_price, signal['type'])
        take_profit = self.calculate_take_profit(entry_price, signal['type'])

        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)

        risk_reward_ratio = reward / risk
        return risk_reward_ratio >= 2  # Example of minimum risk/reward ratio

    def calculate_stop_loss(self, entry_price: float, position_type: str) -> float:
        if position_type == 'BUY':
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)

    def calculate_take_profit(self, entry_price: float, position_type: str) -> float:
        if position_type == 'BUY':
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)

    def calculate_position_size(self, account_balance: float, risk_per_trade: float, entry_price: float, stop_loss: float) -> float:
        risk_amount = account_balance * risk_per_trade
        position_size = risk_amount / abs(entry_price - stop_loss)
        return min(position_size, self.max_position_size)

    def update_trailing_stop(self, position: Dict, current_price: float) -> float:
        if position['type'] == 'BUY':
            new_stop_loss = max(position['stop_loss'], current_price * (1 - self.stop_loss_pct))
        else:
            new_stop_loss = min(position['stop_loss'], current_price * (1 + self.stop_loss_pct))
        
        return new_stop_loss

    def check_max_drawdown(self, portfolio: 'Portfolio') -> bool:
        historical_values = portfolio.get_historical_values()
        if len(historical_values) < 2:
            return False

        peak = np.maximum.accumulate(historical_values)
        drawdown = (peak - historical_values) / peak
        max_drawdown = np.max(drawdown)

        return max_drawdown > self.max_drawdown_pct

    def check_risk_per_trade(self, signal: Dict, portfolio: 'Portfolio') -> bool:
        account_balance = portfolio.get_balance()
        entry_price = signal['price']
        stop_loss = self.calculate_stop_loss(entry_price, signal['type'])
        
        risk_amount = abs(entry_price - stop_loss) * signal['amount']
        risk_percentage = risk_amount / account_balance

        return risk_percentage <= self.max_risk_per_trade

    def adjust_position_size(self, portfolio: 'Portfolio', volatility: float) -> None:
        # Adjust position size based on market volatility
        base_volatility = 0.02  # Assuming 2% as base volatility
        volatility_factor = base_volatility / volatility
        
        # Limit the adjustment factor
        volatility_factor = max(0.5, min(2, volatility_factor))
        
        new_max_position_size = self.max_position_size * volatility_factor
        
        # Limit the change in position size
        max_change = 0.2  # 20% maximum change
        new_max_position_size = max(
            min(new_max_position_size, self.max_position_size * (1 + max_change)),
            self.max_position_size * (1 - max_change)
        )
        
        self.max_position_size = new_max_position_size
        self.logger.info(f"Adjusted max position size to {self.max_position_size} based on volatility of {volatility}")
        
        # Adjust stop loss and take profit percentages
        self.stop_loss_pct = min(0.1, self.stop_loss_pct * volatility_factor)
        self.take_profit_pct = max(0.05, self.take_profit_pct / volatility_factor)
        
        self.logger.info(f"Adjusted stop loss to {self.stop_loss_pct} and take profit to {self.take_profit_pct}")

    def reset_position_size(self):
        # Reset the position size to its original value
        if hasattr(self, 'original_max_position_size'):
            self.max_position_size = self.original_max_position_size
            self.logger.info(f"Reset max position size to original value: {self.max_position_size}")
        else:
            self.logger.warning("Original max position size not set. Unable to reset.")

    def get_parameters(self):
        return {
            'max_position_size': self.max_position_size,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit_pct': self.take_profit_pct,
            'max_drawdown_pct': self.max_drawdown_pct,
            'max_risk_per_trade': self.max_risk_per_trade
        }

    def update_parameters(self, new_params: Dict):
        for param, value in new_params.items():
            if hasattr(self, param):
                setattr(self, param, value)
                self.logger.info(f"Updated {param} to {value}")
            else:
                self.logger.warning(f"Parameter {param} does not exist in RiskManager")
        
        # Update original_max_position_size if max_position_size was changed
        if 'max_position_size' in new_params:
            self.original_max_position_size = self.max_position_size
        
        self.logger.info("Risk management parameters updated")

    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        # Calculate optimal bet size using Kelly Criterion
        q = 1 - win_rate
        f = (win_rate / q) - (avg_loss / (q * avg_win))
        return max(0, min(f, 1))  # Ensure f is between 0 and 1
