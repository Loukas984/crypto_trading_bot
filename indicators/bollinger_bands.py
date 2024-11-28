
import numpy as np
from indicators.base_indicator import BaseIndicator

class BollingerBands(BaseIndicator):
    def __init__(self, period=20, std_dev=2):
        super().__init__()
        self.period = period
        self.std_dev = std_dev

    def calculate(self, data):
        close_prices = np.array(data)
        
        # Calculate middle band (simple moving average)
        middle_band = np.convolve(close_prices, np.ones(self.period), 'valid') / self.period

        # Calculate standard deviation
        rolling_std = np.std([close_prices[i:i+self.period] for i in range(len(close_prices)-self.period+1)], axis=1)

        # Calculate upper and lower bands
        upper_band = middle_band + (rolling_std * self.std_dev)
        lower_band = middle_band - (rolling_std * self.std_dev)

        # Pad the beginning of the bands to match the input data length
        padding = np.array([np.nan] * (len(close_prices) - len(middle_band)))
        middle_band = np.concatenate((padding, middle_band))
        upper_band = np.concatenate((padding, upper_band))
        lower_band = np.concatenate((padding, lower_band))

        return upper_band, middle_band, lower_band

    def get_signal(self, data):
        close_prices = np.array(data)
        upper_band, middle_band, lower_band = self.calculate(close_prices)

        last_close = close_prices[-1]
        last_upper = upper_band[-1]
        last_lower = lower_band[-1]

        if last_close > last_upper:
            return 'SELL'
        elif last_close < last_lower:
            return 'BUY'
        else:
            return 'NEUTRAL'

    def get_bandwidth(self, data):
        upper_band, middle_band, lower_band = self.calculate(data)
        bandwidth = (upper_band - lower_band) / middle_band
        return bandwidth

    def get_percent_b(self, data):
        close_prices = np.array(data)
        upper_band, _, lower_band = self.calculate(close_prices)
        percent_b = (close_prices - lower_band) / (upper_band - lower_band)
        return percent_b
