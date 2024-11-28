
import numpy as np
from .base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, short_window=10, long_window=50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, exchange_data):
        signals = []
        for symbol, data in exchange_data.data.items():
            if len(data) >= self.long_window:
                short_ma = np.mean(data['close'][-self.short_window:])
                long_ma = np.mean(data['close'][-self.long_window:])
                
                last_price = data['close'].iloc[-1]
                
                if short_ma > long_ma:
                    signals.append({
                        'symbol': symbol,
                        'action': 'buy',
                        'price': last_price,
                        'amount': 1  # This should be calculated based on available balance and risk management
                    })
                elif short_ma < long_ma:
                    signals.append({
                        'symbol': symbol,
                        'action': 'sell',
                        'price': last_price,
                        'amount': 1  # This should be calculated based on current position
                    })
        
        return signals
