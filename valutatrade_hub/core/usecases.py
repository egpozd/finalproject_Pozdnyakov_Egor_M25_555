"""Бизнес-логика приложения"""

import os
import json
from datetime import datetime
from valutatrade_hub.core.models import User
from valutatrade_hub.decorators import log_action
from valutatrade_hub.core.utils import read_json, write_json

# Система сессии
SESSION_FILE = 'data/session.json'

def save_session(user_id):
    """Сохранение сессии пользователя"""
    os.makedirs('data', exist_ok=True)
    session_data = {
        'user_id': user_id,
        'timestamp': datetime.now().isoformat()
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(session_data, f)

def load_session():
    """Загрузка сессии пользователя"""
    try:
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def clear_session():
    """Очистка сессии"""
    try:
        os.remove(SESSION_FILE)
    except FileNotFoundError:
        pass


class UserManager:
    def __init__(self):
        self.users_file = 'data/users.json'
        self.portfolios_file = 'data/portfolios.json'
        self.current_user = None
        self._load_session()  # Загружаем сессию при инициализации

    def _load_session(self):
        """Загрузка сессии при старте"""
        session_data = load_session()
        if session_data:
            user_id = session_data['user_id']
            user_data = self.get_user_by_id(user_id)
            if user_data:
                self.current_user = User(
                    user_data['user_id'],
                    user_data['username'],
                    user_data['hashed_password'],
                    user_data['salt'],
                    datetime.fromisoformat(user_data['registration_date'])
                )

    def get_user_by_id(self, user_id):
        """Получение пользователя по ID"""
        users = read_json(self.users_file)
        for user in users:
            if user.get('user_id') == user_id:
                return user
        return None

    @log_action('REGISTER', verbose=True)
    def register_user(self, username: str, password: str) -> User:
        """Регистрация нового пользователя с логированием"""
        import secrets
        
        users = read_json(self.users_file)
        
        # Проверка уникальности username
        for user_data in users:
            if user_data['username'] == username:
                raise ValueError(f"Имя пользователя '{username}' уже занято")

        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")

        # Генерация user_id
        user_id = 1
        if users:
            user_id = max(user['user_id'] for user in users) + 1

        # Создание пользователя
        salt = secrets.token_hex(8)
        hashed_password = User._hash_password(password, salt)
        registration_date = datetime.now().isoformat()

        new_user = User(user_id, username, hashed_password, salt, registration_date)
        
        # Сохранение пользователя
        users.append({
            'user_id': user_id,
            'username': username,
            'hashed_password': hashed_password,
            'salt': salt,
            'registration_date': registration_date
        })
        write_json(users, self.users_file)

        # Создание пустого портфеля
        portfolios = read_json(self.portfolios_file)
        portfolios.append({
            'user_id': user_id,
            'wallets': {}
        })
        write_json(portfolios, self.portfolios_file)

        return new_user

    @log_action('LOGIN', verbose=True)  
    def login(self, username: str, password: str) -> User:
        """Вход пользователя с логированием"""
        users = read_json(self.users_file)
        
        for user_data in users:
            if user_data['username'] == username:
                user = User(
                    user_data['user_id'],
                    user_data['username'],
                    user_data['hashed_password'],
                    user_data['salt'],
                    datetime.fromisoformat(user_data['registration_date'])
                )
                if user.verify_password(password):
                    self.current_user = user
                    save_session(user.user_id)  # Сохраняем сессию
                    return user
                else:
                    raise ValueError("Неверный пароль")
        
        raise ValueError(f"Пользователь '{username}' не найден")

    def logout(self):
        """Выход пользователя"""
        clear_session()
        self.current_user = None


class PortfolioManager:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
        self.portfolios_file = 'data/portfolios.json'

    def _get_portfolio_data(self):
        """Получение портфеля текущего пользователя"""
        if not self.user_manager.current_user:
            raise ValueError("Сначала выполните login")

        portfolios = read_json(self.portfolios_file)
        for portfolio_data in portfolios:
            if portfolio_data['user_id'] == self.user_manager.current_user.user_id:
                return portfolio_data
        
        # Если портфель не найден, создаем новый
        new_portfolio = {
            'user_id': self.user_manager.current_user.user_id,
            'wallets': {}
        }
        portfolios.append(new_portfolio)
        write_json(portfolios, self.portfolios_file)
        return new_portfolio

    def _save_portfolio_data(self, portfolio_data):
        """Сохранение портфеля"""
        portfolios = read_json(self.portfolios_file)
        for i, portfolio in enumerate(portfolios):
            if portfolio['user_id'] == self.user_manager.current_user.user_id:
                portfolios[i] = portfolio_data
                break
        write_json(portfolios, self.portfolios_file)

    def get_portfolio(self):
        """Получение объекта Portfolio"""
        from valutatrade_hub.core.models import Portfolio, Wallet
        
        portfolio_data = self._get_portfolio_data()
        
        wallets = {}
        for currency_code, wallet_data in portfolio_data['wallets'].items():
            wallets[currency_code] = Wallet(currency_code, wallet_data['balance'])
        
        return Portfolio(portfolio_data['user_id'], wallets)

    def save_portfolio(self, portfolio):
        """Сохранение Portfolio в JSON"""
        portfolio_data = {
            'user_id': portfolio.user_id,
            'wallets': {
                currency: {'balance': wallet.balance}
                for currency, wallet in portfolio.wallets.items()
            }
        }
        self._save_portfolio_data(portfolio_data)

    @log_action('BUY')
    def buy_currency(self, user_id: int, currency_code: str, amount: float) -> dict:
        """Покупка валюты с логированием"""
        portfolio = self.get_portfolio()
        
        if currency_code.upper() not in portfolio.wallets:
            portfolio.add_currency(currency_code.upper())
        
        wallet = portfolio.get_wallet(currency_code.upper())
        old_balance = wallet.balance
        wallet.deposit(amount)
        
        self.save_portfolio(portfolio)
        
        return {
            'currency': currency_code,
            'amount': amount,
            'old_balance': old_balance,
            'new_balance': wallet.balance,
            'user_id': user_id
        }

    @log_action('SELL')
    def sell_currency(self, user_id: int, currency_code: str, amount: float) -> dict:
        """Продажа валюты с логированием"""
        portfolio = self.get_portfolio()
        wallet = portfolio.get_wallet(currency_code.upper())
        
        if not wallet:
            raise ValueError(f"Кошелек для валюты {currency_code} не найден")
        
        old_balance = wallet.balance
        wallet.withdraw(amount)
        
        self.save_portfolio(portfolio)
        
        return {
            'currency': currency_code,
            'amount': amount,
            'old_balance': old_balance,
            'new_balance': wallet.balance,
            'user_id': user_id
        }


# Глобальные менеджеры
user_manager = UserManager()
portfolio_manager = PortfolioManager(user_manager)