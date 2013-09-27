import arff
import datetime
import hashlib
import json
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

def fetch_group_stats(users):
    stats = {}

    for response_field in MOBILYZE_QUESTIONS:
        if response_field in CATEGORICAL_QUESTIONS:
            pass
        else:
            stats[response_field] = {}
            
            min_values = []
            max_values = []
            mean_values = []
            stddev_values = []
            
            for user in users:
                if response_field in user['statistics'] and user['statistics'][response_field]['count'] > 0:
                    min_values.append(user['statistics'][response_field]['min'])
                    max_values.append(user['statistics'][response_field]['max'])
                    mean_values.append(user['statistics'][response_field]['mean'])
                    stddev_values.append(user['statistics'][response_field]['stddev'])
                    
            if len(min_values) > 0:
                stats[response_field]['min'] = numpy.mean(min_values)
                stats[response_field]['max'] = numpy.mean(max_values)
                stats[response_field]['mean'] = numpy.mean(mean_values)
                stats[response_field]['stddev'] = numpy.mean(stddev_values)
            
    return stats

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
            if table_exists(hash, 'mobilyze_eav') == False:
                report['status'] = 'Error'
                report['errors'].append('No such table ' + 'mobilyze_eav' + ' for ID ' + id + '.')
            else:
                values = fetch_data(hash, 'mobilyze_eav', response_field, start, now)
        
                if len(values) < 1:
                    report['status'] = 'Error'
                    report['errors'].append('No recent responses from PRO.')

        else:
            values = fetch_data(hash, response_table, response_field, start, now)
    
            if len(values) < 1:
                report['status'] = 'Error'
                report['errors'].append('No recent responses from PRO.')

        values = fetch_data(hash, response_table, response_field, datetime.datetime.min, now, limit=5)

        try:
            report['last_response'] = values[-1][0]
        except:
            values = fetch_data(hash, 'mobilyze_eav', response_field, datetime.datetime.min, now, limit=5)
    
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
            if table_exists(hash, 'mobilyze_eav') == False:
                report['status'] = 'Error'
                report['errors'].append('No such table ' + 'mobilyze_eav' + ' for ID ' + id + '.')
            else:
                last_session_date = datetime.datetime.min

                session_delta = datetime.timedelta(seconds=600)
                
                session_count = 0

                values = fetch_data(hash, 'mobilyze_eav', 'FEATURE_VALUE_DT_name', start, now)

                for value in values:
                    if value[1] != None:
                        if (value[0] - last_session_date) > session_delta:
                            session_count += 1
                            last_session_date = value[0]

#                values = fetch_data(hash, 'mobilyze_eav', 'FEATURE_VALUE_DT_name', start, now)
                
                last_value = ''
                last_name = ''

                values = fetch_data(hash, 'mobilyze_eav', 'FEATURE_VALUE_DT_name', start, now)

                for value in values:
                    if value[1] != None and value[1] != last_value and value[1] != '':
                        last_value = value[1]
                        
                        total_count += 1
                
                responses['DISTINCT_TIMES'] = session_count
        else:
            for response_field in MOBILYZE_QUESTIONS:
                values = fetch_data(hash, response_table, response_field, start, now)
                
                response_count = 0
                
                for value in values:
                    if value[1] != None:
                        response_count += 1
                
                total_count += response_count
                        
                responses[response_field] = response_count

                values = fetch_data(hash, response_table, 'eventDateTime', start, now, distinct=True)
                
                values.sort(key=lambda x: x[1])
                values.reverse()
                
                session_delta = datetime.timedelta(seconds=600)
                session_count = 0
                
                last_submit = datetime.datetime.max
                
                for value in values:
                    if (last_submit - value[1]) > session_delta:
                        session_count += 1
                        
                    last_submit = value[1]

                responses['DISTINCT_TIMES'] = session_count


        responses['TOTAL'] = total_count
        
        report['responses'] = responses
        
    return report

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        
        admin_user = DashboardUser.objects.get(username=args[0])

        mobilyze = Study.objects.get(slug='mobilyze-2013')

        for study in Study.objects.filter(slug='mobilyze-2013'):
            for id in study.participant_ids(admin_user, active=True):
                print('Generating ' + id + ' status report...')
                reports = CachedMobilyzeReport.objects.filter(user_id=id, report_type='status').order_by('-pk')
            
                last_report = None
                report_type = 'unknown'
                json_string = None
            
                if reports.count() > 0:
                    last_report = reports[0]
                    report_type = last_report.report_type
                
                update = False

                status = fetch_status(id)
                json_string = json.dumps(status, indent=2, cls=DjangoJSONEncoder)
                
                if last_report == None or report_type != 'status' or last_report.report != json_string:
                    update = True
                    report_type = 'status'

                if update:
                    print('Saving ' + id + ' status report...')
                    report = CachedMobilyzeReport(user_id=id, report_type=report_type, report=json_string)
                    report.save()

            for id in study.participant_ids(admin_user, active=False):
                print('Generating ' + id + ' completion report...')
                reports = CachedMobilyzeReport.objects.filter(user_id=id, report_type='completion').order_by('-pk')
            
                last_report = None
                report_type = 'unknown'
                json_string = None
            
                if reports.count() > 0:
                    last_report = reports[0]
                    report_type = last_report.report_type
                
                update = False

                completion = fetch_completion(id)

                json_string = json.dumps(completion, indent=2, cls=DjangoJSONEncoder)
                
                if last_report == None or report_type != 'completion' or last_report.report != json_string:
                    update = True
                    report_type = 'completion'
            
                if update:
                    print('Saving ' + id + ' completion report...')
                    report = CachedMobilyzeReport(user_id=id, report_type=report_type, report=json_string)
                    report.save()

