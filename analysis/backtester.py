
import pandas as pd
import numpy as np
from typing import Dict, List
from strategies.base_strategy import BaseStrategy
from portfolio_management.portfolio import Portfolio
from portfolio_management.risk_management import RiskManager
from utils.logging_config import setup_logging

class Backtester:
    def __init__(self, strategy: BaseStrategy, initial_balance: float, risk_params: Dict):
        self.logger = setup_logging()
        self.strategy = strategy
        self.portfolio = Portfolio(initial_balance)
        self.risk_manager = RiskManager(**risk_params)

    def run(self, historical_data: pd.DataFrame) -> Dict:
        self.logger.info("Starting backtesting...")
        results = []
        for index, row in historical_data.iterrows():
            signals = self.strategy.generate_signals(historical_data.loc[:index])
            for signal in signals:
                if self.risk_manager.check_risk(signal, self.portfolio):
                    order = self.execute_trade(signal, row['close'])
                    self.portfolio.update(order)
            
            portfolio_value = self.portfolio.get_total_value({'close': row['close']})
            results.append({
                'timestamp': index,
                'close': row['close'],
                'portfolio_value': portfolio_value
            })

        performance_metrics = self.calculate_performance_metrics(results)
        self.logger.info(f"Backtesting completed. Performance metrics: {performance_metrics}")
        return performance_metrics

    def execute_trade(self, signal: Dict, current_price: float) -> Dict:
        amount = self.risk_manager.calculate_position_size(
            self.portfolio.balance,
            0.02,  # risk per trade (2% of balance)
            current_price,
            self.risk_manager.calculate_stop_loss(current_price, signal['type'])
        )

        return {
            'symbol': signal['symbol'],
            'side': 'buy' if signal['type'] == 'BUY' else 'sell',
            'amount': amount,
            'price': current_price
        }

    def calculate_performance_metrics(self, results: List[Dict]) -> Dict:
        df = pd.DataFrame(results)
        df['returns'] = df['portfolio_value'].pct_change()

        total_return = (df['portfolio_value'].iloc[-1] - df['portfolio_value'].iloc[0]) / df['portfolio_value'].iloc[0]
        sharpe_ratio = np.sqrt(252) * df['returns'].mean() / df['returns'].std()
        max_drawdown = (df['portfolio_value'] / df['portfolio_value'].cummax() - 1).min()
        
        # Calculate win rate
        trades = self.portfolio.get_trade_history()
        winning_trades = [trade for trade in trades if trade['profit'] > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0

        # Calculate profit factor
        gross_profit = sum([trade['profit'] for trade in winning_trades])
        losing_trades = [trade for trade in trades if trade['profit'] <= 0]
        gross_loss = abs(sum([trade['profit'] for trade in losing_trades]))
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')

        # Calculate average trade
        avg_trade = np.mean([trade['profit'] for trade in trades]) if trades else 0

        # Calculate maximum consecutive losses
        trade_results = [1 if trade['profit'] > 0 else 0 for trade in trades]
        max_consecutive_losses = max(sum(1 for _ in group) for key, group in itertools.groupby(trade_results) if key == 0)

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(trades),
            'avg_trade': avg_trade,
            'max_consecutive_losses': max_consecutive_losses,
            'final_portfolio_value': df['portfolio_value'].iloc[-1]
        }

    def optimize_parameters(self, historical_data: pd.DataFrame, param_grid: Dict) -> Dict:
        best_params = {}
        best_performance = float('-inf')

        for params in self._generate_param_combinations(param_grid):
            self.strategy.set_parameters(**params)
            performance = self.run(historical_data)
            
            if performance['total_return'] > best_performance:
                best_performance = performance['total_return']
                best_params = params

        self.logger.info(f"Optimization completed. Best parameters: {best_params}")
        return best_params

    def _generate_param_combinations(self, param_grid: Dict):
        keys = param_grid.keys()
        values = param_grid.values()
        for combination in itertools.product(*values):
            yield dict(zip(keys, combination))

if __name__ == "__main__":
    # Example usage
    from strategies.example_strategy import ExampleStrategy
    import pandas as pd

    # Load historical data (you would need to implement this)
    historical_data = pd.read_csv("path_to_your_historical_data.csv")

    strategy = ExampleStrategy(symbol='BTC/USDT')
    backtester = Backtester(
        strategy,
        initial_balance=10000,
        risk_params={'max_position_size': 0.1, 'stop_loss_pct': 0.02, 'take_profit_pct': 0.04}
    )

    results = backtester.run(historical_data)
    print(f"Backtesting results: {results}")

    # Optimize strategy parameters
    param_grid = {
        'ema_short': range(5, 21),
        'ema_long': range(20, 51),
    }
    best_params = backtester.optimize_parameters(historical_data, param_grid)
    print(f"Best parameters: {best_params}")
