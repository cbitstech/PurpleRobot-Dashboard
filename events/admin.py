from django.contrib import admin

from models import *

class EventAdmin(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.logged.strftime("%d %b %Y %H:%M:%S")

    time_seconds.short_description = 'Log Date'    

    list_display = ('user_id', 'logged', 'event_type', 'error_type', 'error_location', 'latitude', 'longitude', 'altitude', 'time_drift_ms')
    list_filter = ['event_type', 'logged', 'recorded', 'error_type', 'error_location', 'user_id']

admin.site.register(Event, EventAdmin)
