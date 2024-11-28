
import importlib
import os
from typing import Dict, Any
from utils.logging_config import setup_logging

class PluginManager:
    def __init__(self):
        self.logger = setup_logging()
        self.strategies = {}
        self.indicators = {}
        self.custom_plugins_dir = 'plugins/custom_plugins'

    def load_strategy(self, strategy_name: str, config: Dict) -> Any:
        if strategy_name in self.strategies:
            return self.strategies[strategy_name]

        try:
            # Convert CamelCase to snake_case
            module_name = ''.join(['_' + c.lower() if c.isupper() else c for c in strategy_name]).lstrip('_')
            # Try to load from built-in strategies
            module = importlib.import_module(f'strategies.{module_name}')
            strategy_class = getattr(module, strategy_name)
            self.strategies[strategy_name] = strategy_class(config)
            self.logger.info(f"Loaded built-in strategy: {strategy_name}")
            return self.strategies[strategy_name]
        except ImportError:
            # If not found, try to load from custom plugins
            return self.load_custom_plugin('strategies', strategy_name, config)

    def load_indicator(self, indicator_name: str) -> Any:
        if indicator_name in self.indicators:
            return self.indicators[indicator_name]

        try:
            # Try to load from built-in indicators
            module = importlib.import_module(f'indicators.{indicator_name.lower()}')
            indicator_class = getattr(module, indicator_name)
            self.indicators[indicator_name] = indicator_class()
            self.logger.info(f"Loaded built-in indicator: {indicator_name}")
            return self.indicators[indicator_name]
        except ImportError:
            # If not found, try to load from custom plugins
            return self.load_custom_plugin('indicators', indicator_name)

    def load_custom_plugin(self, plugin_type: str, plugin_name: str, config: Dict = None) -> Any:
        plugin_path = os.path.join(self.custom_plugins_dir, plugin_type, f"{plugin_name.lower()}.py")
        if not os.path.exists(plugin_path):
            raise ImportError(f"Custom {plugin_type} plugin not found: {plugin_name}")

        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        plugin_class = getattr(module, plugin_name)
        plugin_instance = plugin_class(config) if config else plugin_class()

        if plugin_type == 'strategies':
            self.strategies[plugin_name] = plugin_instance
        elif plugin_type == 'indicators':
            self.indicators[plugin_name] = plugin_instance

        self.logger.info(f"Loaded custom {plugin_type} plugin: {plugin_name}")
        return plugin_instance

    def get_available_strategies(self) -> Dict[str, Any]:
        return self.strategies

    def get_available_indicators(self) -> Dict[str, Any]:
        return self.indicators

    def unload_strategy(self, strategy_name: str) -> None:
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
            self.logger.info(f"Unloaded strategy: {strategy_name}")
        else:
            self.logger.warning(f"Strategy not found: {strategy_name}")

    def unload_indicator(self, indicator_name: str) -> None:
        if indicator_name in self.indicators:
            del self.indicators[indicator_name]
            self.logger.info(f"Unloaded indicator: {indicator_name}")
        else:
            self.logger.warning(f"Indicator not found: {indicator_name}")

if __name__ == "__main__":
    # Example usage
    plugin_manager = PluginManager()

    # Example configuration
    config = {
        'param1': 'value1',
        'param2': 'value2'
    }

    # Load a built-in strategy
    scalping_strategy = plugin_manager.load_strategy("ScalpingStrategy", config)
    print(f"Loaded strategy: {scalping_strategy}")

    # Load a built-in indicator
    rsi_indicator = plugin_manager.load_indicator("RSI")
    print(f"Loaded indicator: {rsi_indicator}")

    # Try to load a custom strategy (this will fail if the custom plugin doesn't exist)
    try:
        custom_strategy = plugin_manager.load_strategy("CustomStrategy", config)
        print(f"Loaded custom strategy: {custom_strategy}")
    except ImportError as e:
        print(f"Failed to load custom strategy: {e}")

    # Print available strategies and indicators
    print("Available strategies:", plugin_manager.get_available_strategies())
    print("Available indicators:", plugin_manager.get_available_indicators())

    # Unload a strategy
    plugin_manager.unload_strategy("ScalpingStrategy")
    print("Available strategies after unload:", plugin_manager.get_available_strategies())
