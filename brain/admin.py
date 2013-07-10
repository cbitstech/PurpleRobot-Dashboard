from django.contrib import admin

from brain.models import *

class ReportJobAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_start', 'job_end', 'result_type',)

admin.site.register(ReportJob, ReportJobAdmin)


class PerformanceMeasurementEndpointAdmin(admin.ModelAdmin):
    list_display = ('name', 'endpoint',)

admin.site.register(PerformanceMeasurementEndpoint, PerformanceMeasurementEndpointAdmin)


class ModelGeneratorEndpointAdmin(admin.ModelAdmin):
    list_display = ('name', 'endpoint', 'expect_type',)

admin.site.register(ModelGeneratorEndpoint, ModelGeneratorEndpointAdmin)

class ModelAnalysisAdmin(admin.ModelAdmin):
    list_display = ('name', 'report', 'analysis_start', 'analysis_end', 'accuracy', 'standard_deviation',)

admin.site.register(ModelAnalysis, ModelAnalysisAdmin)

class CachedAnalysisAdmin(admin.ModelAdmin):
    list_display = ('key', 'type', 'generated',)

admin.site.register(CachedAnalysis, CachedAnalysisAdmin)
