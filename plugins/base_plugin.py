
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    @abstractmethod
    def initialize(self, config):
        pass

    @abstractmethod
    def execute(self, data):
        pass

    @abstractmethod
    def get_info(self):
        pass

class StrategyPlugin(BasePlugin):
    @abstractmethod
    def generate_signals(self, data):
        pass

class IndicatorPlugin(BasePlugin):
    @abstractmethod
    def calculate(self, data):
        pass
