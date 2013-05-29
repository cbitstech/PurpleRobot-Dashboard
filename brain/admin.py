from django.contrib import admin

from brain.models import ReportJob

class ReportJobAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_start', 'job_end', 'result_type',)

admin.site.register(ReportJob, ReportJobAdmin)
