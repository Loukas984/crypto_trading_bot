
import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, window=20, num_std=2):
        self.window = window
        self.num_std = num_std

    def calculate_bollinger_bands(self, data):
        rolling_mean = data['close'].rolling(window=self.window).mean()
        rolling_std = data['close'].rolling(window=self.window).std()
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)
        return upper_band, lower_band

    def generate_signals(self, exchange_data):
        signals = []
        for symbol, data in exchange_data.data.items():
            print(f"Processing symbol: {symbol}")
            print(f"Data length: {len(data)}")
            if len(data) >= self.window:
                upper_band, lower_band = self.calculate_bollinger_bands(data)
                last_close = data['close'].iloc[-1]
                last_upper = upper_band.iloc[-1]
                last_lower = lower_band.iloc[-1]
                print(f"Last close: {last_close}, Upper band: {last_upper}, Lower band: {last_lower}")

                if last_close > last_upper:
                    print("Generating sell signal")
                    signals.append({
                        'symbol': symbol,
                        'action': 'sell',
                        'price': last_close,
                        'amount': 1  # This should be calculated based on available balance and risk management
                    })
                elif last_close < last_lower:
                    print("Generating buy signal")
                    signals.append({
                        'symbol': symbol,
                        'action': 'buy',
                        'price': last_close,
                        'amount': 1  # This should be calculated based on available balance and risk management
                    })
                else:
                    print("Generating hold signal")
                    signals.append({
                        'symbol': symbol,
                        'action': 'hold',
                        'price': last_close,
                        'amount': 0
                    })

        print(f"Total signals generated: {len(signals)}")
        return signals
