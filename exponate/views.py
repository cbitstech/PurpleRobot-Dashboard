import hashlib
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from participants.models import *
from pr_integration.util import database_exists, fetch_data, table_exists

def exponate_response(request):
    output = {}
    
    for study in Study.objects.filter(slug='exponate-2013'):
        for id in study.participant_ids(request.user, active=True):
            m = hashlib.md5()
            m.update(id)
            hash = m.hexdigest()

            output[id] = {}
            
            if database_exists(hash):
                output[id]['hash'] = hash
                
                if table_exists(hash, 'EXPONATE'):
                    rows = fetch_data(hash, 'EXPONATE', 'FEATURE_VALUE_DT_name,FEATURE_VALUE_DT_user,FEATURE_VALUE_DT_value')                    
                    output[id]['rows'] = rows
                else:
                    output[id]['error'] = 'No such table "EXPONATE".'
            else:
                output[id]['error'] = 'No such database.'

    return HttpResponse(json.dumps(output, indent=2, cls=DjangoJSONEncoder), content_type="text/plain")


# def fetch_data(database, table_name, column_names, start=datetime.datetime.min, end=datetime.datetime.max, distinct=False, limit=0, filter=False):
