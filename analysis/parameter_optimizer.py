
import numpy as np
from typing import Dict, List
from strategies.base_strategy import BaseStrategy
from data.historical_data import HistoricalData
from utils.error_handling import error_handler, StrategyError

class ParameterOptimizer:
    def __init__(self, strategy: BaseStrategy, historical_data: HistoricalData):
        self.strategy = strategy
        self.historical_data = historical_data

    @error_handler
    def optimize(self, param_ranges: Dict[str, List[float]], metric: str = 'sharpe_ratio') -> Dict[str, float]:
        best_params = {}
        best_metric_value = float('-inf')

        for params in self._generate_param_combinations(param_ranges):
            try:
                self.strategy.set_parameters(params)
                performance = self._backtest(params)
                current_metric_value = performance[metric]

                if current_metric_value > best_metric_value:
                    best_metric_value = current_metric_value
                    best_params = params
            except Exception as e:
                raise StrategyError(f"Error during parameter optimization: {str(e)}")

        return best_params

    def _generate_param_combinations(self, param_ranges: Dict[str, List[float]]):
        keys, values = zip(*param_ranges.items())
        for combination in np.array(np.meshgrid(*values)).T.reshape(-1, len(keys)):
            yield dict(zip(keys, combination))

    @error_handler
    def _backtest(self, params: Dict[str, float]) -> Dict[str, float]:
        self.strategy.set_parameters(params)
        signals = self.strategy.generate_signals(self.historical_data.get_data())
        
        # Implement backtesting logic here
        # This is a placeholder implementation
        total_return = np.random.random()
        sharpe_ratio = np.random.random()
        max_drawdown = np.random.random()

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }
