import argparse
from prettytable import PrettyTable
from valutatrade_hub.core.usecases import user_manager, portfolio_manager
from valutatrade_hub.parser_service.updater import RatesUpdater
from valutatrade_hub.parser_service.storage import storage
from valutatrade_hub.core.exchange_rates import ExchangeRateService
from valutatrade_hub.core.exceptions import CurrencyNotFoundError


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

    # logout command
    subparsers.add_parser('logout', help='Logout user')

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

    # update-rates command
    update_parser = subparsers.add_parser('update-rates', help='Update currency rates')
    update_parser.add_argument('--source', choices=['coingecko', 'exchangerate', 'all'], 
                              default='all', help='Data source to update from')

    # show-rates command
    show_rates_parser = subparsers.add_parser('show-rates', help='Show current rates')
    show_rates_parser.add_argument('--currency', help='Filter by currency code')
    show_rates_parser.add_argument('--top', type=int, help='Show top N currencies by rate')
    show_rates_parser.add_argument('--base', default='USD', help='Base currency for display')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'register':
            register_user(args.username, args.password)
        elif args.command == 'login':
            login_user(args.username, args.password)
        elif args.command == 'logout':
            logout_user()
        elif args.command == 'show-portfolio':
            show_portfolio(args.base)
        elif args.command == 'buy':
            buy_currency(args.currency, args.amount)
        elif args.command == 'sell':
            sell_currency(args.currency, args.amount)
        elif args.command == 'get-rate':
            get_rate(args.from_currency, args.to)
        elif args.command == 'update-rates':
            update_rates(args.source)
        elif args.command == 'show-rates':
            show_rates(args.currency, args.top, args.base)
    except Exception as e:
        print(f"Ошибка: {e}")


def register_user(username: str, password: str):
    """Регистрация нового пользователя"""
    user = user_manager.register_user(username, password)
    print(f"Пользователь '{username}' зарегистрирован (id={user.user_id}). "
          f"Войдите: login --username {username} --password ****")


def login_user(username: str, password: str):
    """Вход пользователя"""
    user_manager.login(username, password)
    print(f"Вы вошли как '{username}'")


def logout_user():
    """Выход пользователя"""
    user_manager.logout()
    print("Вы вышли из системы")


def show_portfolio(base_currency: str):
    """Показать портфель пользователя с реальными курсами"""
    if not user_manager.current_user:
        print("Сначала выполните login")
        return

    portfolio = portfolio_manager.get_portfolio()
    
    if not portfolio.wallets:
        print("Портфель пуст")
        return

    print(f"Портфель пользователя '{user_manager.current_user.username}' (база: {base_currency}):")
    
    total_value = 0.0
    rates_used = {}
    
    for currency, wallet in portfolio.wallets.items():
        try:
            if currency == base_currency:
                value = wallet.balance
                rate = 1.0
            else:
                rate = ExchangeRateService.get_rate(currency, base_currency)
                value = wallet.balance * rate
                rates_used[f"{currency}_{base_currency}"] = rate
                
            total_value += value
            print(f"- {currency}: {wallet.balance:.4f} → {value:.2f} {base_currency} (курс: {rate:.4f})")
            
        except CurrencyNotFoundError:
            print(f"- {currency}: {wallet.balance:.4f} → [КУРС НЕДОСТУПЕН]")
    
    print("---------------------------------")
    print(f"ИТОГО: {total_value:,.2f} {base_currency}")
    
    # Предупреждение об устаревших данных
    if not ExchangeRateService.is_cache_valid():
        print("\n⚠️ Внимание: данные о курсах устарели. Выполните 'update-rates' для обновления.")


def buy_currency(currency: str, amount: float):
    """Покупка валюты через usecases с логированием"""
    if not user_manager.current_user:
        print("Сначала выполните login")
        return

    try:
        result = portfolio_manager.buy_currency(
            user_manager.current_user.user_id, 
            currency, 
            amount
        )
        
        # Расчет стоимости покупки
        try:
            rate = ExchangeRateService.get_rate(currency.upper(), 'USD')
            cost_usd = amount * rate
            cost_info = f"Оценочная стоимость: {cost_usd:.2f} USD (курс: {rate:.4f})"
        except CurrencyNotFoundError:
            cost_info = "Не удалось рассчитать стоимость (курс недоступен)"
        
        print(f"✅ Покупка выполнена: {amount:.4f} {currency.upper()}")
        print("💳 Изменения в портфеле:")
        print(f"   - {currency.upper()}: было {result['old_balance']:.4f} → стало {result['new_balance']:.4f}")
        print(f"💰 {cost_info}")
        
    except Exception as e:
        print(f"❌ Ошибка при покупке: {e}")


