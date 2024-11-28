
import unittest
from portfolio_management.portfolio import Portfolio
from data.exchange_data import ExchangeData

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio()
        self.exchange_data = ExchangeData('binance', 'dummy_api_key', 'dummy_api_secret')
        
        # Add some sample data to exchange_data
        import pandas as pd
        self.exchange_data.data['BTC/USDT'] = pd.DataFrame({
            'close': [10000, 10100, 10200, 10300, 10400]
        })

    def test_execute_trade(self):
        self.portfolio.balance = 10000
        self.portfolio.execute_trade({'symbol': 'BTC/USDT', 'action': 'buy', 'amount': 1, 'price': 10000})
        self.assertEqual(self.portfolio.positions['BTC/USDT'], 1)
        self.assertEqual(self.portfolio.balance, 0)

    def test_update_status(self):
        self.portfolio.positions['BTC/USDT'] = 1
        self.portfolio.balance = 0
        self.portfolio.update_status(self.exchange_data)
        self.assertGreater(len(self.portfolio.value_history), 0)

    def test_calculate_returns(self):
        self.portfolio.positions['BTC/USDT'] = 1
        self.portfolio.balance = 0
        self.portfolio.update_status(self.exchange_data)
        self.portfolio.update_status(self.exchange_data)  # Call twice to have two data points
        returns = self.portfolio.calculate_returns()
        self.assertIsNotNone(returns)

    def test_calculate_drawdown(self):
        self.portfolio.positions['BTC/USDT'] = 1
        self.portfolio.balance = 0
        self.portfolio.update_status(self.exchange_data)
        drawdown = self.portfolio.calculate_drawdown()
        self.assertGreaterEqual(drawdown, 0)
        self.assertLess(drawdown, 1)

if __name__ == '__main__':
    unittest.main()
