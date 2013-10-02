from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('converter_app.views',
    url(r'^$', 'landing'),
    url(r'^(?P<amount>[0-9]+(\.[0-9]{1,2})?)/(?P<curr_from>\w{3})/to/(?P<curr_to>\w{3})/in/(?P<response_format>\w{4})$',
        'conversion_result', name="conversion_result"),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

# Adding context variables to 500 error template to load stat
handler500 = 'converter_app.error_handlers.error500'
