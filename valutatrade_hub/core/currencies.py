from abc import ABC, abstractmethod
from valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name: str, code: str):
        self._validate_code(code)
        self._validate_name(name)
        self._name = name
        self._code = code.upper()

    @property
    def name(self) -> str:
        return self._name

    @property
    def code(self) -> str:
        return self._code

    def _validate_code(self, code: str):
        if not code or not isinstance(code, str):
            raise ValueError("Код валюты должен быть непустой строкой")
        if not (2 <= len(code) <= 5):
            raise ValueError("Код валюты должен содержать от 2 до 5 символов")
        if not code.replace("_", "").isalnum():
            raise ValueError("Код валюты должен содержать только буквы, цифры и подчеркивания")

    def _validate_name(self, name: str):
        if not name or not isinstance(name, str):
            raise ValueError("Название валюты должно быть непустой строкой")

    @abstractmethod
    def get_display_info(self) -> str:
        pass

    def __str__(self) -> str:
        return self.get_display_info()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', code='{self.code}')"


class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self._issuing_country = issuing_country

    @property
    def issuing_country(self) -> str:
        return self._issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(name, code)
        self._algorithm = algorithm
        self._market_cap = market_cap

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @property
    def market_cap(self) -> float:
        return self._market_cap

    def get_display_info(self) -> str:
        mcap_str = f"{self.market_cap:.2e}" if self.market_cap > 1e6 else f"{self.market_cap:,.2f}"
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {mcap_str})"


# Реестр валют
class CurrencyRegistry:
    def __init__(self):
        self._currencies = {}
        self._initialize_currencies()

    def _initialize_currencies(self):
        # Фиатные валюты
        fiats = [
            FiatCurrency("US Dollar", "USD", "United States"),
            FiatCurrency("Euro", "EUR", "Eurozone"),
            FiatCurrency("Russian Ruble", "RUB", "Russia"),
            FiatCurrency("British Pound", "GBP", "United Kingdom"),
            FiatCurrency("Japanese Yen", "JPY", "Japan"),
        ]
        
        # Криптовалюты
        cryptos = [
            CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
            CryptoCurrency("Ethereum", "ETH", "Ethash", 4.5e11),
            CryptoCurrency("Litecoin", "LTC", "Scrypt", 6.5e9),
        ]
        
        for currency in fiats + cryptos:
            self._currencies[currency.code] = currency

    def get_currency(self, code: str) -> Currency:
        code = code.upper()
        if code not in self._currencies:
            raise CurrencyNotFoundError(code)
        return self._currencies[code]

    def get_all_currencies(self) -> list[Currency]:
        return list(self._currencies.values())

    def get_currency_codes(self) -> list[str]:
        return list(self._currencies.keys())


# Глобальный экземпляр реестра
currency_registry = CurrencyRegistry()

def get_currency(code: str) -> Currency:
    return currency_registry.get_currency(code)