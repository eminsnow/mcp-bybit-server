import os
import logging
from dotenv import load_dotenv

load_dotenv(verbose=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Maksymalny rozmiar zlecenia w USDT (zabezpieczenie przed przypadkowym duzym zleceniem)
MAX_ORDER_SIZE_USDT = float(os.getenv("MAX_ORDER_SIZE_USDT", "100"))

class Config:
    MEMBER_ID = os.getenv("MEMBER_ID")
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    TESTNET = os.getenv("TESTNET", "false").lower() == "true"
    TRADING_ENABLED = os.getenv("TRADING_ENABLED", "false").lower() == "true"

    @classmethod
    def log_config(cls):
        # BEZPIECZENSTWO: logujemy TYLKO czy klucz istnieje, NIGDY wartosc
        logger.info(f"ACCESS_KEY configured: {'YES' if cls.ACCESS_KEY else 'NO'}")
        logger.info(f"SECRET_KEY configured: {'YES' if cls.SECRET_KEY else 'NO'}")
        logger.info(f"TESTNET: {cls.TESTNET}")
        logger.info(f"TRADING_ENABLED: {cls.TRADING_ENABLED}")
        logger.info(f"MAX_ORDER_SIZE_USDT: {MAX_ORDER_SIZE_USDT}")

# Log configuration
Config.log_config()
