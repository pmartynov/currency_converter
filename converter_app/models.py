from django.db import models

class ExchangeRate(models.Model):
    currency_from = models.CharField(max_length=3)
    currency_to = models.CharField(max_length=3)
    exchange_rates = models.DecimalField(max_digits=12, decimal_places=12);

class Currency(models.Model):
    short_name = models.CharField(max_length=3)
    long_name = models.CharField(max_length=20)

