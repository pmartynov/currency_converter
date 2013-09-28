from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.template.response import TemplateResponse
from django.template import loader
from decimal import Decimal
from converter_app.models import Currency, ExchangeRate
from converter_app import helpers
import sys
import json


def _get_redirect_obj(req):
    kwargs = {'curr_from': req["from"], 'curr_to': req["to"], 'amount': req["amount"], 'response_format': "html"}
    return HttpResponseRedirect(reverse('conversion_result', kwargs=kwargs))


def _render_error_html(request, status, message):
    return TemplateResponse(request, 'error.html', context={'message': message}, status=status)


def _process_error(request, status, message, response_format):
    if response_format == "html":
        return _render_error_html(request, status, message)
    elif response_format == "json":
        response_data = {'success': False, 'error': message}
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    elif response_format == "text":
        return HttpResponse(message, content_type="text/plain")
    else:
        return TemplateResponse(request, 'error.html', context={'message': 'Format is not supported'}, status=400)


def _conversion_result_html(request, conversion):
    return render_to_response('conversion_result.html', conversion, RequestContext(request))


def _conversion_result_json(request, conversion):
    return HttpResponse(
        json.dumps({'success': True, 'result': float(conversion["result"])}), content_type="application/json")


def _conversion_result_text(request, conversion):
    return HttpResponse(conversion["result"], content_type="text/plain")


CURRENCIES_KEY = "currencies"
EXCHANGE_RATES = "exchange_rates"


def _get_currencies():
    currencies = cache.get(CURRENCIES_KEY)
    if not currencies:
        currencies = Currency.objects.all().order_by("short_name")
        cache.set(CURRENCIES_KEY, currencies)

    return currencies


def _get_exchange_rates():
    exchange_rates = cache.get(EXCHANGE_RATES)
    if not exchange_rates:
        exchange_rates = ExchangeRate.objects.select_related("currency_from", "currency_to")\
            .all().order_by("currency_from", "currency_to")
        cache.set(EXCHANGE_RATES, exchange_rates)

    return exchange_rates


def error404(request):
    t = loader.get_template('404.html')
    return HttpResponseNotFound(t.render(RequestContext(request)))


def error500(request):
    t = loader.get_template('500.html')
    return HttpResponseServerError(t.render(RequestContext(request)))


def landing(request):
    if request.method == 'POST':
        return _get_redirect_obj(request.POST)

    return render_to_response('landing.html', {'currencies': _get_currencies()}, RequestContext(request))


def conversion_result(request, curr_from, curr_to, amount, response_format):
    if request.method == 'POST':
        return _get_redirect_obj(request.POST)

    try:
        amount = Decimal(amount)
        currencies = _get_currencies()
        exchange_rates = _get_exchange_rates()

        curr_usd = currencies[helpers._binary_search(currencies, Currency(short_name="USD"))]
        curr_from = currencies[helpers._binary_search(currencies, Currency(short_name=curr_from))]
        curr_to = currencies[helpers._binary_search(currencies, Currency(short_name=curr_to))]

        ex_rate_from = exchange_rates[
            helpers._binary_search(exchange_rates, ExchangeRate(currency_from=curr_usd, currency_to=curr_from))]
        ex_rate_to = exchange_rates[
            helpers._binary_search(exchange_rates, ExchangeRate(currency_from=curr_usd, currency_to=curr_to))]

        result = amount / ex_rate_from.rate * ex_rate_to.rate

        conversion = {
            'curr_from': curr_from.short_name,
            'curr_to': curr_to.short_name,
            'amount': helpers._strip_zeros(amount),
            'result': helpers._strip_zeros(result),
            'currencies': currencies
        }

        process_conversion_result = getattr(sys.modules[__name__], "_conversion_result_%s" % response_format)
        return process_conversion_result(request, conversion)

    except AssertionError:
        return _process_error(request, 400, 'Currency is not supported', response_format)
