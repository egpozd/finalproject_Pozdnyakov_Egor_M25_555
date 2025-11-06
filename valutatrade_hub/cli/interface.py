import argparse
from valutatrade_hub.core.usecases import user_manager, portfolio_manager


def main():
    parser = argparse.ArgumentParser(description='Currency Wallet CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # register command
    register_parser = subparsers.add_parser('register', help='Register new user')
    register_parser.add_argument('--username', required=True, help='Username')
    register_parser.add_argument('--password', required=True, help='Password')

    # login command
    login_parser = subparsers.add_parser('login', help='Login user')
    login_parser.add_argument('--username', required=True, help='Username')
    login_parser.add_argument('--password', required=True, help='Password')

    # show-portfolio command
    portfolio_parser = subparsers.add_parser('show-portfolio', help='Show user portfolio')
    portfolio_parser.add_argument('--base', default='USD', help='Base currency (default: USD)')

    # buy command
    buy_parser = subparsers.add_parser('buy', help='Buy currency')
    buy_parser.add_argument('--currency', required=True, help='Currency code to buy')
    buy_parser.add_argument('--amount', type=float, required=True, help='Amount to buy')

    # sell command
    sell_parser = subparsers.add_parser('sell', help='Sell currency')
    sell_parser.add_argument('--currency', required=True, help='Currency code to sell')
    sell_parser.add_argument('--amount', type=float, required=True, help='Amount to sell')

    # get-rate command
    rate_parser = subparsers.add_parser('get-rate', help='Get exchange rate')
    rate_parser.add_argument('--from', required=True, dest='from_currency', help='From currency')
    rate_parser.add_argument('--to', required=True, help='To currency')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'register':
            register_user(args.username, args.password)
        elif args.command == 'login':
            login_user(args.username, args.password)
        elif args.command == 'show-portfolio':
            show_portfolio(args.base)
        elif args.command == 'buy':
            buy_currency(args.currency, args.amount)
        elif args.command == 'sell':
            sell_currency(args.currency, args.amount)
        elif args.command == 'get-rate':
            get_rate(args.from_currency, args.to)
    except Exception as e:
        print(f"Ошибка: {e}")


def register_user(username: str, password: str):
    """Регистрация нового пользователя"""
    user_id = user_manager.register_user(username, password).user_id
    print(f"Пользователь '{username}' зарегистрирован (id={user_id}). "
          f"Войдите: login --username {username} --password ****")


def login_user(username: str, password: str):
    """Вход пользователя"""
    user_manager.login(username, password)
    print(f"Вы вошли как '{username}'")


def show_portfolio(base_currency: str):
    """Показать портфель пользователя"""
    if not user_manager.current_user:
        print("Сначала выполните login")
        return

    portfolio = portfolio_manager.get_portfolio()
    
    if not portfolio.wallets:
        print("Портфель пуст")
        return

    print(f"Портфель пользователя '{user_manager.current_user.username}' (база: {base_currency}):")
    
    total_value = 0
    for currency, wallet in portfolio.wallets.items():
        # Временный расчет стоимости (будет заменен на реальные курсы)
        if currency == base_currency:
            value = wallet.balance
        else:
            # Заглушка для демонстрации
            exchange_rates = {
                'BTC_USD': 59337.21,
                'EUR_USD': 1.0786,
                'USD_USD': 1.0,
            }
            rate_key = f"{currency}_{base_currency}"
            value = wallet.balance * exchange_rates.get(rate_key, 1.0)
        
        total_value += value
        print(f"- {currency}: {wallet.balance:.2f} → {value:.2f} {base_currency}")
    
    print("---------------------------------")
    print(f"ИТОГО: {total_value:,.2f} {base_currency}")


def buy_currency(currency: str, amount: float):
    """Покупка валюты"""
    if not user_manager.current_user:
        print("Сначала выполните login")
        return

    try:
        portfolio = portfolio_manager.get_portfolio()
        
        # Добавляем валюту если ее нет
        if currency.upper() not in portfolio.wallets:
            portfolio.add_currency(currency.upper())
        
        wallet = portfolio.get_wallet(currency.upper())
        wallet.deposit(amount)
        
        portfolio_manager.save_portfolio(portfolio)
        
        print(f"Покупка выполнена: {amount:.4f} {currency.upper()}")
        print("Изменения в портфеле:")
        print(f"- {currency.upper()}: стало {wallet.balance:.4f}")
        
    except Exception as e:
        print(f"Ошибка при покупке: {e}")


def sell_currency(currency: str, amount: float):
    """Продажа валюты"""
    if not user_manager.current_user:
        print("Сначала выполните login")
        return

    try:
        portfolio = portfolio_manager.get_portfolio()
        wallet = portfolio.get_wallet(currency.upper())
        
        if not wallet:
            print(f"У вас нет кошелька '{currency.upper()}'. "
                  f"Добавьте валюту: она создаётся автоматически при первой покупке.")
            return
        
        wallet.withdraw(amount)
        portfolio_manager.save_portfolio(portfolio)
        
        print(f"Продажа выполнена: {amount:.4f} {currency.upper()}")
        print("Изменения в портфеле:")
        print(f"- {currency.upper()}: стало {wallet.balance:.4f}")
        
    except Exception as e:
        print(f"Ошибка при продаже: {e}")


def get_rate(from_currency: str, to_currency: str):
    """Получение курса валюты"""
    # Временная заглушка - будет заменена на реальные данные из API
    exchange_rates = {
        'BTC_USD': 59337.21,
        'EUR_USD': 1.0786,
        'USD_USD': 1.0,
        'RUB_USD': 0.01016,
        'ETH_USD': 3720.00
    }
    
    rate_key = f"{from_currency.upper()}_{to_currency.upper()}"
    
    if rate_key in exchange_rates:
        rate = exchange_rates[rate_key]
        reverse_rate = 1 / rate if rate != 0 else 0
        print(f"Курс {from_currency.upper()}→{to_currency.upper()}: {rate:.6f}")
        print(f"Обратный курс {to_currency.upper()}→{from_currency.upper()}: {reverse_rate:.6f}")
    else:
        print(f"Курс {from_currency.upper()}→{to_currency.upper()} недоступен. "
              f"Повторите попытку позже.")