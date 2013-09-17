from django.contrib import admin
from mobilyze.models import *

class CachedMobilyzeReportAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'report_type', 'generated')

admin.site.register(CachedMobilyzeReport, CachedMobilyzeReportAdmin)
