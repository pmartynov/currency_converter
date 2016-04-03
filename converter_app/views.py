import decimal
import json
import sys
from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse

from .cache_wrappers import get_currencies
from .helpers import strip_zeros, build_url
from .models import Currency, ExchangeRate


def _render_error_html(request, status, message):
    return TemplateResponse(request, 'error.html', context={'message': message}, status=status)


def _process_error(request, status, message, response_format):
    if response_format == "html":
        return _render_error_html(request, status, message)
    elif response_format == "json":
        return HttpResponse(json.dumps({'success': False, 'error': message}), content_type="application/json")
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


def landing(request):
    if request.method == 'POST':
        POST = request.POST
        if 'from' in POST and 'to' in POST and 'amount' in POST:
            kwargs = {
                'curr_from': POST['from'], 'curr_to': POST['to'], 'amount': POST['amount']
            }
            return HttpResponseRedirect(build_url('conversion_result', get=kwargs))

    return render_to_response('landing.html', {'currencies': get_currencies()}, RequestContext(request))


def conversion_result(request):
    curr_from = request.GET.get('curr_from', None)
    curr_to = request.GET.get('curr_to', None)
    amount = request.GET.get('amount', None)
    response_format = request.GET.get('response_format', 'html')

    if not all([curr_from, curr_to, amount]):
        return _process_error(request, 400, 'Incorrect query parameters', response_format)

    currencies = get_currencies()

    try:
        amount = Decimal(amount)
    except decimal.InvalidOperation:
        return _process_error(request, 400, 'The amount is incorrect', response_format)

    try:
        curr_usd = Currency.objects.get(short_name='USD')
        curr_from = Currency.objects.get(short_name=curr_from)
        curr_to = Currency.objects.get(short_name=curr_to)

        ex_rate_from = ExchangeRate.objects.get(currency_from=curr_usd, currency_to=curr_from)
        ex_rate_to = ExchangeRate.objects.get(currency_from=curr_usd, currency_to=curr_to)

        result = amount / ex_rate_from.rate * ex_rate_to.rate
    except (Currency.DoesNotExist, ExchangeRate.DoesNotExist, ZeroDivisionError):
        return _process_error(request, 400, 'Currency is not supported', response_format)

    conversion = {
        'curr_from': curr_from.short_name,
        'curr_to': curr_to.short_name,
        'amount': strip_zeros(amount),
        'result': strip_zeros(result),
        'currencies': currencies
    }

    process_conversion_result = getattr(sys.modules[__name__], "_conversion_result_%s" % response_format)
    return process_conversion_result(request, conversion)
