from django.contrib.gis.db import models

REPORT_TYPES = (
    ('completion', 'Completion'),
    ('status', 'Status'),
)

class CachedMobilyzeReport(models.Model):
    objects = models.GeoManager()
    
    user_id = models.CharField(max_length=512)
    generated = models.DateTimeField(auto_now_add=True)
    report_type = models.CharField(max_length=512, choices=REPORT_TYPES, default='status')
    
    report = models.TextField(max_length=1048576)
