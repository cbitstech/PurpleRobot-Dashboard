from django.conf.urls.defaults import *
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page

from views import *

urlpatterns = patterns('',
    url(r'^', home, name='home'),
)
