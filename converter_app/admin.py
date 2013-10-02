from django.contrib import admin

from .models import ExchangeRate, Currency
from .helpers import strip_zeros


class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('rate_label', 'currency_from', 'currency_to', 'stripped_rate')
    readonly_fields = ('rate_label', 'currency_from', 'currency_to', 'stripped_rate')
    ordering = ('currency_from', 'currency_to')

    def stripped_rate(self, obj):
        return strip_zeros(obj.rate)


admin.site.register(Currency)
admin.site.register(ExchangeRate, ExchangeRateAdmin)