def sell_currency(currency: str, amount: float):
    """Продажа валюты через usecases с логированием"""
    if not user_manager.current_user:
        print("Сначала выполните login")
        return

    try:
        result = portfolio_manager.sell_currency(
            user_manager.current_user.user_id,
            currency, 
            amount
        )
        
        # Расчет выручки
        try:
            rate = ExchangeRateService.get_rate(currency.upper(), 'USD')
            revenue_usd = amount * rate
            revenue_info = f"Оценочная выручка: {revenue_usd:.2f} USD (курс: {rate:.4f})"
        except CurrencyNotFoundError:
            revenue_info = "Не удалось рассчитать выручку (курс недоступен)"
        
        print(f"✅ Продажа выполнена: {amount:.4f} {currency.upper()}")
        print("💳 Изменения в портфеле:")
        print(f"   - {currency.upper()}: было {result['old_balance']:.4f} → стало {result['new_balance']:.4f}")
        print(f"💰 {revenue_info}")
        
    except Exception as e:
        print(f"❌ Ошибка при продаже: {e}")


def get_rate(from_currency: str, to_currency: str):
    """Получение курса валюты с проверкой актуальности"""
    try:
        rate = ExchangeRateService.get_rate(from_currency, to_currency)
        reverse_rate = 1 / rate if rate != 0 else 0
        
        print(f"📊 Курс {from_currency.upper()}→{to_currency.upper()}: {rate:.6f}")
        print(f"🔄 Обратный курс {to_currency.upper()}→{from_currency.upper()}: {reverse_rate:.6f}")
        
        # Информация об актуальности данных
        if not ExchangeRateService.is_cache_valid():
            last_update = ExchangeRateService.get_last_refresh_time()
            print(f"⚠️ Внимание: данные устарели. Последнее обновление: {last_update}")
            print("   Выполните 'update-rates' для получения актуальных курсов.")
        else:
            print(f"✅ Данные актуальны (обновлено: {ExchangeRateService.get_last_refresh_time()})")
            
    except CurrencyNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Попробуйте выполнить 'update-rates' для загрузки актуальных курсов.")


def update_rates(source: str):
    """Обновление курсов валют"""
    sources_map = {
        'all': ('coingecko', 'exchangerate'),
        'coingecko': ('coingecko',),
        'exchangerate': ('exchangerate',)
    }
    
    selected_sources = sources_map.get(source, ('coingecko', 'exchangerate'))
    
    updater = RatesUpdater()
    result = updater.run_update(selected_sources)
    
    if result['success']:
        print("✅ Обновление завершено успешно!")
        print(f"📊 Обновлено курсов: {result['rates_count']}")
        print(f"⏱️ Время выполнения: {result['duration_ms']}ms")
    else:
        print("⚠️ Обновление завершено с ошибками")
        print(f"📊 Обновлено курсов: {result['rates_count']}")
        print("Ошибки:")
        for error in result['errors']:
            print(f"  - {error}")
        print("Подробности смотрите в логах.")


def show_rates(currency: str = None, top: int = None, base: str = 'USD'):
    """Показать текущие курсы валют"""
    data = storage.get_current_rates()
    
    if not data.get('pairs'):
        print("Локальный кеш курсов пуст. Выполните 'update-rates', чтобы загрузить данные.")
        return
    
    # Фильтруем пары по базовой валюте
    relevant_pairs = {}
    for pair, info in data['pairs'].items():
        if pair.endswith(f"_{base}"):
            relevant_pairs[pair] = info
    
    if not relevant_pairs:
        print(f"Курсы для базовой валюты '{base}' не найдены в кеше.")
        return
    
    # Фильтруем по валюте если указана
    if currency:
        currency = currency.upper()
        filtered_pairs = {k: v for k, v in relevant_pairs.items() 
                         if k.startswith(f"{currency}_") or k.endswith(f"_{currency}")}
        if not filtered_pairs:
            print(f"Курс для '{currency}' не найден в кеше.")
            return
        relevant_pairs = filtered_pairs
    
    # Сортируем по курсу (для top N)
    sorted_pairs = sorted(relevant_pairs.items(), 
                         key=lambda x: x[1]['rate'], 
                         reverse=True)
    
    # Ограничиваем количество если указан top
    if top:
        sorted_pairs = sorted_pairs[:top]
    
    # Создаем таблицу
    table = PrettyTable()
    table.field_names = ["Пара", "Курс", "Обновлено", "Источник"]
    table.align["Пара"] = "l"
    table.align["Курс"] = "r"
    
    for pair, info in sorted_pairs:
        # Форматируем время
        updated_at = info['updated_at']
        if 'T' in updated_at:
            updated_at = updated_at.split('T')[1].split('.')[0]  # Берем только время
        
        table.add_row([
            pair,
            f"{info['rate']:,.4f}",
            updated_at,
            info['source']
        ])
    
    print(f"Курсы из кеша (обновлено: {data['last_refresh']}):")
    print(table)
    
    # Предупреждение если кэш устарел
    if not storage.is_cache_valid():
        print("\n⚠️ Внимание: данные в кеше устарели. Рекомендуется выполнить 'update-rates'.")


if __name__ == '__main__':
    main()