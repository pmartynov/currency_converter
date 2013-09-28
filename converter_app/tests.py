"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.utils import unittest
from django.test.client import Client
from django.core.urlresolvers import reverse
from converter_app.models import Currency, ExchangeRate


class ConverterTestCase(unittest.TestCase):
    def setUp(self):
        usd = Currency(short_name="USD", long_name="Dollar")
        rub = Currency(short_name="RUB", long_name="Rouble")
        usd.save()
        rub.save()

        ExchangeRate(currency_from=usd, currency_to=usd, rate=1).save()
        ExchangeRate(currency_from=usd, currency_to=rub, rate=100500).save()

        self.client = Client()

    def get_response_obj(self, r_format):
        kwargs = {'curr_from': "USD", 'curr_to': "RUB", 'amount': 60.0, 'response_format': r_format}
        return self.client.get(reverse("conversion_result", kwargs=kwargs))

    def test_text_request_returns_text(self):
        response = self.get_response_obj("text")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("text/plain" in response._headers["content-type"][1])

    def test_json_request_returns_json(self):
        response = self.get_response_obj("json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("application/json" in response._headers["content-type"][1])

    def test_html_request_returns_html(self):
        response = self.get_response_obj("html")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("text/html" in response._headers["content-type"][1])
