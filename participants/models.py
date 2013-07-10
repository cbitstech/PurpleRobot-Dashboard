from django.contrib.gis.db import models

from users.models import DashboardUser

class Study(models.Model):
    objects = models.GeoManager()
    
    name = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512, unique=True)
    
    managers = models.ManyToManyField(DashboardUser, related_name='managed_studies')
    
    def __unicode__(self):
        return self.name
        
    def participant_ids(self, user, active=None):
        participants = []
        
        for manager in self.managers.all():
            if manager.pk == user.pk:
                if active == None:
                    for p in self.participants.all().order_by('participant_id'):
                        participants.append(p.participant_id)
                else:
                    for p in self.participants.filter(active=active).order_by('participant_id'):
                        participants.append(p.participant_id)
        
        return participants


class StudyParticipant(models.Model):
    objects = models.GeoManager()
    
    participant_id = models.CharField(max_length=512)
    active = models.BooleanField(default=True)
    
    study = models.ForeignKey(Study, related_name='participants')

    def __unicode__(self):
        return self.participant_id
