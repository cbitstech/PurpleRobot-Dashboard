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
    url(r'^quality', mobilyze_quality, name='mobilyze_quality'),
    url(r'^num_stats/group/(?P<question>.+)', mobilyze_num_stats, name='mobilyze_num_stats_group'),
    url(r'^nom_stats/group/(?P<question>.+)', mobilyze_nom_stats, name='mobilyze_nom_stats_group'),
    url(r'^num_stats/(?P<user_id>\w+)/(?P<question>.+)', mobilyze_num_stats, name='mobilyze_num_stats'),
    url(r'^nom_stats/(?P<user_id>\w+)/(?P<question>.+)', mobilyze_nom_stats, name='mobilyze_nom_stats'),
    url(r'^numeric\.xls', mobilyze_numeric, name='mobilyze_numeric'),
    url(r'^demographic\.xls', mobilyze_demographic, name='mobilyze_demographic'),
    url(r'^scheme_config', scheme_config, name='scheme_config'),
)
