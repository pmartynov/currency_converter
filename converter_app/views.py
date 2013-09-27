from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.template.response import TemplateResponse
from django.template import loader
from converter_app.models import Currency, ExchangeRate
from decimal import Decimal
import sys
import json


def _strip_zeros(dec):
    return Decimal(str(round(dec, 6)).strip('0').rstrip('.'))


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


def _conversion_result_html(request, result, conversion):
    return render_to_response('conversion_result.html', conversion, RequestContext(request))


def _conversion_result_json(request, result, conversion):
    return HttpResponse(json.dumps({'success': True, 'result': result}), content_type="application/json")


def _conversion_result_text(request, result, conversion):
    return HttpResponse(result, content_type="text/plain")


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


def _binary_search(a, x, lo=0, hi=None):
    if hi is None:
        hi = len(a)

    while lo < hi:
        mid = (lo + hi) / 2
        mid_model = a[mid]
        if mid_model.is_less_than(x):
            lo = mid + 1
        elif x.is_less_than(mid_model):
            hi = mid
        else:
            return mid

    return -1


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
        if amount < 0:
            return _process_error(request, 403, 'Amount is negative', response_format)

        currencies = _get_currencies()
        exchange_rates = _get_exchange_rates()

        curr_usd = currencies[_binary_search(currencies, Currency(short_name="USD"))]
        curr_from = currencies[_binary_search(currencies, Currency(short_name=curr_from))]
        curr_to = currencies[_binary_search(currencies, Currency(short_name=curr_to))]

        ex_rate_from = exchange_rates[
            _binary_search(exchange_rates, ExchangeRate(currency_from=curr_usd, currency_to=curr_from))]
        ex_rate_to = exchange_rates[
            _binary_search(exchange_rates, ExchangeRate(currency_from=curr_usd, currency_to=curr_to))]

        result = amount / ex_rate_from.rate * ex_rate_to.rate

        conversion = {
            'curr_from': curr_from.short_name,
            'curr_to': curr_to.short_name,
            'amount': _strip_zeros(amount),
            'result': _strip_zeros(result),
            'currencies': currencies
        }

        process_conversion_result = getattr(sys.modules[__name__], "_conversion_result_%s" % response_format)
        return process_conversion_result(request, result, conversion)

    except KeyError:
        return _process_error(request, 400, 'Currency is not supported', response_format)
    except ValueError:
        return _process_error(request, 400, 'Amount is neither decimal nor integer', response_format)
