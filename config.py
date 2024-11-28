
# Configuration globale pour le bot de trading

# Paramètres de l'exchange
EXCHANGE = {
    'name': 'binance',
    'api_key': 'YOUR_API_KEY_HERE',
    'secret_key': 'YOUR_SECRET_KEY_HERE'
}

# Paramètres de trading
TRADING_PARAMS = {
    'symbols': ['HMSTR/USDT', 'DOGE/USDT', 'SHIB/USDT'],  # Paires de trading mises à jour
    'timeframe': '1h',  # Intervalle de temps pour les données
    'initial_balance': 10000,  # Solde initial en USDT
}

# Paramètres de gestion des risques
RISK_MANAGEMENT = {
    'max_position_size': 0.01,  # Taille maximale de position réduite à 1% du portefeuille
    'stop_loss_pct': 0.05,  # Pourcentage de stop loss augmenté à 5%
    'take_profit_pct': 0.10,  # Pourcentage de take profit augmenté à 10%
    'max_open_positions': 2,  # Nombre maximum de positions ouvertes réduit à 2
    'max_daily_trades': 10,  # Limite le nombre de trades par jour
    'volatility_adjustment': True,  # Active l'ajustement dynamique basé sur la volatilité
    'exceptional_price_change_threshold': 0.1,  # Seuil pour les mouvements de prix exceptionnels (10%)
    'strategy_performance_threshold': -0.05,  # Seuil de performance pour l'ajustement des stratégies (-5%)
    'strategy_adjustment_interval': 3600,  # Intervalle d'ajustement des stratégies (en secondes, ici 1 heure)
    'max_drawdown_pct': 0.2,  # Pourcentage maximum de drawdown autorisé
    'max_risk_per_trade': 0.02  # Risque maximum par trade (2% du portefeuille)
}

# Paramètres des stratégies
STRATEGIES = [
    {
        'name': 'SentimentMomentumStrategy',
        'params': {
            'rsi_period': 14,
            'rsi_overbought': 75,  # Augmenté pour s'adapter à la volatilité
            'rsi_oversold': 25,    # Diminué pour s'adapter à la volatilité
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'sentiment_threshold': 0.15  # Diminué pour être plus sensible aux changements de sentiment
        }
    },
    {
        'name': 'GridTradingStrategy',
        'params': {
            'grid_levels': 5,
            'grid_size': 0.02,  # 2% entre chaque niveau de la grille
            'total_investment': 1000  # Investissement total en USDT
        }
    },
    {
        'name': 'BreakoutStrategy',
        'params': {
            'lookback_period': 20,
            'breakout_threshold': 2.5,
            'stop_loss_pct': 0.05,
            'take_profit_pct': 0.10
        }
    }
]

# Paramètres de performance
PERFORMANCE = {
    'benchmark': 'DOGE/USDT',  # Symbole à utiliser comme référence pour la performance
}

# Paramètres de logging
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Paramètres de base de données
DATABASE = {
    'name': 'trading_bot.db',
    'type': 'sqlite'
}

# Paramètres de backtesting
BACKTESTING = {
    'start_date': '2023-01-01',
    'end_date': '2023-06-30',
}
