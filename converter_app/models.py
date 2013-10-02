from django.db import models


class Currency(models.Model):
    short_name = models.CharField(primary_key=True, max_length=3)
    long_name = models.CharField(max_length=50)

    def is_less_than(self, other):
        return self.short_name < other.short_name

    def __unicode__(self):
        return "%s - %s" % (self.short_name, self.long_name)

    class Meta:
        verbose_name_plural = "currencies"
        ordering = ('short_name',)


class ExchangeRate(models.Model):
    currency_from = models.ForeignKey(Currency, related_name="+", unique=False)
    currency_to = models.ForeignKey(Currency, related_name="+", unique=False)
    rate = models.DecimalField(max_digits=24, decimal_places=12, unique=False)

    def is_less_than(self, other):
        return self.currency_from.is_less_than(other.currency_from) or\
            self.currency_from == other.currency_from and self.currency_to.is_less_than(other.currency_to)

    @property
    def rate_label(self):
        return "%s to %s" % (self.currency_from.short_name, self.currency_to.short_name)

    class Meta:
        unique_together = ('currency_from', 'currency_to')
        ordering = ('currency_from', 'currency_to')
