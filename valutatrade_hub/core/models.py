"""Модели данных для Core Service"""

import hashlib
import secrets
from datetime import datetime
from typing import Dict, Optional
from valutatrade_hub.core.exceptions import InsufficientFundsError, InvalidAmountError


class User:
    """Класс пользователя системы"""
    
    def __init__(self, user_id: int, username: str, hashed_password: str, 
                 salt: str, registration_date: datetime):
        """
        Инициализация пользователя
        
        Args:
            user_id: Уникальный идентификатор пользователя
            username: Имя пользователя
            hashed_password: Хешированный пароль
            salt: Соль для хеширования
            registration_date: Дата регистрации
        """
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        """ID пользователя"""
        return self._user_id

    @property
    def username(self) -> str:
        """Имя пользователя"""
        return self._username

    @username.setter
    def username(self, value: str):
        """Установка имени пользователя с валидацией"""
        if not value:
            raise ValueError("Имя не может быть пустым")
        self._username = value

    @property
    def hashed_password(self) -> str:
        """Хешированный пароль"""
        return self._hashed_password

    @property
    def salt(self) -> str:
        """Соль для хеширования"""
        return self._salt

    @property
    def registration_date(self) -> datetime:
        """Дата регистрации"""
        return self._registration_date

    def get_user_info(self) -> str:
        """Получение информации о пользователе (без пароля)"""
        return (f"User ID: {self._user_id}, "
                f"Username: {self._username}, "
                f"Registered: {self._registration_date}")

    def change_password(self, new_password: str):
        """
        Изменение пароля пользователя
        
        Args:
            new_password: Новый пароль
            
        Raises:
            ValueError: Если пароль слишком короткий
        """
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._salt = secrets.token_hex(8)
        self._hashed_password = self._hash_password(new_password, self._salt)

    def verify_password(self, password: str) -> bool:
        """
        Проверка пароля
        
        Args:
            password: Пароль для проверки
            
        Returns:
            bool: True если пароль верный
        """
        return self._hashed_password == self._hash_password(password, self._salt)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Хеширование пароля с солью"""
        return hashlib.sha256((password + salt).encode()).hexdigest()


class Wallet:
    """Кошелек для хранения баланса в конкретной валюте"""
    
    def __init__(self, currency_code: str, balance: float = 0.0):
        """
        Инициализация кошелька
        
        Args:
            currency_code: Код валюты
            balance: Начальный баланс
        """
        self.currency_code = currency_code
        self._balance = balance

    @property
    def balance(self) -> float:
        """Текущий баланс"""
        return self._balance

    @balance.setter
    def balance(self, value: float):
        """Установка баланса с валидацией"""
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")
        self._balance = value

    def deposit(self, amount: float):
        """
        Пополнение баланса
        
        Args:
            amount: Сумма пополнения
            
        Raises:
            InvalidAmountError: Если сумма некорректна
        """
        if amount <= 0:
            raise InvalidAmountError(amount)
        self.balance += amount

    def withdraw(self, amount: float):
        """
        Снятие средств
        
        Args:
            amount: Сумма снятия
            
        Raises:
            InvalidAmountError: Если сумма некорректна
            InsufficientFundsError: Если недостаточно средств
        """
        if amount <= 0:
            raise InvalidAmountError(amount)
        if amount > self.balance:
            raise InsufficientFundsError(self.balance, amount, self.currency_code)
        self.balance -= amount

    def get_balance_info(self) -> str:
        """Информация о балансе"""
        return f"{self.currency_code}: {self.balance:.4f}"


class Portfolio:
    """Портфель кошельков пользователя"""
    
    def __init__(self, user_id: int, wallets: Dict[str, Wallet] = None):
        """
        Инициализация портфеля
        
        Args:
            user_id: ID пользователя
            wallets: Словарь кошельков
        """
        self._user_id = user_id
        self._wallets = wallets if wallets is not None else {}

    @property
    def user_id(self) -> int:
        """ID пользователя"""
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Wallet]:
        """Копия словаря кошельков"""
        return self._wallets.copy()

    def add_currency(self, currency_code: str):
        """
        Добавление новой валюты в портфель
        
        Args:
            currency_code: Код валюты
            
        Raises:
            ValueError: Если валюта уже существует или код некорректен
        """
        if not currency_code:
            raise ValueError("Код валюты не может быть пустым")
        currency_code = currency_code.upper()
        if currency_code in self._wallets:
            raise ValueError(f"Валюта {currency_code} уже есть в портфеле")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Optional[Wallet]:
        """
        Получение кошелька по коду валюты
        
        Args:
            currency_code: Код валюты
            
        Returns:
            Wallet или None если не найден
        """
        return self._wallets.get(currency_code.upper())

    def get_total_value(self, base_currency: str = 'USD') -> float:
        """
        Расчет общей стоимости портфеля в базовой валюте
        
        Args:
            base_currency: Базовая валюта для расчета
            
        Returns:
            Общая стоимость портфеля
        """
        # Временная заглушка - будет заменена на реальные курсы
        exchange_rates = {
            'BTC_USD': 59337.21,
            'EUR_USD': 1.0786,
            'USD_USD': 1.0,
            'RUB_USD': 0.01016,
            'ETH_USD': 3720.00
        }
        
        total_value = 0.0
        for currency, wallet in self._wallets.items():
            if currency == base_currency:
                total_value += wallet.balance
            else:
                rate_key = f"{currency}_{base_currency}"
                if rate_key in exchange_rates:
                    total_value += wallet.balance * exchange_rates[rate_key]
                else:
                    print(f"Предупреждение: курс для {rate_key} не найден")
        return total_value