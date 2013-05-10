import arff
import datetime
import json
import string

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from events.models import Event

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        
        for event in Event.objects.filter(event_type='java_exception'): #, error_type=None):
            json_obj = json.loads(event.properties)
            
            if 'stacktrace' in json_obj:
                stacktrace = json_obj['stacktrace']
                
                for line in string.split(stacktrace, '\n\t'):
                    line = string.strip(line)
                    
                    if line.find('edu.northwestern.cbits.purple_robot_manager') != -1:
                        tokens = line.split(' ')

                        if event.error_location != 'foobar': # None:
                            start = tokens[1].find('(')
                            event.error_location = tokens[1][(start+1):-1]
                    
                        line_tokens = string.split(stacktrace, ':')
                        event.error_type = line_tokens[0].split('\n\t')[0]
                        
                        event.save()
                            
                        count += 1
                            
        print(str(count) + ' updated.');

                        
                
                