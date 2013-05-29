from django.contrib.gis.db import models

from data_sources.models import DataSource, DataReport

class ReportJob(models.Model):
    objects = models.GeoManager()
    
    name = models.CharField(max_length=128)

    parameters = models.TextField(max_length=1048576);
    job_start = models.DateTimeField(null=True, blank=True)
    job_end = models.DateTimeField(null=True, blank=True)
    
    result_file = models.FileField(upload_to='brain/jobs', null=True, blank=True)
    result_type = models.CharField(max_length=128, default='application/octet-stream')
    
    def __unicode__(self):
        return self.name
