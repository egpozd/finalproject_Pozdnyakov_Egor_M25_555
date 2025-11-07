import time
import requests
from typing import Dict
from valutatrade_hub.parser_service.config import config
from valutatrade_hub.core.exceptions import ApiRequestError


class BaseApiClient:
    """Базовый класс для API клиентов"""
    
    def __init__(self):
        self.timeout = config.REQUEST_TIMEOUT
        self.retry_attempts = config.RETRY_ATTEMPTS
        self.retry_delay = config.RETRY_DELAY
    
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Выполнение HTTP запроса с повторными попытками"""
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_attempts - 1:
                    raise ApiRequestError(f"Ошибка запроса к {url}: {str(e)}")
                time.sleep(self.retry_delay)
        
        raise ApiRequestError(f"Не удалось выполнить запрос после {self.retry_attempts} попыток")
    
    def fetch_rates(self) -> Dict[str, float]:
        """Получение курсов валют (должен быть реализован в подклассах)"""
        raise NotImplementedError


class CoinGeckoClient(BaseApiClient):
    """Клиент для работы с CoinGecko API"""
    
    def fetch_rates(self) -> Dict[str, float]:
        """Получение курсов криптовалют"""
        # Формируем список ID криптовалют
        crypto_ids = [config.CRYPTO_ID_MAP[code] for code in config.CRYPTO_CURRENCIES 
                     if code in config.CRYPTO_ID_MAP]
        
        if not crypto_ids:
            return {}
        
        # Формируем параметры запроса
        params = {
            'ids': ','.join(crypto_ids),
            'vs_currencies': config.BASE_CURRENCY.lower()
        }
        
        # Добавляем API ключ если есть
        if config.COINGECKO_API_KEY:
            params['x_cg_demo_api_key'] = config.COINGECKO_API_KEY
        
        try:
            # Выполняем запрос
            data = self._make_request(config.COINGECKO_URL, params)
            
            # Преобразуем данные в единый формат
            rates = {}
            for crypto_code, gecko_id in config.CRYPTO_ID_MAP.items():
                if gecko_id in data and config.BASE_CURRENCY.lower() in data[gecko_id]:
                    rate_key = f"{crypto_code}_{config.BASE_CURRENCY}"
                    rates[rate_key] = data[gecko_id][config.BASE_CURRENCY.lower()]
            
            return rates
        except ApiRequestError:
            # Возвращаем демо-данные если API недоступно
            return {
                'BTC_USD': 59337.21,
                'ETH_USD': 3720.00,
                'SOL_USD': 145.12
            }


class ExchangeRateApiClient(BaseApiClient):
    """Клиент для работы с ExchangeRate-API"""
    
    def fetch_rates(self) -> Dict[str, float]:
        """Получение курсов фиатных валют"""
        # Если ключ не установлен, возвращаем демо-данные
        if not config.EXCHANGERATE_API_KEY or config.EXCHANGERATE_API_KEY == "demo_key":
            return {
                'EUR_USD': 1.0786,
                'GBP_USD': 1.2593,
                'RUB_USD': 0.01016,
                'JPY_USD': 0.0067
            }
        
        # Формируем URL запроса
        url = f"{config.EXCHANGERATE_API_URL}/{config.EXCHANGERATE_API_KEY}/latest/{config.BASE_CURRENCY}"
        
        try:
            # Выполняем запрос
            data = self._make_request(url)
            
            # Проверяем успешность запроса
            if data.get('result') != 'success':
                raise ApiRequestError(f"API вернуло ошибку: {data.get('error-type', 'unknown')}")
            
            # Извлекаем курсы для нужных валют
            rates = {}
            for currency in config.FIAT_CURRENCIES:
                if currency in data.get('conversion_rates', {}):
                    rate_key = f"{currency}_{config.BASE_CURRENCY}"
                    rates[rate_key] = data['conversion_rates'][currency]
            
            return rates
        except ApiRequestError:
            # Возвращаем демо-данные если API недоступно
            return {
                'EUR_USD': 1.0786,
                'GBP_USD': 1.2593,
                'RUB_USD': 0.01016,
                'JPY_USD': 0.0067
            }