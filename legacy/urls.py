try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
    url(r'^(?P<database>.+)$', database_contents, name='legacy_database_contents'),
    url(r'^$', legacy_status, name='legacy_status'),
)
