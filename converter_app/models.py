from django.db import models
from django.core.exceptions import ValidationError


class Currency(models.Model):
    short_name = models.CharField(primary_key=True, max_length=3)
    long_name = models.CharField(max_length=50)

    def is_less_than(self, other):
        return self.short_name < other.short_name

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.short_name == other.short_name

    def __unicode__(self):
        return "%s - %s" % (self.short_name, self.long_name)

    class Meta:
        verbose_name_plural = "currencies"


class ExchangeRate(models.Model):
    currency_from = models.ForeignKey(Currency, related_name="+", unique=False)
    currency_to = models.ForeignKey(Currency, related_name="+", unique=False)
    rate = models.DecimalField(max_digits=24, decimal_places=12, unique=False)

    def validate_unique(self, *args, **kwargs):
        super(ExchangeRate, self).validate_unique(*args, **kwargs)
        ex_rate = self.__class__.objects.get(currency_from=self.currency_from, currency_to=self.currency_to)

        if ex_rate.exists():
            raise ValidationError('ExchangeRate row with these currencies already exists')

    def is_less_than(self, other):
        return self.currency_from.is_less_than(other.currency_from) or\
            self.currency_from == other.currency_from and self.currency_to.is_less_than(other.currency_to)

    @property
    def rate_label(self):
        return "%s to %s" % (self.currency_from.short_name, self.currency_to.short_name)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.currency_from == other.currency_from\
            and self.currency_to == other.currency_to
