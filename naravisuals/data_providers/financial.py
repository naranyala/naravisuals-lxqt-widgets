"""Currency and Crypto data providers."""
import time
from typing import Any

from naravisuals.daemon.dbus_service import WidgetProvider


class CurrencyProvider(WidgetProvider):
    PROVIDER_ID = "currency"

    def __init__(self):
        super().__init__()
        self._base_currency = "USD"
        self._target_currencies = ["EUR", "GBP", "JPY"]
        self._last_data: dict[str, Any] = {}
        self._last_update = 0.0
        self._update_interval = 300.0  # 5 minutes

    def start(self):
        self._last_update = 0.0

    def get_data(self) -> dict[str, Any]:
        now = time.time()
        if now - self._last_update > self._update_interval:
            self._fetch_rates()
            self._last_update = now
        return self._last_data

    def set_base_currency(self, currency: str):
        self._base_currency = currency.upper()
        self._last_update = 0.0

    def set_target_currencies(self, currencies: list[str]):
        self._target_currencies = [c.upper() for c in currencies]
        self._last_update = 0.0

    def _fetch_rates(self):
        try:
            import requests

            targets = ",".join(self._target_currencies)
            url = f"https://api.exchangerate-api.com/v4/latest/{self._base_currency}"
            r = requests.get(url, timeout=10)
            data = r.json()

            rates = {}
            for currency in self._target_currencies:
                if currency in data.get("rates", {}):
                    rates[currency] = data["rates"][currency]

            self._last_data = {
                "base": self._base_currency,
                "rates": rates,
                "available": True,
                "last_update": data.get("time_last_update_utc", ""),
            }
        except Exception:
            self._last_data = {
                "base": self._base_currency,
                "rates": {},
                "available": False,
            }


class CryptoProvider(WidgetProvider):
    PROVIDER_ID = "crypto"

    def __init__(self):
        super().__init__()
        self._coins = ["bitcoin", "ethereum", "litecoin"]
        self._last_data: dict[str, Any] = {}
        self._last_update = 0.0
        self._update_interval = 60.0  # 1 minute

    def start(self):
        self._last_update = 0.0

    def get_data(self) -> dict[str, Any]:
        now = time.time()
        if now - self._last_update > self._update_interval:
            self._fetch_prices()
            self._last_update = now
        return self._last_data

    def set_coins(self, coins: list[str]):
        self._coins = [c.lower() for c in coins]
        self._last_update = 0.0

    def _fetch_prices(self):
        try:
            import requests

            ids = ",".join(self._coins)
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
            r = requests.get(url, timeout=10)
            data = r.json()

            prices = {}
            for coin in self._coins:
                if coin in data:
                    prices[coin] = {
                        "usd": data[coin].get("usd", 0),
                        "change_24h": data[coin].get("usd_24h_change", 0),
                    }

            self._last_data = {
                "coins": prices,
                "available": True,
            }
        except Exception:
            self._last_data = {
                "coins": {},
                "available": False,
            }
