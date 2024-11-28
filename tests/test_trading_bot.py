
import unittest
import asyncio
from core.engine import TradingEngine
from strategies.sentiment_momentum_strategy import SentimentMomentumStrategy
from strategies.grid_trading_strategy import GridTradingStrategy
from strategies.breakout_strategy import BreakoutStrategy
from portfolio_management.risk_management import RiskManager
from utils.volatility_analyzer import VolatilityAnalyzer

class TestTradingBot(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.config = {
            'exchange': {
                'name': 'binance',
                'api_key': 'test_api_key',
                'secret_key': 'test_secret_key'
            },
            'TRADING_PARAMS': {
                'symbols': ['BTC/USDT', 'ETH/USDT'],
                'initial_balance': 10000,
                'update_interval': 1,
                'strategy_interval': 5
            },
            'RISK_MANAGEMENT': {
                'max_position_size': 0.1,
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.05
            },
            'strategies': [
                {'name': 'SentimentMomentumStrategy', 'params': {}},
                {'name': 'GridTradingStrategy', 'params': {}},
                {'name': 'BreakoutStrategy', 'params': {}}
            ]
        }
        self.engine = TradingEngine(self.config)

    async def test_engine_initialization(self):
        self.assertIsNotNone(self.engine)
        self.assertEqual(len(self.engine.strategies), 3)
        self.assertIsInstance(self.engine.risk_manager, RiskManager)
        self.assertIsInstance(self.engine.volatility_analyzer, VolatilityAnalyzer)

    async def test_strategy_loading(self):
        await self.engine.load_strategies()
        self.assertEqual(len(self.engine.strategies), 3)
        self.assertIsInstance(self.engine.strategies[0], SentimentMomentumStrategy)
        self.assertIsInstance(self.engine.strategies[1], GridTradingStrategy)
        self.assertIsInstance(self.engine.strategies[2], BreakoutStrategy)

    async def test_risk_management(self):
        initial_position_size = self.engine.risk_manager.max_position_size
        await self.engine.adjust_risk_params()
        self.assertNotEqual(initial_position_size, self.engine.risk_manager.max_position_size)

    async def test_config_update(self):
        new_config = {
            'strategy': 'SentimentMomentumStrategy',
            'active': True,
            'strategy_params': {'rsi_period': 14, 'rsi_overbought': 70, 'rsi_oversold': 30},
            'risk_params': {'max_position_size': 0.05, 'stop_loss_pct': 0.03, 'take_profit_pct': 0.06},
            'global_params': {'Trading Frequency (seconds)': 30, 'Update Interval (seconds)': 2, 'Strategy Interval (seconds)': 10, 'Optimize Parameters': True}
        }
        self.engine.update_config(new_config)
        updated_config = self.engine.get_config()
        self.assertEqual(updated_config['strategy'], 'SentimentMomentumStrategy')
        self.assertEqual(updated_config['risk_params']['max_position_size'], 0.05)
        self.assertEqual(updated_config['global_params']['Update Interval (seconds)'], 2)

    async def test_market_data_update(self):
        await self.engine.update_market_data()
        self.assertIsNotNone(self.engine.exchange_data.get_latest_data())

    async def test_strategy_execution(self):
        # Run strategies for a short period
        asyncio.create_task(self.engine.run_strategies())
        await asyncio.sleep(1)  # Wait for 1 second to allow strategies to run

        # Check if any trade signals were added to the event queue
        while not self.engine.event_queue.empty():
            event = await self.engine.event_queue.get()
            if event['type'] == 'trade_signal':
                self.assertIsNotNone(event['data'])
                return  # Test passes if we find at least one trade signal

        self.fail("No trade signals were generated")

    async def test_error_handling(self):
        with self.assertRaises(Exception):
            await self.engine.execute_trade(None)

    async def test_portfolio_update(self):
        initial_balance = self.engine.portfolio.get_total_value()
        # Simulate a trade
        await self.engine.portfolio.update({'symbol': 'BTC/USDT', 'side': 'buy', 'amount': 0.1, 'price': 50000})
        updated_balance = self.engine.portfolio.get_total_value()
        self.assertNotEqual(initial_balance, updated_balance)

if __name__ == '__main__':
    asyncio.run(unittest.main())
