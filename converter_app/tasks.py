from __future__ import absolute_import
from django.db import transaction
from celery.task import periodic_task
from celery.task.schedules import crontab
from converter_app.models import Currency, ExchangeRate
import requests


OER_APP_ID = "8c5757490b42495c892fe171fa2603a7"
OER_LATEST_URL = "http://openexchangerates.org/api/latest.json?app_id=" + OER_APP_ID
OER_CURRENCIES_URL = "http://openexchangerates.org/api/currencies.json?app_id=" + OER_APP_ID


@periodic_task(run_every=crontab(hour="0-23"))
@transaction.commit_manually
def update_currencies():
    try:
        currencies = requests.get(OER_CURRENCIES_URL).json()

        for short, long in currencies.iteritems():
            currency = Currency(short_name=short, long_name=long.encode('unicode_escape'))
            currency.save()

        transaction.commit()

    except requests.exceptions.ConnectionError:
        pass


@periodic_task(run_every=crontab(hour="0-23"))
@transaction.commit_manually
def update_rates():
    try:
        rates = requests.get(OER_LATEST_URL).json()["rates"]

        for short, rate in rates.iteritems():
            curr_from = Currency.objects.get(short_name="USD")
            curr_to = Currency.objects.get(short_name=short)
            ex_rate, created = ExchangeRate.objects.get_or_create(
                currency_from=curr_from, currency_to=curr_to, defaults={'rate': 1.0})
            ex_rate.rate = rate
            ex_rate.save()

        transaction.commit()

    except requests.exceptions.ConnectionError:
        pass