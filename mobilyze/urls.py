try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
    url(r'^verify/(?P<id>\w+)$', verify_id, name='verify_id'),
    url(r'^retire/(?P<id>\w+)$', retire_id, name='retire_id'),
    url(r'^activate/(?P<id>\w+)$', activate_id, name='activate_id'),
    url(r'^add_id$', add_id, name='add_id'),
    url(r'^status$', mobilyze_status, name='mobilyze_status'),
)
