from datetime import timedelta

import requests
from django.db import transaction
from celery.task import periodic_task

from .models import Currency, ExchangeRate
from .external_settings import *


@periodic_task(run_every=timedelta(minutes=60))
@transaction.commit_manually
def update_currencies():
    try:
        currencies = requests.get(OER_CURRENCIES_URL).json()
    except requests.exceptions.ConnectionError:
        return

    for short, long in currencies.iteritems():
        currency = Currency(short_name=short, long_name=long.encode('unicode_escape'))
        currency.save()

    transaction.commit()


@periodic_task(run_every=timedelta(minutes=60))
@transaction.commit_manually
def update_rates():
    try:
        rates = requests.get(OER_LATEST_URL).json()["rates"]
    except (requests.exceptions.ConnectionError, KeyError):
        return

    curr_from = Currency.objects.get(short_name="USD")
    for short, rate in rates.iteritems():
        curr_to = Currency.objects.get(short_name=short)
        ex_rate, created = ExchangeRate.objects.get_or_create(currency_from=curr_from, currency_to=curr_to)
        ex_rate.rate = rate
        ex_rate.save()

    transaction.commit()

