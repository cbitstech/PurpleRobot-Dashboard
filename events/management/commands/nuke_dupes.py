import arff
import datetime
import json
import string

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.utils.text import slugify

from events.models import Event

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        
        stacks = []
        
        for event in Event.objects.distinct('properties'):
            stacks.append(event.properties)
                
        for stack in stacks:
            while Event.objects.filter(properties=stack).count() > 1:
                Event.objects.filter(properties=stack)[0].delete()
                
                count += 1
                            
        print(str(count) + ' deleted.');

                        
                
                
                