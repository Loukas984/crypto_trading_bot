
from abc import ABC, abstractmethod
import logging
from utils.error_handling import error_handler, StrategyError

class BaseStrategy(ABC):
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.volatility = 1.0
        self.symbols = config['symbols']
        self.timeframe = config['timeframe']
        self.parameters = {}
        self.required_parameters = []

    @error_handler
    def set_parameters(self, params):
        self.parameters.update(params)
        self.validate_parameters()

    def adjust_for_volatility(self, volatility):
        self.volatility = volatility
        self.update_parameters()

    @abstractmethod
    def update_parameters(self):
        pass

    @abstractmethod
    async def analyze(self, symbol, timeframe, latest_data, sentiment_score):
        '''
        Analyse les données de marché et renvoie un résultat d'analyse.
        '''
        pass

    @abstractmethod
    async def generate_signal(self, analysis_result):
        '''
        Génère un signal de trading basé sur l'analyse.
        '''
        pass

    @error_handler
    async def execute(self, symbol, timeframe, latest_data, sentiment_score):
        '''
        Exécute la stratégie pour un symbole et un timeframe donnés.
        '''
        analysis_result = await self.analyze(symbol, timeframe, latest_data, sentiment_score)
        signal = await self.generate_signal(analysis_result)
        return signal

    def log_info(self, message):
        '''
        Enregistre un message d'information.
        '''
        self.logger.info(message)

    def log_error(self, message):
        '''
        Enregistre un message d'erreur.
        '''
        self.logger.error(message)

    def validate_parameters(self):
        '''
        Valide les paramètres de la stratégie.
        '''
        missing_params = [param for param in self.required_parameters if param not in self.parameters]
        if missing_params:
            raise StrategyError(f"Missing required parameters for {self.__class__.__name__}: {', '.join(missing_params)}")
