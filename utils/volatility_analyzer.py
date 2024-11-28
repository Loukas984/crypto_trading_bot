
import numpy as np
from typing import Dict, List

class VolatilityAnalyzer:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.price_history: List[float] = []
        self.current_volatility: float = 0.0

    def update(self, latest_data: Dict[str, Dict]):
        for symbol, data in latest_data.items():
            self.price_history.append(data['close'])
            if len(self.price_history) > self.window_size:
                self.price_history.pop(0)
            
            if len(self.price_history) >= 2:
                returns = np.diff(np.log(self.price_history))
                self.current_volatility = np.std(returns) * np.sqrt(len(returns))

    def get_current_volatility(self) -> float:
        return self.current_volatility

    def is_high_volatility(self, threshold: float = 0.02) -> bool:
        return self.current_volatility > threshold
