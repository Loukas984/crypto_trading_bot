
import unittest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from strategies.moving_average_strategy import MovingAverageStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.bollinger_bands_strategy import BollingerBandsStrategy
from strategies.ema_crossover_strategy import EMACrossoverStrategy
from data.exchange_data import ExchangeData
from portfolio_management.portfolio import Portfolio
from portfolio_management.risk_management import RiskManager

class TestStrategies(unittest.TestCase):
    def setUp(self):
        # Create sample data for testing with both upward and downward trends
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        close_prices = [100]
        for i in range(1, 100):
            if i < 50:
                close_prices.append(close_prices[-1] + np.random.randint(-1, 3))  # Upward trend
            else:
                close_prices.append(close_prices[-1] + np.random.randint(-3, 1))  # Downward trend
        
        self.sample_data = pd.DataFrame({
            'open': close_prices,
            'high': [x + 5 for x in close_prices],
            'low': [x - 5 for x in close_prices],
            'close': close_prices,
            'volume': np.random.randint(1000, 2000, 100)
        }, index=dates)

        self.exchange_data = ExchangeData('binance', 'dummy_api_key', 'dummy_api_secret')
        self.exchange_data.data['BTC/USDT'] = self.sample_data
        self.portfolio = Portfolio()
        self.portfolio.balance = 1000  # Set initial balance
        self.risk_manager = RiskManager()

    def test_moving_average_strategy(self):
        strategy = MovingAverageStrategy()
        signals = strategy.generate_signals(self.exchange_data)
        self.assertIsInstance(signals, list)
        self.assertTrue(len(signals) > 0)

    def test_rsi_strategy(self):
        strategy = RSIStrategy()
        signals = strategy.generate_signals(self.exchange_data)
        self.assertIsInstance(signals, list)
        self.assertTrue(len(signals) > 0)

    def test_bollinger_bands_strategy(self):
        strategy = BollingerBandsStrategy()
        signals = strategy.generate_signals(self.exchange_data)
        self.assertIsInstance(signals, list)
        self.assertTrue(len(signals) > 0)

    def test_ema_crossover_strategy(self):
        strategy = EMACrossoverStrategy(short_window=5, long_window=10)
        signals = strategy.generate_signals(self.exchange_data)
        self.assertIsInstance(signals, list)
        self.assertTrue(len(signals) > 0, "No signals were generated")
        
        # Check if we have both buy and sell signals
        actions = [signal['action'] for signal in signals]
        self.assertIn('buy', actions, "No buy signals were generated")
        self.assertIn('sell', actions, "No sell signals were generated")
        
        # Check if the signals are properly formatted
        for signal in signals:
            self.assertIn('symbol', signal)
            self.assertIn('action', signal)
            self.assertIn('price', signal)
            self.assertIn('amount', signal)

    def test_portfolio(self):
        # Simulate buying at a high price
        self.portfolio.execute_trade({'symbol': 'BTC/USDT', 'action': 'buy', 'amount': 1, 'price': 200})
        self.assertEqual(self.portfolio.get_position('BTC/USDT'), 1)
        self.portfolio.update_status(self.exchange_data)
        
        # Simulate a price drop
        self.exchange_data.data['BTC/USDT'].loc[self.exchange_data.data['BTC/USDT'].index[-1], 'close'] = 180
        self.portfolio.update_status(self.exchange_data)
        
        self.assertTrue(len(self.portfolio.value_history) > 0)
        self.assertGreater(self.portfolio.calculate_drawdown(), 0)
        
        # Test other portfolio methods
        self.assertIsInstance(self.portfolio.calculate_returns(), pd.Series)
        self.assertGreater(self.portfolio.get_total_value(self.exchange_data), 0)

    def test_risk_management(self):
        signal = {'symbol': 'BTC/USDT', 'action': 'buy', 'amount': 1, 'price': 100}
        self.assertTrue(self.risk_manager.check_risk(signal, self.portfolio, self.exchange_data))
        position_size = self.risk_manager.get_position_size('BTC/USDT')
        self.assertIsInstance(position_size, float)
        self.assertGreater(position_size, 0)

if __name__ == '__main__':
    unittest.main()
