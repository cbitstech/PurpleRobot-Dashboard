from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
    url(r'^log$', log_event, name='log_event'),
)
