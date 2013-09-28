from decimal import Decimal


def _strip_zeros(dec):
    return Decimal(str(round(dec, 6)).strip('0').rstrip('.'))


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
