
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='trading_bot.log', max_file_size=5*1024*1024, backup_count=3):
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a custom logger
    logger = logging.getLogger('TradingBot')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=max_file_size, backupCount=backup_count)
    c_handler.setLevel(logging.WARNING)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    # Create a security logger
    security_logger = logging.getLogger('TradingBot.Security')
    security_handler = RotatingFileHandler(os.path.join(log_dir, 'security.log'), maxBytes=max_file_size, backupCount=backup_count)
    security_handler.setLevel(logging.INFO)
    security_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    security_handler.setFormatter(security_format)
    security_logger.addHandler(security_handler)

    return logger, security_logger

# Usage example
if __name__ == "__main__":
    logger, security_logger = setup_logging()
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
    
    security_logger.info('User logged in')
    security_logger.warning('Failed login attempt')
    security_logger.error('Unauthorized access attempt')
