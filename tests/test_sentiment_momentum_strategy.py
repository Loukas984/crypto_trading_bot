
import asynctest
from unittest.mock import Mock, patch
import numpy as np
from strategies.sentiment_momentum_strategy import SentimentMomentumStrategy
from utils.error_handling import StrategyError

class TestSentimentMomentumStrategy(asynctest.TestCase):
    def setUp(self):
        self.config = {
            'symbols': ['BTC/USDT'],
            'timeframe': '1h',
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'sentiment_threshold': 0.2,
            'macd_threshold': 0.05,
            'risk_per_trade': 0.01
        }
        self.strategy = SentimentMomentumStrategy(self.config)

    @patch('strategies.sentiment_momentum_strategy.MACD')
    @patch('strategies.sentiment_momentum_strategy.RSI')
    async def test_analyze(self, mock_rsi, mock_macd):
        mock_macd.return_value.calculate.return_value = (np.array([38.0, 39.0]), np.array([6.0, 7.0]), np.array([32.0, 32.0]))
        mock_rsi.return_value.calculate.return_value = np.array([100.0, 100.0])

        latest_data = [
            {'timestamp': 1625097600, 'open': 33000, 'high': 34000, 'low': 32000, 'close': 33500, 'volume': 1000},
            {'timestamp': 1625101200, 'open': 33500, 'high': 34500, 'low': 33000, 'close': 34000, 'volume': 1200}
        ]
        sentiment_score = 0.5

        result = await self.strategy.analyze('BTC/USDT', '1h', latest_data, sentiment_score)

        self.assertEqual(result['symbol'], 'BTC/USDT')
        self.assertEqual(result['close'], 34000)
        self.assertEqual(result['macd'], 39.0)
        self.assertEqual(result['signal'], 7.0)
        self.assertEqual(result['rsi'], 100.0)
        self.assertEqual(result['sentiment'], 0.5)
        self.assertIn('atr', result)

    async def test_generate_signal_buy(self):
        analysis_result = {
            'symbol': 'BTC/USDT',
            'close': 34000,
            'macd': 0.2,
            'signal': 0.15,
            'rsi': 50,
            'sentiment': 0.3
        }

        signal = await self.strategy.generate_signal(analysis_result)

        self.assertIsNotNone(signal)
        self.assertEqual(signal['type'], 'BUY')
        self.assertEqual(signal['symbol'], 'BTC/USDT')
        self.assertEqual(signal['price'], 34000)
        self.assertEqual(signal['metadata'], analysis_result)

    async def test_generate_signal_sell(self):
        analysis_result = {
            'symbol': 'BTC/USDT',
            'close': 34000,
            'macd': 0.1,
            'signal': 0.2,
            'rsi': 80,
            'sentiment': -0.3
        }

        signal = await self.strategy.generate_signal(analysis_result)

        self.assertIsNotNone(signal)
        self.assertEqual(signal['type'], 'SELL')
        self.assertEqual(signal['symbol'], 'BTC/USDT')
        self.assertEqual(signal['price'], 34000)
        self.assertEqual(signal['metadata'], analysis_result)

    async def test_generate_signal_no_trade(self):
        analysis_result = {
            'symbol': 'BTC/USDT',
            'close': 34000,
            'macd': 0.15,
            'signal': 0.15,
            'rsi': 50,
            'sentiment': 0
        }

        signal = await self.strategy.generate_signal(analysis_result)

        self.assertIsNone(signal)

    def test_calculate_position_size(self):
        account_balance = 10000
        position_size = self.strategy.calculate_position_size(account_balance)
        self.assertEqual(position_size, 100)  # 1% of account balance

    def test_set_stop_loss(self):
        entry_price = 34000
        stop_loss_buy = self.strategy.set_stop_loss(entry_price, 'BUY')
        stop_loss_sell = self.strategy.set_stop_loss(entry_price, 'SELL')
        self.assertEqual(stop_loss_buy, 32980)  # 3% below entry price
        self.assertEqual(stop_loss_sell, 35020)  # 3% above entry price

    def test_set_take_profit(self):
        entry_price = 34000
        take_profit_buy = self.strategy.set_take_profit(entry_price, 'BUY')
        take_profit_sell = self.strategy.set_take_profit(entry_price, 'SELL')
        self.assertEqual(take_profit_buy, 36040)  # 6% above entry price
        self.assertEqual(take_profit_sell, 31960)  # 6% below entry price

    def test_update_parameters(self):
        initial_risk = self.strategy.parameters['risk_per_trade']
        initial_sentiment = self.strategy.parameters['sentiment_threshold']
        self.strategy.volatility = 0.5
        self.strategy.update_parameters()
        self.assertLess(self.strategy.parameters['risk_per_trade'], initial_risk)
        self.assertGreater(self.strategy.parameters['sentiment_threshold'], initial_sentiment)

    @patch('strategies.sentiment_momentum_strategy.MACD')
    @patch('strategies.sentiment_momentum_strategy.RSI')
    async def test_analyze_with_empty_data(self, mock_rsi, mock_macd):
        mock_macd.return_value.calculate.return_value = (np.array([]), np.array([]), np.array([]))
        mock_rsi.return_value.calculate.return_value = np.array([])

        latest_data = []
        sentiment_score = 0.5

        with self.assertRaises(ValueError):
            await self.strategy.analyze('BTC/USDT', '1h', latest_data, sentiment_score)

    def test_calculate_atr(self):
        high = np.array([10, 12, 15])
        low = np.array([8, 9, 11])
        close = np.array([9, 11, 14])
        atr = self.strategy.calculate_atr(high, low, close, period=3)
        expected_atr = (4 + 3 + 6) / 3  # (12-8, 12-9, 15-11) = (4, 3, 4)
        self.assertAlmostEqual(atr, expected_atr, places=2)

    def test_set_parameters_missing_param(self):
        config = self.config.copy()
        del config['macd_fast']
        with self.assertRaises(StrategyError):
            strategy = SentimentMomentumStrategy(config)
            strategy.set_parameters(config)  # Explicitly call set_parameters

if __name__ == '__main__':
    asynctest.main()
