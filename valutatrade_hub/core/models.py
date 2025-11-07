import hashlib
import secrets
from datetime import datetime
from typing import Dict, Optional
from valutatrade_hub.core.exceptions import InsufficientFundsError, InvalidAmountError


class User:
    def __init__(self, user_id: int, username: str, hashed_password: str, 
                 salt: str, registration_date: datetime):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        if not value:
            raise ValueError("Имя не может быть пустым")
        self._username = value

    @property
    def hashed_password(self) -> str:
        return self._hashed_password

    @property
    def salt(self) -> str:
        return self._salt

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    def get_user_info(self) -> str:
        return (f"User ID: {self._user_id}, "
                f"Username: {self._username}, "
                f"Registered: {self._registration_date}")

    def change_password(self, new_password: str):
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._salt = secrets.token_hex(8)
        self._hashed_password = self._hash_password(new_password, self._salt)

    def verify_password(self, password: str) -> bool:
        return self._hashed_password == self._hash_password(password, self._salt)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode()).hexdigest()


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")
        self._balance = value

    def deposit(self, amount: float):
        if amount <= 0:
            raise InvalidAmountError(amount)
        self.balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise InvalidAmountError(amount)
        if amount > self.balance:
            raise InsufficientFundsError(self.balance, amount, self.currency_code)
        self.balance -= amount

    def get_balance_info(self) -> str:
        return f"{self.currency_code}: {self.balance:.4f}"



class Portfolio:
    def __init__(self, user_id: int, wallets: Dict[str, Wallet] = None):
        self._user_id = user_id
        self._wallets = wallets if wallets is not None else {}

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Wallet]:
        return self._wallets.copy()

    def add_currency(self, currency_code: str):
        if not currency_code:
            raise ValueError("Код валюты не может быть пустым")
        currency_code = currency_code.upper()
        if currency_code in self._wallets:
            raise ValueError(f"Валюта {currency_code} уже есть в портфеле")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Optional[Wallet]:
        return self._wallets.get(currency_code.upper())

    def get_total_value(self, base_currency: str = 'USD') -> float:
        # Временная заглушка для курсов валют
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