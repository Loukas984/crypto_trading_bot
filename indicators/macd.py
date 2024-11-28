
from indicators.base_indicator import BaseIndicator
import pandas as pd

import numpy as np

class MACD(BaseIndicator):
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, close_prices):
        # Convert to numpy array if it's not already
        close_prices = np.array(close_prices)
        
        # Calculate EMAs
        fast_ema = self.ema(close_prices, self.fast_period)
        slow_ema = self.ema(close_prices, self.slow_period)
        
        # Calculate MACD line
        macd_line = fast_ema - slow_ema
        
        # Calculate signal line
        signal_line = self.ema(macd_line, self.signal_period)
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram

    def ema(self, data, period):
        alpha = 2 / (period + 1)
        ema = np.zeros_like(data)
        ema[0] = data[0]
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
        return ema
