from django.contrib.gis.db import models

class Event(models.Model):
    objects = models.GeoManager()
    
    user_id = models.CharField(max_length=512, db_index=True)
    
    event_type = models.CharField(max_length=256, db_index=True)
    logged = models.DateTimeField(db_index=True)
    recorded = models.DateTimeField(auto_now_add=True, db_index=True)
    
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    altitude = models.FloatField(blank=True, null=True)
    time_drift_ms = models.BigIntegerField(blank=True, null=True)

    error_location = models.CharField(max_length=512, blank=True, null=True, db_index=True)
    error_type = models.CharField(max_length=512, blank=True, null=True, db_index=True)
    
    properties = models.TextField(max_length=1048576, blank=True, null=True)
