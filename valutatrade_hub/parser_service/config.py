import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


@dataclass
class ParserConfig:
    """Конфигурация для сервиса парсинга"""
    
    # API ключи (загружаются из переменных окружения)
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "")
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    
    # Эндпоинты API
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"
    
    # Базовая валюта
    BASE_CURRENCY: str = "USD"
    
    # Списки отслеживаемых валют
    FIAT_CURRENCIES: tuple = ("EUR", "GBP", "RUB", "JPY", "CHF", "CNY")
    CRYPTO_CURRENCIES: tuple = ("BTC", "ETH", "SOL", "ADA", "DOT", "DOGE")
    
    # Сопоставление кодов криптовалют с ID в CoinGecko
    CRYPTO_ID_MAP: dict = None
    
    # Параметры запросов
    REQUEST_TIMEOUT: int = 10
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 2
    
    # Пути к файлам
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"
    
    # TTL кэша (в секундах)
    CACHE_TTL: int = 300  # 5 минут
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.CRYPTO_ID_MAP is None:
            self.CRYPTO_ID_MAP = {
                "BTC": "bitcoin",
                "ETH": "ethereum", 
                "SOL": "solana",
                "ADA": "cardano",
                "DOT": "polkadot",
                "DOGE": "dogecoin"
            }
        
        # Проверяем обязательные настройки
        if not self.EXCHANGERATE_API_KEY:
            raise ValueError("EXCHANGERATE_API_KEY не установлен. Добавьте его в .env файл")


# Глобальный экземпляр конфигурации
config = ParserConfig()