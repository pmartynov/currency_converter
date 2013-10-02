from django.core.cache import cache

from .models import Currency, ExchangeRate


CURRENCIES_KEY = "currencies"
EXCHANGE_RATES = "exchange_rates"


def get_currencies():
    currencies = cache.get(CURRENCIES_KEY)
    if not currencies:
        currencies = Currency.objects.all().order_by("short_name")
        cache.set(CURRENCIES_KEY, currencies)

    return currencies


def get_exchange_rates():
    exchange_rates = cache.get(EXCHANGE_RATES)
    if not exchange_rates:
        exchange_rates = ExchangeRate.objects.select_related("currency_from", "currency_to").all()\
            .order_by("currency_from", "currency_to")
        cache.set(EXCHANGE_RATES, exchange_rates)

    return exchange_rates
