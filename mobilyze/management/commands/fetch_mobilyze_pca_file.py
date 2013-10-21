import arff
import csv
import datetime
import hashlib
import json
import numpy
import pytz
from pytz import timezone
import uuid
import tempfile
import urllib
import urllib2
import subprocess

from xml.dom.minidom import *

from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils.text import slugify


from users.models import DashboardUser
from data_sources.models import DataSource, DataReport
from participants.models import *
from pr_integration.util import database_exists, fetch_data, table_exists

from mobilyze.models import *

MOBILYZE_QUESTIONS = [
    'FEATURE_VALUE_DT_CalmR1',
    'FEATURE_VALUE_DT_StressR1',
    'FEATURE_VALUE_DT_AnxietyR1',
    'FEATURE_VALUE_DT_RelaxednessR1',
    'FEATURE_VALUE_DT_TenseTODOR1',
    'FEATURE_VALUE_DT_NervousnessR1',
    'FEATURE_VALUE_DT_IrritabilityR1',
    'FEATURE_VALUE_DT_AnnoyanceR1', 
    'FEATURE_VALUE_DT_HappinessR1',
    'FEATURE_VALUE_DT_ContentmentR1',
    'FEATURE_VALUE_DT_PleasureR1',
    'FEATURE_VALUE_DT_SadnessR1',
    'FEATURE_VALUE_DT_DepressionR1',
    'FEATURE_VALUE_DT_DiscouragementR1',
    'FEATURE_VALUE_DT_HopelessnessR1',
    'FEATURE_VALUE_DT_HelplessnessR1',
    'FEATURE_VALUE_DT_InterestR1',
    'FEATURE_VALUE_DT_UninterestR1',
    'FEATURE_VALUE_DT_EnergyR1',
    'FEATURE_VALUE_DT_SluggishnessR1',
    'FEATURE_VALUE_DT_TirednessR1',
    'FEATURE_VALUE_DT_AccomplishmentR1',
    'FEATURE_VALUE_DT_UncertaintyR1',
    'FEATURE_VALUE_DT_ConfidenceR1',
    'FEATURE_VALUE_DT_ClearHeadednessR1',
    'FEATURE_VALUE_DT_BelongingR1',
    'FEATURE_VALUE_DT_LonelinessR1',
    'FEATURE_VALUE_DT_GuiltR1',
    'FEATURE_VALUE_DT_ControlR1',
    'FEATURE_VALUE_DT_BlahnessR1',
    'FEATURE_VALUE_DT_PhysicalEffortR1',
]

def key_for_user(user_id, value_date):
#    return user_id + '_' + value_date.strftime('%m_%d')
    return user_id + '_' + value_date.strftime('%U')


def fetch_responses(id):
    m = hashlib.md5()
    m.update(id)
    
    hash = m.hexdigest()

    report = { 'status': 'OK', 'errors': [], 'id': id,  'hash': hash, 'questions': MOBILYZE_QUESTIONS,  }
    
    if database_exists(hash) == False:
        report['status'] = 'Error'
        report['errors'].append('No such database ' + hash + ' for ID ' + id + '.')
    else:
        now = datetime.datetime.utcnow()
        start = datetime.datetime.utcfromtimestamp(0)
        
        response_table = 'undefined'
        
        total_count = 0
        
        std_devs = []
        
        id_responses = {}
#        responses = {}

        if table_exists(hash, response_table) == False:
            report['status'] = 'Error'
            report['errors'].append('No such table ' + response_table + ' for ID ' + id + '.')
        else:
            for response_field in MOBILYZE_QUESTIONS:
                values = fetch_data(hash, response_table, response_field, start, now, filter=True)
                
                for value in values:
                    if value[1] != None and str(value[1]).strip() != '':
                        key = key_for_user(id, value[0])
                        
                        value_dict = {}
                        
                        if key in id_responses:
                            value_dict = id_responses[key]
                        else:
                            id_responses[key] = value_dict
                            
                        num_values = []
                        
                        if response_field in value_dict:
                            num_values = value_dict[response_field]
                        else:
                            value_dict[response_field] = num_values
                        
                        num_values.append(float(value[1]))
                        
            for key, value_dict in id_responses.iteritems():
                for response_field,num_values in value_dict.iteritems():
                    value_dict[response_field] = numpy.mean(num_values)
                    
        return id_responses
        
    return {}

class Command(BaseCommand):
    def handle(self, *args, **options):
        admin_user = DashboardUser.objects.get(username=args[0])

        mobilyze = Study.objects.get(slug='mobilyze-2013')
        
        group = {}

        for study in Study.objects.filter(slug='mobilyze-2013'):
            for id in study.participant_ids(admin_user):
                responses = fetch_responses(id)
                
                for k,v in responses.iteritems():
                    group[k] = v
                
#                if len(responses) > 0:
#                    group[id] = responses
                    
        output = ''
        
        for question in MOBILYZE_QUESTIONS:
            output += '\t' + question
            
        output += '\n'

        for user,values in group.iteritems():
            output += user
          
            for question in MOBILYZE_QUESTIONS:
                value = '?'

                
                if question in values:
                    value = str(values[question])

                output += '\t' + value
                
            output += '\n'
                
#        print(json.dumps(group, indent=2, cls=DjangoJSONEncoder))
        print(output)


