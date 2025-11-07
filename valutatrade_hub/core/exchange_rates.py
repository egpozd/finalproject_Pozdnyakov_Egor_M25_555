"""Сервис для работы с курсами валют в Core Service"""

from valutatrade_hub.core.exceptions import CurrencyNotFoundError
from valutatrade_hub.parser_service.storage import storage


class ExchangeRateService:
    """Сервис для получения актуальных курсов валют"""
    
    @staticmethod
    def get_rate(from_currency: str, to_currency: str) -> float:
        """
        Получение курса валюты
        
        Args:
            from_currency: Исходная валюта
            to_currency: Целевая валюта
            
        Returns:
            Курс обмена
            
        Raises:
            CurrencyNotFoundError: Если курс не найден
        """
        data = storage.get_current_rates()
        pair = f"{from_currency.upper()}_{to_currency.upper()}"
        
        if pair in data.get('pairs', {}):
            return data['pairs'][pair]['rate']
        
        # Попробуем обратную пару
        reverse_pair = f"{to_currency.upper()}_{from_currency.upper()}"
        if reverse_pair in data.get('pairs', {}):
            rate = data['pairs'][reverse_pair]['rate']
            return 1.0 / rate if rate != 0 else 0
        
        # Для одинаковых валют
        if from_currency.upper() == to_currency.upper():
            return 1.0
            
        raise CurrencyNotFoundError(f"Курс для {from_currency}->{to_currency}")

    @staticmethod
    def is_cache_valid() -> bool:
        """Проверка актуальности кэша курсов"""
        return storage.is_cache_valid()

    @staticmethod
    def get_all_rates() -> dict:
        """Получение всех текущих курсов"""
        data = storage.get_current_rates()
        return data.get('pairs', {})

    @staticmethod
    def get_last_refresh_time() -> str:
        """Время последнего обновления курсов"""
        data = storage.get_current_rates()
        return data.get('last_refresh', 'Never')