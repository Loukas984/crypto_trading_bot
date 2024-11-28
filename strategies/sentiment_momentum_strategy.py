
from strategies.base_strategy import BaseStrategy
from indicators.macd import MACD
from indicators.rsi import RSI
from analysis.sentiment_analysis import SentimentAnalyzer
import numpy as np
import pandas as pd
from utils.error_handling import error_handler, StrategyError
from utils.logging_config import setup_logging

class SentimentMomentumStrategy(BaseStrategy):
    def __init__(self, config):
        self.required_parameters = ['macd_fast', 'macd_slow', 'macd_signal', 'rsi_period', 'sentiment_threshold', 'risk_per_trade', 'macd_threshold', 'rsi_overbought', 'rsi_oversold']
        super().__init__(config)
        self.logger = setup_logging()
        self.set_parameters(config)

    def set_parameters(self, params):
        try:
            missing_params = [param for param in self.required_parameters if param not in params]
            if missing_params:
                raise StrategyError(f"Missing required parameters: {', '.join(missing_params)}")
            super().set_parameters(params)
            if all(param in self.parameters for param in ['macd_fast', 'macd_slow', 'macd_signal', 'rsi_period']):
                self.macd = MACD(fast_period=self.parameters['macd_fast'], slow_period=self.parameters['macd_slow'], signal_period=self.parameters['macd_signal'])
                self.rsi = RSI(period=self.parameters['rsi_period'])
            self.logger.info(f"Parameters set: {self.parameters}")
        except Exception as e:
            self.logger.error(f"Error setting parameters: {str(e)}")
            raise

    def update_parameters(self):
        # Ajuster les paramètres en fonction de la volatilité
        self.parameters['risk_per_trade'] *= (1 / (1 + self.volatility))
        self.parameters['sentiment_threshold'] *= (1 + self.volatility)

    @error_handler
    async def analyze(self, symbol, timeframe, latest_data, sentiment_score):
        if not latest_data:
            raise ValueError("No data provided for analysis")
        
        df = pd.DataFrame(latest_data)
        close_prices = df['close'].values
        macd, signal, _ = self.macd.calculate(close_prices)
        rsi = self.rsi.calculate(close_prices)

        return {
            'symbol': symbol,
            'close': float(df['close'].iloc[-1]),
            'timestamp': df['timestamp'].iloc[-1],
            'macd': float(macd[-1]),
            'signal': float(signal[-1]),
            'rsi': float(rsi[-1]),
            'sentiment': sentiment_score,
            'atr': float(self.calculate_atr(df['high'].values, df['low'].values, close_prices))
        }

    @error_handler
    async def generate_signal(self, analysis_result):
        macd_crossover = analysis_result['macd'] - analysis_result['signal']
        
        if (macd_crossover > self.parameters['macd_threshold'] and 
            analysis_result['rsi'] < self.parameters['rsi_overbought'] and 
            analysis_result['sentiment'] > self.parameters['sentiment_threshold']):
            return {
                'type': 'BUY',
                'symbol': analysis_result['symbol'],
                'price': analysis_result['close'],
                'metadata': analysis_result
            }
        elif (macd_crossover < -self.parameters['macd_threshold'] and 
              analysis_result['rsi'] > self.parameters['rsi_oversold'] and 
              analysis_result['sentiment'] < -self.parameters['sentiment_threshold']):
            return {
                'type': 'SELL',
                'symbol': analysis_result['symbol'],
                'price': analysis_result['close'],
                'metadata': analysis_result
            }
        return None

    def calculate_position_size(self, account_balance):
        return min(account_balance * self.parameters['risk_per_trade'], account_balance * 0.02)  # Max 2% of account balance per trade

    def set_stop_loss(self, entry_price, position_type):
        return entry_price * (0.97 if position_type == 'BUY' else 1.03)  # 3% stop-loss

    def set_take_profit(self, entry_price, position_type):
        return entry_price * (1.06 if position_type == 'BUY' else 0.94)  # 6% take-profit

    def calculate_atr(self, high, low, close, period=14):
        high_low = high - low
        high_close = np.abs(high - np.roll(close, 1))
        low_close = np.abs(low - np.roll(close, 1))
        ranges = np.max([high_low, high_close, low_close], axis=0)
        return np.mean(ranges[-period:])
