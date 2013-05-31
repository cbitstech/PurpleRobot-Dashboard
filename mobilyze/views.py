import datetime
import hashlib
import json
import pytz
from pytz import timezone
import time
import urllib2

from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.context_processors import *
from django.http import HttpResponse
from django.shortcuts import *
from django.template import *
from django.template.loader import *
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from participants.models import *
from pr_integration.util import database_exists, fetch_data, table_exists

MOBILYZE_QUESTIONS = [
    'FEATURE_VALUE_DT_AnnoyanceR1', 
    'FEATURE_VALUE_DT_InterestR1',
    'FEATURE_VALUE_DT_IrritabilityR1',
    'FEATURE_VALUE_DT_LocationR1',
    'FEATURE_VALUE_DT_PeopleInEnvironmentR1',
    'FEATURE_VALUE_DT_PeopleNearbyR1',
    'FEATURE_VALUE_DT_PhysicalEffortR1',
    'FEATURE_VALUE_DT_UninterestR1',
    'FEATURE_VALUE_DT_DepressionR1',
    'FEATURE_VALUE_DT_DiscouragementR1',
    'FEATURE_VALUE_DT_NervousnessR1',
    'FEATURE_VALUE_DT_RelaxednessR1',
    'FEATURE_VALUE_DT_SadnessR1',
    'FEATURE_VALUE_DT_ConversationTypeR1',
    'FEATURE_VALUE_DT_AccomplishmentR1',
    'FEATURE_VALUE_DT_ConfidenceR1',
    'FEATURE_VALUE_DT_UncertaintyR1',
    'FEATURE_VALUE_DT_BelongingR1',
    'FEATURE_VALUE_DT_LonelinessR1',
    'FEATURE_VALUE_DT_ContentmentR1',
    'FEATURE_VALUE_DT_HappinessR1',
    'FEATURE_VALUE_DT_ConfidenceR1',
    'FEATURE_VALUE_DT_PleasureR1',
    'FEATURE_VALUE_DT_CalmR1',
    'FEATURE_VALUE_DT_StressR1',
    'FEATURE_VALUE_DT_ClearHeadednessR1',
    'FEATURE_VALUE_DT_HopelessnessR1',
    'FEATURE_VALUE_DT_HelplessnessR1',
    'FEATURE_VALUE_DT_AnxietyR1',
    'FEATURE_VALUE_DT_BlahnessR1',
    'FEATURE_VALUE_DT_ControlR1',
    'FEATURE_VALUE_DT_GuiltR1',
    'FEATURE_VALUE_DT_EnergyR1',
    'FEATURE_VALUE_DT_SluggishnessR1',
    'FEATURE_VALUE_DT_TirednessR1'
]

def fetch_status(id):
    m = hashlib.md5()
    m.update(id)
    
    hash = m.hexdigest()

    report = { 'status': 'OK', 'errors': [], 'id': id,  'hash': hash }
    
    if database_exists(hash) == False:
        report['status'] = 'Error'
        report['errors'].append('No such database ' + hash + ' for ID ' + id + '.')
    else:
        now = datetime.datetime.utcnow()
        start = now - datetime.timedelta(0, 3600 * 6)
        
        sensor_table = 'RobotHealthProbe'
        sensor_field = 'ACTIVE_RUNTIME'
        
        if table_exists(hash, sensor_table) == False:
            report['status'] = 'Error'
            report['errors'].append('No such table ' + sensor_table + ' for ID ' + id + '.')
        else:
            values = fetch_data(hash, sensor_table, sensor_field, start, now)
    
            if len(values) < 1:
                report['status'] = 'Error'
                report['errors'].append('No recent data from sensor ' + sensor_table + '.' + sensor_field + '.')
                
        values = fetch_data(hash, sensor_table, sensor_field, datetime.datetime.min, now, limit=5)
        
        try:
            report['last_sensor'] = values[-1][0]
        except:
            report['last_sensor'] = None
            
        if report['last_sensor'] != None:
            report['last_sensor'] = pytz.utc.localize(report['last_sensor'])
            report['last_sensor'] = report['last_sensor'].astimezone(timezone('US/Central'))

        response_table = 'undefined'
        response_field = 'GUID'
        
        if table_exists(hash, response_table) == False:
            report['status'] = 'Error'
            report['errors'].append('No such table ' + response_table + ' for ID ' + id + '.')
        else:
            values = fetch_data(hash, response_table, response_field, start, now)
    
            if len(values) < 1:
                report['status'] = 'Error'
                report['errors'].append('No recent responses from PRO.')

        values = fetch_data(hash, response_table, response_field, datetime.datetime.min, now, limit=5)

        try:
            report['last_response'] = values[-1][0]
        except:
            report['last_response'] = None

        if report['last_response'] != None:
            report['last_response'] = pytz.utc.localize(report['last_response'])
            report['last_response'] = report['last_response'].astimezone(timezone('US/Central'))

    return report

def fetch_completion(id):
    m = hashlib.md5()
    m.update(id)
    
    hash = m.hexdigest()

    report = { 'status': 'OK', 'errors': [], 'id': id,  'hash': hash }
    
    if database_exists(hash) == False:
        report['status'] = 'Error'
        report['errors'].append('No such database ' + hash + ' for ID ' + id + '.')
    else:
        now = datetime.datetime.utcnow()
        start = datetime.datetime.utcfromtimestamp(0)
        
        response_table = 'undefined'
        
        responses = {}
        
        total_count = 0

        if table_exists(hash, response_table) == False:
            report['status'] = 'Error'
            report['errors'].append('No such table ' + response_table + ' for ID ' + id + '.')
        else:
            for response_field in MOBILYZE_QUESTIONS:
                values = fetch_data(hash, response_table, response_field, start, now)
                
                response_count = 0
                
                for value in values:
                    if value[1] != None:
                        response_count += 1
                
                total_count += response_count
                        
                responses[response_field] = response_count

                values = fetch_data(hash, response_table, 'insertedTime', start, now, distinct=True)
                responses['DISTINCT_TIMES'] = len(values)


        responses['TOTAL'] = total_count
        
        report['responses'] = responses
        
    return report
    
@login_required
def mobilyze_status(request):
    active_rows = []
    complete_rows = []
    
    for study in Study.objects.filter(slug='mobilyze-2013'):
        for id in study.participant_ids(request.user, active=True):
            active_rows.append(fetch_status(id))

        for id in study.participant_ids(request.user, active=False):
            complete_rows.append(fetch_completion(id))
    
    c = RequestContext(request)
    
    c['active_rows'] = active_rows
    c['complete_rows'] = complete_rows
    c['request'] = request

    return render_to_response('mobilyze_status.html', c)

def verify_id(request, id):
    return HttpResponse(json.dumps(fetch_status(id), indent=2), content_type="application/json")
