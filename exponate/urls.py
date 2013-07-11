try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
    url(r'^responses.json', exponate_response, name='exponate_response'),
)
