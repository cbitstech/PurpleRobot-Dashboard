from django.contrib import admin
from data_sources.models import DataSource, DataReport

class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(DataSource, DataSourceAdmin)


class DataReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'table', 'report_type', 'start_time', 'end_time',)

admin.site.register(DataReport, DataReportAdmin)
