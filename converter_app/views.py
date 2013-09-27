from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
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


def landing(request):
    if request.method == 'POST':
        return _get_redirect_obj(request.POST)

    return render_to_response('landing.html', {'currencies': Currency.objects.all()}, RequestContext(request))


def conversion_result(request, curr_from, curr_to, amount, response_format):
    if request.method == 'POST':
        return _get_redirect_obj(request.POST)

    try:
        amount = Decimal(amount)
        if amount < 0:
            return _process_error(request, 403, 'Amount is negative', response_format)

        curr_usd = Currency.objects.get(short_name="USD")
        curr_from = Currency.objects.get(short_name=curr_from)
        curr_to = Currency.objects.get(short_name=curr_to)
        ex_rate_from = ExchangeRate.objects.get(currency_from=curr_usd, currency_to=curr_from)
        ex_rate_to = ExchangeRate.objects.get(currency_from=curr_usd, currency_to=curr_to)

        result = amount / ex_rate_from.rate * ex_rate_to.rate

        conversion = {
            'curr_from': curr_from.short_name,
            'curr_to': curr_to.short_name,
            'amount': _strip_zeros(amount),
            'result': _strip_zeros(result),
            'currencies': Currency.objects.all()
        }

        process_conversion_result = getattr(sys.modules[__name__], "_conversion_result_%s" % response_format)
        return process_conversion_result(request, result, conversion)

    except KeyError:
        return _process_error(request, 400, 'Currency is not supported', response_format)
    except ValueError:
        return _process_error(request, 400, 'Amount is neither decimal nor integer', response_format)
