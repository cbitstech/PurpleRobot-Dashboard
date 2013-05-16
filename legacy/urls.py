try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
    url(r'^fetch/(?P<database>[a-z0-9]+)/(?P<table>[a-zA-Z0-9_\. ]+)/(?P<column>[a-zA-Z0-9_,]+)/(?P<timestamp>[a-zA-Z0-9_]+)$', legacy_fetch_data, name='legacy_fetch_data'),
    url(r'^(?P<database>.+)$', database_contents, name='legacy_database_contents'),
    url(r'^$', legacy_status, name='legacy_status'),
)
