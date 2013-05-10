from django.conf.urls.defaults import *
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page

from views import *

urlpatterns = patterns('',
    url(r'^list/(?P<slug>.+)', participants_list, name='participants_list'),
)
