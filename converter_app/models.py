from django.db import models


class Currency(models.Model):
    short_name = models.CharField(primary_key=True, max_length=3)
    long_name = models.CharField(max_length=50)


class ExchangeRate(models.Model):
    currency_from = models.ForeignKey(Currency, related_name="+", unique=False)
    currency_to = models.ForeignKey(Currency, related_name="+", unique=False)
    rate = models.DecimalField(max_digits=24, decimal_places=12, unique=False)

    def validate_unique(self, *args, **kwargs):
        super(ExchangeRate, self).validate_unique(*args, **kwargs)
        ex_rate = self.__class__.objects.get(currency_from=self.currency_from, currency_to=self.currency_to)

        if ex_rate.exists():
            raise ValidationError('ExchangeRate row with these currencies already exists')
