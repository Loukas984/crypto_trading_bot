
import numpy as np
import pandas as pd
from strategies.base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, rsi_period=14, oversold_threshold=30, overbought_threshold=70):
        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold

    def calculate_rsi(self, data):
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def generate_signals(self, exchange_data):
        signals = []
        for symbol, data in exchange_data.data.items():
            if len(data) >= self.rsi_period:
                rsi = self.calculate_rsi(data)
                last_rsi = rsi.iloc[-1]
                last_price = data['close'].iloc[-1]

                if last_rsi < self.oversold_threshold:
                    signals.append({
                        'symbol': symbol,
                        'action': 'buy',
                        'price': last_price,
                        'amount': 1  # This should be calculated based on available balance and risk management
                    })
                elif last_rsi > self.overbought_threshold:
                    signals.append({
                        'symbol': symbol,
                        'action': 'sell',
                        'price': last_price,
                        'amount': 1  # This should be calculated based on current position
                    })

        return signals
