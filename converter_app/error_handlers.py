from django.http import HttpResponseNotFound, HttpResponseServerError
from django.template import RequestContext
from django.template import loader


def error404(request):
    t = loader.get_template('404.html')
    return HttpResponseNotFound(t.render(RequestContext(request)))


def error500(request):
    t = loader.get_template('500.html')
    return HttpResponseServerError(t.render(RequestContext(request)))
