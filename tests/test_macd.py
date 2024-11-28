
import unittest
import numpy as np
from indicators.macd import MACD

class TestMACD(unittest.TestCase):
    def setUp(self):
        self.macd = MACD(fast_period=12, slow_period=26, signal_period=9)

    def test_macd_calculation_basic(self):
        # Test with a simple price series
        prices = np.array([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30])
        macd_line, signal_line, histogram = self.macd.calculate(prices)
        self.assertEqual(len(macd_line), len(prices))
        self.assertEqual(len(signal_line), len(prices))
        self.assertEqual(len(histogram), len(prices))

    def test_macd_calculation_constant_price(self):
        # Test with constant price (should result in MACD close to zero)
        prices = np.array([10] * 50)
        macd_line, signal_line, histogram = self.macd.calculate(prices)
        self.assertTrue(all(abs(m) < 1e-6 for m in macd_line[26:]))
        self.assertTrue(all(abs(s) < 1e-6 for s in signal_line[34:]))
        self.assertTrue(all(abs(h) < 1e-6 for h in histogram[34:]))

    def test_macd_calculation_increasing_price(self):
        # Test with consistently increasing price
        prices = np.array(range(1, 51))
        macd_line, signal_line, histogram = self.macd.calculate(prices)
        self.assertTrue(all(m > 0 for m in macd_line[26:]))

    def test_macd_calculation_decreasing_price(self):
        # Test with consistently decreasing price
        prices = np.array(range(50, 0, -1))
        macd_line, signal_line, histogram = self.macd.calculate(prices)
        self.assertTrue(all(m < 0 for m in macd_line[26:]))

    def test_macd_calculation_alternating_prices(self):
        # Test with alternating prices
        prices = np.array([10, 11, 10, 11, 10, 11] * 10)
        macd_line, signal_line, histogram = self.macd.calculate(prices)
        self.assertTrue(all(abs(m) < 1 for m in macd_line[26:]))

    def test_macd_calculation_negative_prices(self):
        # Test with negative prices
        prices = np.array([-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4] * 4)
        macd_line, signal_line, histogram = self.macd.calculate(prices)
        self.assertEqual(len(macd_line), len(prices))
        self.assertEqual(len(signal_line), len(prices))
        self.assertEqual(len(histogram), len(prices))

    def test_macd_calculation_large_numbers(self):
        # Test with very large numbers
        prices = np.array([1e9, 2e9, 3e9, 4e9, 5e9, 6e9, 7e9, 8e9, 9e9, 1e10] * 6)
        macd_line, signal_line, histogram = self.macd.calculate(prices)
        self.assertEqual(len(macd_line), len(prices))
        self.assertEqual(len(signal_line), len(prices))
        self.assertEqual(len(histogram), len(prices))

if __name__ == '__main__':
    unittest.main()
