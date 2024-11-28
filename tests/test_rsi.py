
import unittest
import numpy as np
from indicators.rsi import RSI

class TestRSI(unittest.TestCase):
    def setUp(self):
        self.rsi = RSI(period=14)

    def test_rsi_calculation_basic(self):
        # Test with a simple price series
        prices = np.array([10, 11, 12, 11, 10, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
        rsi_values = self.rsi.calculate(prices)
        self.assertEqual(len(rsi_values), len(prices))
        self.assertTrue(all(0 <= rsi <= 100 for rsi in rsi_values))

    def test_rsi_calculation_constant_price(self):
        # Test with constant price (should result in RSI = 50)
        prices = np.array([10] * 20)
        rsi_values = self.rsi.calculate(prices)
        self.assertTrue(all(rsi == 50 for rsi in rsi_values[14:]))

    def test_rsi_calculation_increasing_price(self):
        # Test with consistently increasing price (should result in high RSI)
        prices = np.array(range(1, 21))
        rsi_values = self.rsi.calculate(prices)
        self.assertTrue(all(rsi > 70 for rsi in rsi_values[14:]))

    def test_rsi_calculation_decreasing_price(self):
        # Test with consistently decreasing price (should result in low RSI)
        prices = np.array(range(20, 0, -1))
        rsi_values = self.rsi.calculate(prices)
        self.assertTrue(all(rsi < 30 for rsi in rsi_values[14:]))

    def test_rsi_calculation_zero_price(self):
        # Test with zero prices (edge case)
        prices = np.array([0] * 20)
        rsi_values = self.rsi.calculate(prices)
        self.assertTrue(all(np.isnan(rsi) for rsi in rsi_values))

    def test_get_signal(self):
        # Test the get_signal method
        prices = np.array([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])
        signal = self.rsi.get_signal(prices)
        self.assertIn(signal, ['BUY', 'SELL', 'NEUTRAL'])

    def test_rsi_calculation_alternating_prices(self):
        # Test with alternating prices
        prices = np.array([10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10])
        rsi_values = self.rsi.calculate(prices)
        self.assertTrue(all(45 < rsi < 55 for rsi in rsi_values[14:]))

    def test_rsi_calculation_single_price_change(self):
        # Test with a single price change
        prices = np.array([10] * 13 + [11] * 7)
        rsi_values = self.rsi.calculate(prices)
        self.assertTrue(rsi_values[-1] > 50)

    def test_rsi_calculation_negative_prices(self):
        # Test with negative prices
        prices = np.array([-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4])
        rsi_values = self.rsi.calculate(prices)
        self.assertTrue(all(0 <= rsi <= 100 for rsi in rsi_values))

    def test_rsi_calculation_large_numbers(self):
        # Test with very large numbers
        prices = np.array([1e9, 2e9, 3e9, 4e9, 5e9, 6e9, 7e9, 8e9, 9e9, 1e10, 1.1e10, 1.2e10, 1.3e10, 1.4e10, 1.5e10])
        rsi_values = self.rsi.calculate(prices)
        self.assertTrue(all(0 <= rsi <= 100 for rsi in rsi_values))

if __name__ == '__main__':
    unittest.main()
