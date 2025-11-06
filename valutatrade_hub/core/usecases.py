import secrets
from datetime import datetime
from typing import Optional, Dict, Any
from valutatrade_hub.core.models import User, Portfolio, Wallet
from valutatrade_hub.core.utils import read_json, write_json


class UserManager:
    def __init__(self):
        self.users_file = 'data/users.json'
        self.portfolios_file = 'data/portfolios.json'
        self.current_user: Optional[User] = None

    def register_user(self, username: str, password: str) -> User:
        """Регистрация нового пользователя"""
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

    def login(self, username: str, password: str) -> User:
        """Вход пользователя"""
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
                    return user
                else:
                    raise ValueError("Неверный пароль")
        
        raise ValueError(f"Пользователь '{username}' не найден")

    def logout(self):
        """Выход пользователя"""
        self.current_user = None


class PortfolioManager:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
        self.portfolios_file = 'data/portfolios.json'

    def _get_portfolio_data(self) -> Dict[str, Any]:
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

    def _save_portfolio_data(self, portfolio_data: Dict[str, Any]):
        """Сохранение портфеля"""
        portfolios = read_json(self.portfolios_file)
        for i, portfolio in enumerate(portfolios):
            if portfolio['user_id'] == self.user_manager.current_user.user_id:
                portfolios[i] = portfolio_data
                break
        write_json(portfolios, self.portfolios_file)

    def get_portfolio(self) -> Portfolio:
        """Получение объекта Portfolio"""
        portfolio_data = self._get_portfolio_data()
        
        wallets = {}
        for currency_code, wallet_data in portfolio_data['wallets'].items():
            wallets[currency_code] = Wallet(currency_code, wallet_data['balance'])
        
        return Portfolio(portfolio_data['user_id'], wallets)

    def save_portfolio(self, portfolio: Portfolio):
        """Сохранение Portfolio в JSON"""
        portfolio_data = {
            'user_id': portfolio.user_id,
            'wallets': {
                currency: {'balance': wallet.balance}
                for currency, wallet in portfolio.wallets.items()
            }
        }
        self._save_portfolio_data(portfolio_data)


# Глобальные менеджеры
user_manager = UserManager()
portfolio_manager = PortfolioManager(user_manager)