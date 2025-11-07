import json
import os
from typing import Any
from valutatrade_hub.infra.settings import settings


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def read_json(self, filename: str) -> Any:
        """Чтение JSON файла"""
        file_path = settings.get_data_path(filename)
        if not os.path.exists(file_path):
            # Возвращаем значение по умолчанию в зависимости от имени файла
            if 'users' in filename or 'portfolios' in filename:
                return []
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise IOError(f"Ошибка чтения файла {filename}: {e}")

    def write_json(self, data: Any, filename: str):
        """Запись в JSON файл"""
        file_path = settings.get_data_path(filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except IOError as e:
            raise IOError(f"Ошибка записи файла {filename}: {e}")

    def get_user_by_id(self, user_id: int) -> dict[str, Any]:
        """Получение пользователя по ID"""
        users = self.read_json('users.json')
        for user in users:
            if user.get('user_id') == user_id:
                return user
        return None

    def get_portfolio_by_user_id(self, user_id: int) -> dict[str, Any]:
        """Получение портфеля по ID пользователя"""
        portfolios = self.read_json('portfolios.json')
        for portfolio in portfolios:
            if portfolio.get('user_id') == user_id:
                return portfolio
        return None

    def update_portfolio(self, user_id: int, portfolio_data: dict[str, Any]):
        """Обновление портфеля пользователя"""
        portfolios = self.read_json('portfolios.json')
        updated = False
        
        for i, portfolio in enumerate(portfolios):
            if portfolio.get('user_id') == user_id:
                portfolios[i] = portfolio_data
                updated = True
                break
        
        if not updated:
            portfolios.append(portfolio_data)
        
        self.write_json(portfolios, 'portfolios.json')


# Глобальный экземпляр менеджера базы данных
db = DatabaseManager()