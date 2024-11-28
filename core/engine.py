
import asyncio
from typing import Dict, List
from core.exchange_handler import ExchangeHandler
from core.plugin_manager import PluginManager
from data.exchange_data import ExchangeData
from data.historical_data import HistoricalData
from portfolio_management.portfolio import Portfolio
from portfolio_management.risk_management import RiskManager
from utils.logging_config import setup_logging
from utils.volatility_analyzer import VolatilityAnalyzer
from analysis.parameter_optimizer import ParameterOptimizer
from utils.error_handling import error_handler, StrategyError
from strategies.grid_trading_strategy import GridTradingStrategy
from strategies.breakout_strategy import BreakoutStrategy

import asyncio
from asyncio import Queue

class TradingEngine:
    def __init__(self, config):
        self.config = config
        self.logger, _ = setup_logging()
        self.event_queue = Queue()
        self.volatility_analyzer = VolatilityAnalyzer()
        self.exchange_handler = ExchangeHandler(config['exchange'])
        self.plugin_manager = PluginManager()
        self.exchange_data = ExchangeData(self.exchange_handler)
        self.historical_data = HistoricalData(self.exchange_handler)
        self.portfolio = Portfolio(config['TRADING_PARAMS']['initial_balance'])
        self.risk_manager = RiskManager(config['RISK_MANAGEMENT'])
        
        self.strategies = []
        self.running = False
        self.data_manager = None
        self.sentiment_analyzer = None

        # Update trading pairs
        self.trading_pairs = config['TRADING_PARAMS']['symbols']

    async def initialize_historical_data(self):
        self.logger.info("Initializing historical data...")
        for symbol in self.trading_pairs:
            for timeframe in self.config['TRADING_PARAMS']['timeframes']:
                await self.historical_data.update_data(symbol, timeframe)
        self.logger.info("Historical data initialization complete.")

    def set_data_manager(self, data_manager):
        self.data_manager = data_manager
        self.logger.info("RealTimeDataManager set in TradingEngine")

    def set_sentiment_analyzer(self, sentiment_analyzer):
        self.sentiment_analyzer = sentiment_analyzer
        self.logger.info("SentimentAnalyzer set in TradingEngine")

    def set_volatility_analyzer(self, volatility_analyzer):
        self.volatility_analyzer = volatility_analyzer
        self.logger.info("VolatilityAnalyzer set in TradingEngine")

    async def start(self):
        self.logger.info("Starting trading engine...")
        self.running = True
        await self.initialize_historical_data()
        await self.load_strategies()
        await asyncio.gather(
            self.update_market_data(),
            self.run_strategies(),
            self.adjust_risk_params(),
            self.adjust_strategies_performance(),
            self.process_events()
        )

    async def adjust_risk_params(self):
        while self.running:
            volatility = self.volatility_analyzer.get_current_volatility()
            self.risk_manager.adjust_position_size(self.portfolio, volatility)
            await asyncio.sleep(300)  # Adjust every 5 minutes

    def stop(self):
        self.logger.info("Stopping trading engine...")
        self.running = False
        # Additional cleanup
        self.exchange_handler.close()
        for strategy in self.strategies:
            if hasattr(strategy, 'cleanup'):
                strategy.cleanup()
        self.logger.info("Trading engine stopped.")

    def get_available_symbols(self):
        return self.exchange_handler.get_available_symbols()

    @error_handler
    async def load_strategies(self):
        self.strategies = []  # Clear existing strategies
        for strategy_config in self.config['strategies']:
            try:
                strategy = self.plugin_manager.load_strategy(strategy_config['name'], strategy_config.get('params', {}))
                if self.config.get('optimize_parameters', False):
                    optimizer = ParameterOptimizer(strategy, self.historical_data)
                    optimized_params = optimizer.optimize(strategy_config.get('param_ranges', {}))
                    strategy.set_parameters(optimized_params)
                self.strategies.append(strategy)
            except Exception as e:
                self.logger.error(f"Error loading strategy {strategy_config['name']}: {str(e)}")
                # Continue loading other strategies instead of raising an exception

    async def update_market_data(self):
        while self.running:
            try:
                await self.exchange_data.update()
                latest_data = self.exchange_data.get_latest_data()
                self.volatility_analyzer.update(latest_data)
                self.adjust_strategies_for_volatility()
                await self.event_queue.put({"type": "market_update", "data": latest_data})
                await self.check_exceptional_market_events(latest_data)
                await asyncio.sleep(self.config['update_interval'])
            except Exception as e:
                self.logger.error(f"Error updating market data: {e}")

    async def check_exceptional_market_events(self, latest_data):
        for symbol, data in latest_data.items():
            price_change = (data['close'] - data['open']) / data['open']
            if abs(price_change) > self.config.get('exceptional_price_change_threshold', 0.1):
                await self.event_queue.put({
                    "type": "exceptional_event",
                    "data": {"symbol": symbol, "price_change": price_change}
                })

    async def adjust_strategies_performance(self):
        while self.running:
            for strategy in self.strategies:
                performance = strategy.get_performance()
                if performance < self.config.get('strategy_performance_threshold', 0):
                    new_params = self.optimize_strategy_parameters(strategy)
                    strategy.set_parameters(new_params)
            await asyncio.sleep(self.config.get('strategy_adjustment_interval', 3600))

    def optimize_strategy_parameters(self, strategy):
        optimizer = ParameterOptimizer(strategy, self.historical_data)
        return optimizer.optimize(strategy.get_parameter_ranges())

    def get_config(self):
        return {
            "strategy": self.strategies[0].__class__.__name__ if self.strategies else None,
            "active": self.running,
            "strategy_params": self.strategies[0].get_parameters() if self.strategies else {},
            "risk_params": self.risk_manager.get_parameters(),
            "global_params": {
                "Trading Frequency (seconds)": self.config['TRADING_PARAMS'].get('update_interval', 60),
                "Update Interval (seconds)": self.config['TRADING_PARAMS'].get('update_interval', 1),
                "Strategy Interval (seconds)": self.config['TRADING_PARAMS'].get('strategy_interval', 5),
                "Optimize Parameters": self.config.get('optimize_parameters', False)
            }
        }

    def update_config(self, new_config: Dict):
        strategy_name = new_config['strategy']
        strategy_params = new_config['strategy_params']
        risk_params = new_config['risk_params']
        global_params = new_config['global_params']

        # Update risk management parameters
        self.risk_manager.update_parameters(risk_params)
        
        # Update strategy parameters
        for strategy in self.strategies:
            if strategy.__class__.__name__ == strategy_name:
                strategy.set_parameters(strategy_params)
                self.logger.info(f"Updated configuration for {strategy_name}")
                break
        else:
            self.logger.warning(f"Strategy {strategy_name} not found")

        # Update global parameters
        self.config['TRADING_PARAMS']['update_interval'] = global_params['Update Interval (seconds)']
        self.config['TRADING_PARAMS']['strategy_interval'] = global_params['Strategy Interval (seconds)']
        self.config['optimize_parameters'] = global_params['Optimize Parameters']

        # Update config dictionary
        for strategy_config in self.config['strategies']:
            if strategy_config['name'] == strategy_name:
                strategy_config['params'] = strategy_params
                break
        
        self.config['RISK_MANAGEMENT'].update(risk_params)
        
        self.logger.info("Strategy, risk management, and global configuration updated")

    async def refresh_data(self):
        self.logger.info("Refreshing market data...")
        try:
            await self.exchange_data.update()
            await self.historical_data.update()
            self.portfolio.update_status(self.exchange_data)
            self.volatility_analyzer.update(self.exchange_data.get_latest_data())
            latest_data = self.exchange_data.get_latest_data()
            await self.event_queue.put({"type": "market_update", "data": latest_data})
            await self.check_exceptional_market_events(latest_data)
            self.logger.info("Market data refreshed successfully")
        except Exception as e:
            self.logger.error(f"Error refreshing market data: {str(e)}")
            raise

    async def process_events(self):
        while self.running:
            event = await self.event_queue.get()
            if event['type'] == 'market_update':
                await self.handle_market_update(event['data'])
            elif event['type'] == 'trade_signal':
                await self.handle_trade_signal(event['data'])
            self.event_queue.task_done()

    async def handle_market_update(self, market_data):
        for strategy in self.strategies:
            await strategy.on_market_update(market_data)

    async def handle_trade_signal(self, signal):
        if self.risk_manager.check_risk(signal, self.portfolio):
            order = await self.exchange_handler.place_order(signal)
            if order:
                self.portfolio.update(order)
                self.logger.info(f"Order placed: {order}")

    def adjust_strategies_for_volatility(self):
        current_volatility = self.volatility_analyzer.get_current_volatility()
        for strategy in self.strategies:
            if hasattr(strategy, 'adjust_for_volatility'):
                strategy.adjust_for_volatility(current_volatility)
            if hasattr(strategy, 'update_parameters'):
                strategy.update_parameters()
        
        # Adjust risk parameters based on volatility
        if self.config['RISK_MANAGEMENT'].get('volatility_adjustment', False):
            volatility_factor = max(0.5, min(2, 1 / current_volatility))
            self.risk_manager.update_parameters({
                'max_position_size': self.config['RISK_MANAGEMENT']['max_position_size'] * volatility_factor,
                'stop_loss_pct': self.config['RISK_MANAGEMENT']['stop_loss_pct'] * volatility_factor,
                'take_profit_pct': self.config['RISK_MANAGEMENT']['take_profit_pct'] * volatility_factor
            })

    async def run_strategies(self):
        while self.running:
            for strategy in self.strategies:
                try:
                    for symbol in strategy.symbols:
                        latest_data = self.data_manager.get_latest_data(symbol)
                        historical_data = await self.get_historical_data(symbol, strategy.timeframe)
                        sentiment_score = await self.sentiment_analyzer.analyze(symbol)
                        analysis_result = await strategy.analyze(symbol, strategy.timeframe, historical_data + latest_data, sentiment_score)
                        signal = await strategy.generate_signal(analysis_result)
                        if signal and self.risk_manager.check_risk(signal, self.portfolio):
                            order = await self.execute_trade(signal)
                            if order:
                                self.portfolio.update(order)
                except Exception as e:
                    self.logger.error(f"Error in strategy {strategy.__class__.__name__}: {e}")
            await asyncio.sleep(self.config['strategy_interval'])

    async def execute_trade(self, signal: Dict) -> Dict:
        try:
            strategy = next(s for s in self.strategies if signal['symbol'] in s.symbols)
            position_size = strategy.calculate_position_size(self.portfolio.get_balance())
            atr = signal['metadata']['atr']
            stop_loss = strategy.set_stop_loss(signal['price'], signal['type'], atr)
            take_profit = strategy.set_take_profit(signal['price'], signal['type'], atr)
            
            order = await self.exchange_handler.place_order(
                symbol=signal['symbol'],
                side=signal['type'],
                amount=position_size,
                price=signal['price'],
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            self.logger.info(f"Executed trade: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return None

    async def get_historical_data(self, symbol: str, timeframe: str, limit: int = 100):
        return await self.historical_data.get_candles(symbol, timeframe, limit)

    def get_performance_metrics(self):
        return self.portfolio.get_metrics()

if __name__ == "__main__":
    # Example configuration
    config = {
        'exchange': {'name': 'binance', 'api_key': 'your_api_key', 'secret_key': 'your_secret_key'},
        'initial_balance': 10000,
        'risk_params': {'max_position_size': 0.02, 'stop_loss_pct': 0.01, 'take_profit_pct': 0.03},
        'strategies': [
            {'name': 'ScalpingStrategy', 'params': {'rsi_period': 14, 'rsi_overbought': 70, 'rsi_oversold': 30}},
            {'name': 'MomentumStrategy', 'params': {'ema_fast': 12, 'ema_slow': 26, 'macd_signal': 9}}
        ],
        'update_interval': 1,  # seconds
        'strategy_interval': 5  # seconds
    }

    engine = TradingEngine(config)
    asyncio.run(engine.start())
