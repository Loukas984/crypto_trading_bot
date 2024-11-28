
import unittest
import asynctest
import asyncio

def load_tests(loader, standard_tests, pattern):
    suite = unittest.TestSuite()
    suite.addTest(asynctest.TestLoader().loadTestsFromName('tests.test_integration'))
    suite.addTest(asynctest.TestLoader().loadTestsFromName('tests.test_sentiment_momentum_strategy'))
    return suite

if __name__ == '__main__':
    runner = asynctest.TextTestRunner()
    result = runner.run(load_tests(None, None, None))
