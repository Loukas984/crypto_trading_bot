
from strategies.base_strategy import BaseStrategy
from indicators.macd import MACD
from indicators.adx import ADX

class MomentumStrategy(BaseStrategy):
    def __init__(self, config, exchange_data, historical_data, portfolio):
        super().__init__(config, exchange_data, historical_data, portfolio)
        self.macd = MACD(fast_period=self.config['macd_fast'], slow_period=self.config['macd_slow'], signal_period=self.config['macd_signal'])
        self.adx = ADX(period=self.config['adx_period'])
        self.adx_threshold = self.config['adx_threshold']
        self.risk_per_trade = self.config['risk_per_trade']
        
    async def analyze(self, symbol, timeframe):
        data = await self.historical_data.get_candles(symbol, timeframe)
        close_prices = [candle['close'] for candle in data]
        high_prices = [candle['high'] for candle in data]
        low_prices = [candle['low'] for candle in data]
        
        macd_line, signal_line, _ = self.macd.calculate(close_prices)
        adx_values = self.adx.calculate(high_prices, low_prices, close_prices)
        
        return {
            'macd_line': macd_line,
            'signal_line': signal_line,
            'adx_values': adx_values,
            'close_prices': close_prices,
            'timestamp': data[-1]['timestamp']
        }

    async def generate_signal(self, analysis_result):
        macd_line = analysis_result['macd_line']
        signal_line = analysis_result['signal_line']
        adx_values = analysis_result['adx_values']
        close_prices = analysis_result['close_prices']
        timestamp = analysis_result['timestamp']

        if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2] and adx_values[-1] > self.adx_threshold:
            return {
                'type': 'BUY',
                'symbol': self.symbol,
                'price': close_prices[-1],
                'timestamp': timestamp,
                'metadata': {
                    'macd': macd_line[-1],
                    'signal': signal_line[-1],
                    'adx': adx_values[-1]
                }
            }
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2] and adx_values[-1] > self.adx_threshold:
            return {
                'type': 'SELL',
                'symbol': self.symbol,
                'price': close_prices[-1],
                'timestamp': timestamp,
                'metadata': {
                    'macd': macd_line[-1],
                    'signal': signal_line[-1],
                    'adx': adx_values[-1]
                }
            }
        return None

    def calculate_position_size(self, account_balance):
        return min(account_balance * self.risk_per_trade, account_balance * 0.02)  # Max 2% of account balance per trade

    def set_stop_loss(self, entry_price, position_type):
        return entry_price * (0.98 if position_type == 'BUY' else 1.02)  # 2% stop-loss

    def set_take_profit(self, entry_price, position_type):
        return entry_price * (1.04 if position_type == 'BUY' else 0.96)  # 4% take-profit

    def update_parameters(self):
        self.adx_threshold *= (2 - self.volatility)
        self.risk_per_trade *= (1 / (1 + self.volatility))
