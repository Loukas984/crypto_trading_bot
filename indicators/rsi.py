
import numpy as np
from indicators.base_indicator import BaseIndicator

class RSI(BaseIndicator):
    def __init__(self, period=14):
        super().__init__()
        self.period = period

    def calculate(self, data):
        close_prices = np.array(data, dtype=float)
        
        # Handle the case of zero prices
        if np.all(close_prices == 0):
            return np.full_like(close_prices, np.nan, dtype=float)
        
        deltas = np.diff(close_prices)
        
        # Handle the case of constant prices
        if np.all(deltas == 0):
            return np.full_like(close_prices, 50., dtype=float)
        
        seed = deltas[:self.period+1]
        up = seed[seed >= 0].sum()/self.period
        down = -seed[seed < 0].sum()/self.period
        rs = np.zeros_like(close_prices, dtype=float)
        rs[:self.period] = up / down if down != 0 else np.inf
        rsi = np.zeros_like(close_prices, dtype=float)
        rsi[:self.period] = 100. - 100./(1. + rs[:self.period])

        for i in range(self.period, len(close_prices)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(self.period-1) + upval)/self.period
            down = (down*(self.period-1) + downval)/self.period
            rs[i] = up / down if down != 0 else np.inf
            rsi[i] = 100. - 100./(1. + rs[i])

        return rsi

    def get_signal(self, data, overbought=70, oversold=30):
        rsi_values = self.calculate(data)
        last_rsi = rsi_values[-1]

        if last_rsi > overbought:
            return 'SELL'
        elif last_rsi < oversold:
            return 'BUY'
        else:
            return 'NEUTRAL'
