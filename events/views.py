from datetime import datetime
import isodate
import json
import time
import uuid

from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.context_processors import *
from django.shortcuts import *
from django.template import *
from django.template.loader import *
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from models import *

@csrf_exempt
def log_event(request):
    return_json = simplejson.dumps({'status': 'error'})
    
    if request.method == 'POST':
        try:
            event_dict = json.loads(request.POST['json'])

            event = Event(user_id=event_dict['user_id'])
            event.event_type = event_dict['event_type']
            event.logged = datetime.utcfromtimestamp(event_dict['timestamp'])
            
            if 'latitude' in event_dict and 'longitude' in event_dict:
                event.latitude = event_dict['latitude']
                event.longitude = event_dict['longitude']
                
                if 'altitude' in event_dict:
                    event.altitude = event_dict['altitude']

                if 'time_drift' in event_dict:
                    event.time_drift_ms = event_dict['time_drift']
                    
            event.properties = json.dumps(event_dict, indent=2)
            
            if Event.objects.filter(properties=event.properties).count() == 0:
                event.save()

            return_json = simplejson.dumps({'status': 'success', 'message': 'success'})
        except:
            pass

    return HttpResponse(return_json, content_type='application/json')
