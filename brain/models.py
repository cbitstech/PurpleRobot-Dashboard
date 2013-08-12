from django.contrib.gis.db import models

from data_sources.models import DataSource, DataReport

class ReportJob(models.Model):
    objects = models.GeoManager()
    
    name = models.CharField(max_length=128)
    app_key = models.CharField(max_length=256, null=True, blank=True)

    parameters = models.TextField(max_length=1048576);
    job_start = models.DateTimeField(null=True, blank=True)
    job_end = models.DateTimeField(null=True, blank=True)
    
    result_file = models.FileField(upload_to='brain/jobs', null=True, blank=True)
    result_type = models.CharField(max_length=128, default='application/octet-stream')

    stats_file = models.FileField(upload_to='brain/stats', null=True, blank=True)
    stats_type = models.CharField(max_length=128, default='application/json')
    
    def __unicode__(self):
        return self.name
    
    def relation_prefix(self):
        return 'foobar'

class PerformanceMeasurementEndpoint(models.Model):
    objects = models.GeoManager()

    name = models.CharField(max_length=1024)
    endpoint = models.URLField(max_length=256, unique=True)

    def __unicode__(self):
        return self.name

class ModelGeneratorEndpoint(models.Model):
    objects = models.GeoManager()

    name = models.CharField(max_length=1024)
    endpoint = models.URLField(max_length=256, unique=True)
    expect_type = models.CharField(max_length=128, default='application/octet-stream')

    parameters = models.TextField(max_length=1048576)
    
    performance_endpoint = models.ForeignKey(PerformanceMeasurementEndpoint, related_name='model_endpoints', null=True, blank=True)

    def __unicode__(self):
        return self.name
    
class ModelAnalysis(models.Model):
    objects = models.GeoManager()

    name = models.CharField(max_length=1024)
    report = models.ForeignKey(ReportJob, related_name='analyses')
    endpoint = models.ForeignKey(ModelGeneratorEndpoint, related_name='analyses', null=True, blank=True)

    analysis_start = models.DateTimeField(null=True, blank=True)
    analysis_end = models.DateTimeField(null=True, blank=True)
    
    parameters = models.TextField(max_length=1048576)

    generated_model = models.TextField(max_length=1048576, blank=True, null=True)
    model_performance = models.TextField(max_length=1048576, blank=True, null=True)
    
    accuracy = models.FloatField(default=0.0)
    standard_deviation = models.FloatField(default=0.0)

    def __unicode__(self):
        return self.name

# url, role, prefix

class CachedAnalysis(models.Model):
    objects = models.GeoManager()

    key = models.CharField(max_length=1024)
    type = models.CharField(max_length=1024)
    generated = models.DateTimeField(auto_now_add=True)
    
    analysis = models.TextField(max_length=1048576)


class GeneratedModel(models.Model):
    objects = models.GeoManager()
    
    name = models.CharField(max_length=1024)
    type = models.CharField(max_length=1024)
    description = models.TextField(max_length=1048576)
    generated = models.DateTimeField(auto_now_add=True)

    model_file = models.FileField(upload_to='models')
    