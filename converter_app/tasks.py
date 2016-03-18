from datetime import timedelta

import requests
from celery.task import periodic_task

from .models import Currency, ExchangeRate
from .external_settings import OER_LATEST_URL, OER_CURRENCIES_URL


@periodic_task(run_every=timedelta(minutes=60))
def update_currencies():
    try:
        currencies = requests.get(OER_CURRENCIES_URL).json()
    except requests.exceptions.ConnectionError:
        return

    for short, long in currencies.iteritems():
        Currency.objects.get_or_create(short_name=short, long_name=long.encode('unicode_escape'))


@periodic_task(run_every=timedelta(minutes=60))
def update_rates():
    try:
        rates = requests.get(OER_LATEST_URL).json()["rates"]
    except (requests.exceptions.ConnectionError, KeyError):
        return

    try:
        curr_from = Currency.objects.get(short_name="USD")
    except Currency.DoesNotExist:
        return
    for short, rate in rates.iteritems():
        try:
            curr_to = Currency.objects.get(short_name=short)
        except Currency.DoesNotExist:
            continue
        ex_rate, created = ExchangeRate.objects.get_or_create(currency_from=curr_from, currency_to=curr_to)
        ex_rate.rate = rate
        ex_rate.save()
