from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
import sys
import requests
import json

OPEN_EXCHANGE_RATE_APP_ID = "8c5757490b42495c892fe171fa2603a7"
OPEN_EXCHANGE_RATE_URL = "http://openexchangerates.org/api/latest.json?app_id=" + OPEN_EXCHANGE_RATE_APP_ID

currencies = {
    "AED": "United Arab Emirates Dirham",
    "AFN": "Afghan Afghani",
    "ALL": "Albanian Lek",
    "AMD": "Armenian Dram"
}


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
    response_data = {'success': True, 'result': result}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def _conversion_result_text(request, result, conversion):
    return HttpResponse(result, content_type="text/plain")


def landing(request):
    if request.method == 'POST':
        return _get_redirect_obj(request.POST)

    return render_to_response('landing.html', {'currencies': currencies}, RequestContext(request))


def conversion_result(request, curr_from, curr_to, amount, response_format):
    if request.method == 'POST':
        return _get_redirect_obj(request.POST)

    try:
        amount = float(amount)
        if amount < 0:
            return _process_error(request, 403, 'Amount is negative', response_format)

        rates = requests.get(OPEN_EXCHANGE_RATE_URL).json()["rates"]
        result = amount / rates[curr_from] * rates[curr_to]

        conversion = {
            'curr_from': curr_from,
            'curr_to': curr_to,
            'amount': str(amount).rstrip('0').rstrip('.'),
            'result': str(result).rstrip('0').rstrip('.'),
            'currencies': currencies
        }

        process_conversion_result = getattr(sys.modules[__name__], "_conversion_result_%s" % response_format)
        return process_conversion_result(request, result, conversion)

    except requests.exceptions.ConnectionError:
        return _process_error(request, 503, 'Openexchangerates.org is not available', response_format)
    except KeyError:
        return _process_error(request, 400, 'Currency is not supported', response_format)
    except ValueError:
        return _process_error(request, 400, 'Amount is neither decimal nor integer', response_format)
