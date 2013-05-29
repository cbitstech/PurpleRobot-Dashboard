from django.conf.urls.defaults import *
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page

from views import *

urlpatterns = patterns('',
    url(r'^(?P<report_id>\d+)/content$', report_contents, name='brain_report_contents'),
)
