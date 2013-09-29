"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from converter_app.models import Currency, ExchangeRate


class ConverterTestCase(TestCase):
    def setUp(self):
        usd = Currency(short_name="USD", long_name="Dollar")
        rub = Currency(short_name="RUB", long_name="Rouble")
        eur = Currency(short_name="EUR", long_name="Euro")
        pln = Currency(short_name="PLN", long_name="Zloty")
        ltl = Currency(short_name="LTL", long_name="Lit")

        for c in [usd, rub, eur, pln, ltl]:
            c.save()

        ExchangeRate(currency_from=usd, currency_to=usd, rate=1).save()
        ExchangeRate(currency_from=usd, currency_to=rub, rate=100500).save()
        ExchangeRate(currency_from=usd, currency_to=eur, rate=0.74).save()
        ExchangeRate(currency_from=eur, currency_to=eur, rate=1).save()
        ExchangeRate(currency_from=ltl, currency_to=pln, rate=1.22).save()

        self.client = Client()

    def get_response_obj(self, curr_from, curr_to, r_format):
        kwargs = {'curr_from': curr_from, 'curr_to': curr_to, 'amount': 10.0, 'response_format': r_format}
        return self.client.get(reverse("conversion_result", kwargs=kwargs))

    def test_text_request_returns_text(self):
        response = self.get_response_obj("USD", "RUB", "text")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("text/plain" in response._headers["content-type"][1])

    def test_json_request_returns_json(self):
        response = self.get_response_obj("USD", "RUB", "json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("application/json" in response._headers["content-type"][1])

    def test_html_request_returns_html(self):
        response = self.get_response_obj("USD", "RUB", "html")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("text/html" in response._headers["content-type"][1])

    def test_wrong_currency(self):
        response = self.get_response_obj("USD", "XXX", "text")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("text/plain" in response._headers["content-type"][1])
        self.assertEqual("Currency is not supported", response.content)

    def test_eur_to_eur(self):
        response = self.get_response_obj("EUR", "EUR", "text")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content, '10')

    def test_ltl_to_pln(self):
        response = self.get_response_obj("LTL", "PLN", "text")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content, '12.2')
