import os
from typing import Any


class SettingsLoader:
    _instance = None
    _settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance

    def _load_settings(self):
        """Загрузка настроек из конфигурации"""
        # Базовые настройки по умолчанию
        self._settings = {
            'data_directory': 'data',
            'rates_ttl_seconds': 300,  # 5 минут
            'default_base_currency': 'USD',
            'log_directory': 'logs',
            'log_level': 'INFO',
            'supported_currencies': ['USD', 'EUR', 'BTC', 'ETH', 'GBP', 'JPY', 'RUB', 'LTC']
        }

        # Здесь можно добавить загрузку из pyproject.toml или config.json
        # Пока используем настройки по умолчанию

    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения настройки"""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        """Установка значения настройки"""
        self._settings[key] = value

    def reload(self):
        """Перезагрузка настроек"""
        self._load_settings()

    def get_data_path(self, filename: str) -> str:
        """Получение полного пути к файлу данных"""
        data_dir = self.get('data_directory', 'data')
        return os.path.join(data_dir, filename)


# Глобальный экземпляр настроек
settings = SettingsLoader()