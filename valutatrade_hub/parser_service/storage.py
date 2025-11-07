from datetime import datetime, timezone
from typing import Dict, Any
from valutatrade_hub.parser_service.config import config
from valutatrade_hub.infra.database import db


class RatesStorage:
    """Класс для работы с хранилищем курсов валют"""
    
    def save_current_rates(self, rates: Dict[str, float], sources: Dict[str, str]) -> int:
        """
        Сохранение текущих курсов в rates.json
        
        Args:
            rates: Словарь с курсами { "BTC_USD": 59337.21, ... }
            sources: Словарь с источниками данных { "BTC_USD": "CoinGecko", ... }
            
        Returns:
            Количество сохраненных курсов
        """
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Формируем структуру данных для rates.json
        pairs = {}
        for pair, rate in rates.items():
            pairs[pair] = {
                'rate': rate,
                'updated_at': current_time,
                'source': sources.get(pair, 'Unknown')
            }
        
        data = {
            'pairs': pairs,
            'last_refresh': current_time
        }
        
        # Сохраняем в файл
        db.write_json(data, 'rates.json')
        return len(rates)
    
    def save_historical_rate(self, from_currency: str, to_currency: str, 
                           rate: float, source: str, meta: Dict[str, Any] = None) -> str:
        """
        Сохранение исторической записи о курсе
        
        Args:
            from_currency: Исходная валюта
            to_currency: Целевая валюта
            rate: Курс
            source: Источник данных
            meta: Дополнительные метаданные
            
        Returns:
            ID созданной записи
        """
        timestamp = datetime.now(timezone.utc)
        record_id = f"{from_currency}_{to_currency}_{timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        
        record = {
            'id': record_id,
            'from_currency': from_currency.upper(),
            'to_currency': to_currency.upper(),
            'rate': rate,
            'timestamp': timestamp.isoformat(),
            'source': source,
            'meta': meta or {}
        }
        
        # Читаем существующие данные
        try:
            history = db.read_json('exchange_rates.json')
            if not isinstance(history, list):
                history = []
        except Exception:
            history = []
        
        # Добавляем новую запись
        history.append(record)
        
        # Сохраняем обратно
        db.write_json(history, 'exchange_rates.json')
        
        return record_id
    
    def get_current_rates(self) -> Dict[str, Any]:
        """Получение текущих курсов из кэша"""
        try:
            return db.read_json('rates.json') or {'pairs': {}, 'last_refresh': None}
        except Exception:
            return {'pairs': {}, 'last_refresh': None}
    
    def is_cache_valid(self) -> bool:
        """Проверка актуальности кэша"""
        try:
            data = self.get_current_rates()
            if not data.get('last_refresh'):
                return False
            
            last_refresh = datetime.fromisoformat(data['last_refresh'])
            now = datetime.now(timezone.utc)
            cache_age = (now - last_refresh).total_seconds()
            
            return cache_age < config.CACHE_TTL
        except Exception:
            return False


# Глобальный экземпляр хранилища
storage = RatesStorage()