from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import data_sources

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dashboard.views.home', name='home'),
    # url(r'^dashboard/', include('dashboard.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^data/', include('data_sources.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^participants/', include('participants.urls')),
    url(r'^mobilyze/', include('mobilyze.urls')),
    url(r'^legacy/', include('legacy.urls')),
    url(r'^brain/', include('brain.urls')),
    url(r'^$', include('website.urls')),
)
