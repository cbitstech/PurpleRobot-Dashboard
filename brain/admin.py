from django.contrib import admin

from brain.models import *

class ReportJobAdmin(admin.ModelAdmin):
    search_fields = ['app_key', 'name']
    list_display = ('name', 'app_key', 'job_start', 'job_end', 'result_type',)

    actions = ['reset_dates']

    def reset_dates(self, request, queryset):
        count = 0
        for job in queryset:
            job.job_start = None
            job.job_end = None
            job.save()
            
            count += 1

        if count == 1:
            message_bit = "1 job was"
        else:
            message_bit = "%s jobs were" % count
            
        self.message_user(request, "%s successfully updated." % message_bit)


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


class GeneratedModelAdmin(admin.ModelAdmin):
    list_display = ('name','type', 'generated',)

admin.site.register(GeneratedModel, GeneratedModelAdmin)
