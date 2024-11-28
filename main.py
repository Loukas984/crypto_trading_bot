
import asyncio
import tkinter as tk
from gui.main_window import MainWindow
from core.engine import TradingEngine
from utils.logging_config import setup_logging
from utils.security import APIKeyManager
from utils.password_manager import PasswordManager
from analysis.sentiment_analysis import SentimentAnalyzer
from data.real_time_data_manager import RealTimeDataManager
from utils.error_handling import error_handler, APIError, StrategyError, DataError
from analysis.volatility_analyzer import VolatilityAnalyzer
import threading
from config import EXCHANGE, TRADING_PARAMS, RISK_MANAGEMENT, STRATEGIES, LOGGING

async def run_async_tasks(engine, data_manager):
    await asyncio.gather(
        engine.start(),
        data_manager.start(),
        engine.adjust_strategies_performance(),
        engine.process_events()
    )

@error_handler
async def main():
    # Setup logging
    logger = setup_logging(LOGGING['level'], LOGGING['format'])
    engine = None
    data_manager = None

    try:
        # Initialize API Key Manager and Password Manager
        api_key_manager = APIKeyManager()
        password_manager = PasswordManager()

        # Prompt for password
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        password = password_manager.prompt_for_password()
        if password is None:
            raise ValueError("Password not provided. Exiting.")

        api_key_manager.store_api_keys(EXCHANGE['name'], EXCHANGE['api_key'], EXCHANGE['secret_key'], password)
        keys = api_key_manager.get_api_keys(EXCHANGE['name'], password)

        # Initialize the trading engine
        config = {
            'exchange': {'name': EXCHANGE['name'], 'api_key': keys['api_key'], 'secret_key': keys['secret_key']},
            'initial_balance': TRADING_PARAMS['initial_balance'],
            'risk_params': RISK_MANAGEMENT,
            'strategies': STRATEGIES,
            'update_interval': TRADING_PARAMS.get('update_interval', 1),  # seconds
            'strategy_interval': TRADING_PARAMS.get('strategy_interval', 5),  # seconds
            'optimize_parameters': TRADING_PARAMS.get('optimize_parameters', False)
        }

        # Initialize Sentiment Analyzer
        sentiment_analyzer = SentimentAnalyzer()

        # Initialize VolatilityAnalyzer
        volatility_analyzer = VolatilityAnalyzer()

        # Initialize TradingEngine
        engine = TradingEngine(config)

        # Initialize RealTimeDataManager
        data_manager = RealTimeDataManager(engine.exchange_handler, TRADING_PARAMS['symbols'])

        # Update TradingEngine with RealTimeDataManager, SentimentAnalyzer, and VolatilityAnalyzer
        engine.set_data_manager(data_manager)
        engine.set_sentiment_analyzer(sentiment_analyzer)
        engine.set_volatility_analyzer(volatility_analyzer)

        # Start the GUI
        main_window = MainWindow(engine)

        # Run the async tasks and GUI
        await asyncio.gather(
            run_async_tasks(engine, data_manager),
            asyncio.to_thread(main_window.run)
        )

    except APIError as e:
        logger.error(f"API Error: {str(e)}")
    except StrategyError as e:
        logger.error(f"Strategy Error: {str(e)}")
    except DataError as e:
        logger.error(f"Data Error: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
    finally:
        logger.info("Shutting down the bot...")
        if engine:
            await engine.stop()
        if data_manager:
            await data_manager.stop()
        logger.info("Bot shutdown complete.")

if __name__ == '__main__':
    asyncio.run(main())

if __name__ == '__main__':
    main()
