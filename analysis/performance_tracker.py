
import pandas as pd
import numpy as np

class PerformanceTracker:
    def __init__(self):
        self.trades = []
        self.portfolio_values = []

    def add_trade(self, timestamp, symbol, action, amount, price):
        self.trades.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'action': action,
            'amount': amount,
            'price': price
        })

    def add_portfolio_value(self, timestamp, value):
        self.portfolio_values.append({
            'timestamp': timestamp,
            'value': value
        })

    def calculate_returns(self):
        df = pd.DataFrame(self.portfolio_values)
        df['returns'] = df['value'].pct_change()
        return df['returns']

    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        returns = self.calculate_returns()
        excess_returns = returns - risk_free_rate/252  # Assuming daily returns
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def calculate_max_drawdown(self):
        df = pd.DataFrame(self.portfolio_values)
        df['cummax'] = df['value'].cummax()
        df['drawdown'] = (df['cummax'] - df['value']) / df['cummax']
        return df['drawdown'].max()

    def generate_report(self):
        returns = self.calculate_returns()
        sharpe_ratio = self.calculate_sharpe_ratio()
        max_drawdown = self.calculate_max_drawdown()
        
        report = {
            'total_return': (self.portfolio_values[-1]['value'] / self.portfolio_values[0]['value']) - 1,
            'annualized_return': (1 + returns.mean())**252 - 1,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(self.trades),
            'winning_trades': sum(1 for trade in self.trades if trade['action'] == 'sell' and trade['price'] > trade['price']),
            'losing_trades': sum(1 for trade in self.trades if trade['action'] == 'sell' and trade['price'] < trade['price'])
        }
        
        return report
