import arff
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
    'FEATURE_VALUE_DT_LocationR1',
    'FEATURE_VALUE_DT_PeopleInEnvironmentR1',
    'FEATURE_VALUE_DT_PeopleNearbyR1',
    'FEATURE_VALUE_DT_ConversationTypeR1',
]

CATEGORICAL_QUESTIONS = [
    'FEATURE_VALUE_DT_ConversationTypeR1',
    'FEATURE_VALUE_DT_LocationR1',
    'FEATURE_VALUE_DT_PeopleInEnvironmentR1',
    'FEATURE_VALUE_DT_PeopleNearbyR1',
]


def fetch_responses(id):
    m = hashlib.md5()
    m.update(id)
    
    hash = m.hexdigest()

    report = { 'status': 'OK', 'errors': [], 'id': id,  'hash': hash, 'questions': MOBILYZE_QUESTIONS, 'categorical': CATEGORICAL_QUESTIONS }
    
    if database_exists(hash) == False:
        report['status'] = 'Error'
        report['errors'].append('No such database ' + hash + ' for ID ' + id + '.')
    else:
        stats = {}
        group_stats = {}
        
        now = datetime.datetime.utcnow()
        start = datetime.datetime.utcfromtimestamp(0)
        
        response_table = 'undefined'
        
        total_count = 0
        
        std_devs = []

        if table_exists(hash, response_table) == False:
            report['status'] = 'Error'
            report['errors'].append('No such table ' + response_table + ' for ID ' + id + '.')
        else:
            for response_field in MOBILYZE_QUESTIONS:
                try:
                    stats[response_field]
                except KeyError:
                    stats[response_field] = {}
                    
                values = fetch_data(hash, response_table, response_field, start, now, filter=True)

                stats[response_field]['count'] = 0
                
                num_values = []

                for value in values:
                    if value[1] != None and str(value[1]).strip() != '':
                        if response_field in CATEGORICAL_QUESTIONS:
                            pass
                        else:
                            num_values.append(float(value[1]))

                        stats[response_field]['count'] += 1
                        
                if len(num_values) > 0:
                    stats[response_field]['min'] = numpy.amin(num_values)
                    stats[response_field]['max'] = numpy.amax(num_values)
                    stats[response_field]['mean'] = numpy.mean(num_values)
                    stats[response_field]['stddev'] = numpy.std(num_values)
                    
                    std_devs.append(stats[response_field]['stddev'])
        
        report['statistics'] = stats
        report['mean_std_dev'] = numpy.mean(std_devs)
        
    return report

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        
        admin_user = DashboardUser.objects.get(username=args[0])

        mobilyze = Study.objects.get(slug='mobilyze-2013')

        for study in Study.objects.filter(slug='mobilyze-2013'):
            for id in study.participant_ids(admin_user):
                print('Generating ' + id + ' responses report...')
                reports = CachedMobilyzeReport.objects.filter(user_id=id, report_type='responses').order_by('-pk')
            
                last_report = None
                report_type = 'responses'
                json_string = None
            
                if reports.count() > 0:
                    last_report = reports[0]
                    report_type = last_report.report_type
                
                update = False

                status = fetch_responses(id)
                json_string = json.dumps(status, indent=2, cls=DjangoJSONEncoder)
                
                if last_report == None or report_type != 'responses' or last_report.report != json_string:
                    update = True
                    report_type = 'responses'

                if update:
                    print('Saving ' + id + ' responses report...')
                    report = CachedMobilyzeReport(user_id=id, report_type=report_type, report=json_string)
                    report.save()

