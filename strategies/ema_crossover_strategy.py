
import logging
import pandas as pd
from strategies.base_strategy import BaseStrategy
from indicators.technical_indicators import calculate_ema

class EMACrossoverStrategy(BaseStrategy):
    def __init__(self, short_window=12, long_window=26):
        self.short_window = short_window
        self.long_window = long_window
        self.logger = logging.getLogger(__name__)

    def generate_signals(self, exchange_data):
        signals = []
        for symbol, data in exchange_data.data.items():
            self.logger.info(f"Generating signals for {symbol}")
            self.logger.info(f"Data length: {len(data)}")
            if len(data) >= self.long_window:
                short_ema = calculate_ema(data['close'], self.short_window)
                long_ema = calculate_ema(data['close'], self.long_window)
                
                # Calculate the EMA crossover
                crossover = pd.Series(short_ema > long_ema, index=data.index)
                crossover_changes = crossover.diff()
                
                self.logger.info(f"Last short EMA: {short_ema.iloc[-1]}, Last long EMA: {long_ema.iloc[-1]}")
                
                # Generate buy signal when short EMA crosses above long EMA
                buy_signals = crossover_changes[crossover_changes == True]
                for timestamp in buy_signals.index:
                    signals.append({
                        'symbol': symbol,
                        'action': 'buy',
                        'price': data.loc[timestamp, 'close'],
                        'amount': 1  # This should be calculated based on available balance and risk management
                    })
                    self.logger.info(f"Generated buy signal for {symbol} at {timestamp}")
                
                # Generate sell signal when short EMA crosses below long EMA
                sell_signals = crossover_changes[crossover_changes == False]
                for timestamp in sell_signals.index:
                    signals.append({
                        'symbol': symbol,
                        'action': 'sell',
                        'price': data.loc[timestamp, 'close'],
                        'amount': 1  # This should be calculated based on current position
                    })
                    self.logger.info(f"Generated sell signal for {symbol} at {timestamp}")
            else:
                self.logger.warning(f"Not enough data for {symbol} to generate signals")
        
        self.logger.info(f"Total signals generated: {len(signals)}")
        return signals
