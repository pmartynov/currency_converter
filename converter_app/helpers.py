import urllib
from decimal import Decimal

from django.core.urlresolvers import reverse


def strip_zeros(dec):
    dec = str(round(dec, 2)).strip('0').rstrip('.')
    return Decimal(dec) if dec else 0


def binary_search(a, x, lo=0, hi=None):
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

    assert False


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.urlencode(get)
    return url
