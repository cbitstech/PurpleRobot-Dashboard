import datetime
import hashlib
import json
import numbers
import numpy
import pytz
from pytz import timezone
import scipy
import scipy.stats
import StringIO
import time
import urllib2
import xlwt

from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.context_processors import *
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import *
from django.template import *
from django.template.loader import *
from django.utils import simplejson
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from brain.models import CachedAnalysis, ReportJob
from data_sources.models import DataSource, DataReport
from participants.models import *
from pr_integration.util import database_exists, fetch_data, table_exists

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
                last_session_date = datetime.datetime.max

                min_delta = datetime.timedelta(0, 60)
                session_delta = datetime.timedelta(0, 1800)
                
                session_count = 0

                values = fetch_data(hash, 'mobilyze_eav', 'insertedTime', start, now)

                for value in values:
                    if value[1] != None:
                        if (last_session_date - value[0]) > session_delta:
                            session_count += 1
                            last_session_date = value[0]

                values = fetch_data(hash, 'mobilyze_eav', 'FEATURE_VALUE_DT_name', start, now)
                
                last_value = ''

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
    c['show_add'] = True

    return render_to_response('mobilyze_status.html', c)

@login_required
def mobilyze_quality(request):
    users = []
    
    for study in Study.objects.filter(slug='mobilyze-2013'):
        for id in study.participant_ids(request.user):
            user = fetch_responses(id)
            
            if 'mean_std_dev' in user:
                users.append(user)
    
    c = RequestContext(request)
    
    c['users'] = sorted(users, key=lambda user: user['mean_std_dev'], reverse=True)
    c['group_stats'] = fetch_group_stats(users)
    c['questions'] = MOBILYZE_QUESTIONS
    c['categorical'] = CATEGORICAL_QUESTIONS
    
    c['request'] = request

    return render_to_response('mobilyze_quality.html', c)

def verify_id(request, id):
    return HttpResponse(json.dumps(fetch_status(id), indent=2), content_type="application/json")

def retire_id(request, id=None):
    for study in Study.objects.filter(slug='mobilyze-2013'):
        for participant in study.participants.filter(participant_id=id):
            participant.active = False
            participant.save()

    return redirect(reverse('mobilyze_status'))

def activate_id(request, id=None):
    for study in Study.objects.filter(slug='mobilyze-2013'):
        for participant in study.participants.filter(participant_id=id):
            participant.active = True
            participant.save()

    return redirect(reverse('mobilyze_status'))

def add_id(request):
    if request.method == 'POST':
        if 'new_id' in request.POST:
            new_id = request.POST['new_id'].strip()
            
            for study in Study.objects.filter(slug='mobilyze-2013'):
                for participant in study.participants.filter(participant_id=new_id):
                    return redirect(reverse('mobilyze_status'))
            
            participant = StudyParticipant(participant_id=new_id, study=study, active=True)
            participant.save()

    return redirect(reverse('mobilyze_status'))

@login_required
def mobilyze_num_stats(request, user_id='group', question=''):
    to_ignore = [ 'RobotHealthProbe', 'CallHistoryFeature.WINDOWS', ]
    fields_ignore = [ 'batteryprobe_icon_sub_small', ]
    force_nominal = [ 'batteryprobe_status', 'batteryprobe_plugged', 'telephonyprobe_psc', 'networkprobe_ip_address' ]

    key = 'correlation_' + user_id + '_' + question
    
    matches = CachedAnalysis.objects.filter(key=key).order_by('-generated')

    if matches.count() > 0:
        pass
    else:
        table_name = 'undefined'

        m = hashlib.md5()
        m.update(user_id)
    
        hash = m.hexdigest()
        
        past = datetime.datetime(datetime.MINYEAR, 1, 1)
        future = datetime.datetime(datetime.MAXYEAR, 12, 31)
        
        examples = []

        for ds in DataSource.objects.filter(name__contains=hash):
            table_names = ds.table_names()

            table_columns = {}
                
            for name in table_names:
                if (name in to_ignore) == False:
                    table_columns[name] = ds.table_columns(name)

            points = ds.fetch_data(table_name, question, past, future)

            categorical_values = {}
            row_keys = []
            
            for point in points:
                example = {}
                example['label'] = float(point[1])
                example['recorded'] = point[0]

                row_dict = {}
                    
                for table, columns in table_columns.iteritems():
                    fetched = ds.fetch_nearest(point[0], table, columns)
                        
                    if len(fetched) > 0:
                        for i in range(0, len(columns)):
                            column = columns[i]
                                
                            column_key = slugify(table + '_' + column[0])
                                
                            if row_keys.count(column_key) == 0:
                                row_keys.append(column_key)
                                
                            if column[1] == 'text' or column[1] == 'boolean':
                                column_values = set([None])
    
                                try:
                                    column_values = categorical_values[column_key]
                                except KeyError:
                                    categorical_values[column_key] = column_values
                                    
                                str_value = slugify(unicode(str(fetched[i])))
                                    
                                if str_value.strip() == '':
                                    str_value = 'empty_string'
                                    
                                column_values.add(str_value)
                                    
                            if fetched[i] == True:
                                row_dict[column_key] = '1'
                            elif fetched[i] == False:
                                row_dict[column_key] = '0'
                            elif column[1] == 'text':
                                str_value = slugify(unicode(fetched[i]))
                                    
                                if str_value.strip() == '':
                                    str_value = 'empty_string'
                                    
                                row_dict[column_key] = str_value
                            else:
                                row_dict[column_key] = fetched[i]

                for remove in fields_ignore:
                    if remove in row_dict:
                        del(row_dict[remove])
                    
                example['values'] = row_dict

                examples.append(example)
            
            feature_values = {}
                
            for example in examples:
                for key, value in example['values'].items():
                    values = []
                    
                    try:
                        values = feature_values[key]
                    except KeyError:
                        feature_values[key] = values
                        
                    if value in values:
                        pass
                    else:
                        values.append(value)
                        
            for key, value in feature_values.items():
                if len(value) < 2:
                    for example in examples:
                        if key in example['values']:
                            del(example['values'][key])
                else:
                    is_num = True
                    
                    for nominal in force_nominal:
                        if key.endswith(nominal):
                            is_num = False
                    
                    for v in value:
                        if isinstance(v, numbers.Number) == False:
                            try:
                                float(v)
                            except:
                                is_num = False
                            
                    if is_num == False:
                        for v in value:
                            k = key + '_' + str(v)
                            
                            for example in examples:
                                example['values'][k] = 0
                                 
                                if key in example['values']:
                                    if str(example['values'][key]) == str(v):
                                        example['values'][k] = 1
                                        
                        for example in examples:
                            if key in example['values']:
                                del(example['values'][key])
                    else:
                        for example in examples:
                            example['values'][key] = float(example['values'][key])

#            print(json.dumps(example, indent=2, cls=DjangoJSONEncoder))
                            
            output = examples

            feature_labels = []

            if len(examples) > 0:
                feature_names = list(examples[0]['values'].keys())
                feature_names.sort()
                
                labels = []
                rows = []
                
                for example in examples:
                    row = []

                    row.append(example['label'])
                    
                    for name in feature_names:
                        row.append(example['values'][name])
                        
                    rows.append(row)

                feature_names.insert(0, 'label')
                
                rows = numpy.array(rows)
 
                x = rows[:,0]
                    
                output = { }
                
                for i in range(0, len(feature_names)):
                    feature = feature_names[i]
                    
                    y = rows[:,i]
                    
                    y_val = y[0]
                    
                    y_same = True
                    
                    for value in y:
                        if y_same and value != y_val:
                            y_same = False

                    if y_same == False:
                        output[feature] = {}

                        output[feature]['correlation'] = numpy.corrcoef(x, y).tolist()[0][1]
                        output[feature]['covariance'] = numpy.cov(x, y).tolist()[0][1]

                        pearson = scipy.stats.pearsonr(x, y)
                        output[feature]['pearson_r'] = pearson[0]
                        output[feature]['pearson_pvalue'] = pearson[1]

                        spearman = scipy.stats.spearmanr(x, y)
                        output[feature]['spearman_r'] = spearman[0]
                        output[feature]['spearman_pvalue'] = spearman[1]
                        
                        if feature.startswith('undefined_feature_value_dt') == False:
                            feature_labels.append(feature)

#            return HttpResponse(json.dumps(output, indent=2, cls=DjangoJSONEncoder), content_type="text/plain")

            c = RequestContext(request)
            c['request'] = request
            c['user_id'] = user_id
            c['label'] = question
            c['analysis'] = output
            c['feature_names'] = feature_labels

    return render_to_response('mobilyze_numeric.html', c)

@login_required
def mobilyze_demographic(request):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Responses')
    
    sheet.write(0, 0, 'Response ID')
    sheet.write(0, 1, 'Participant ID')
    sheet.write(0, 2, 'Response Key')
    sheet.write(0, 3, 'Response Date')
    sheet.write(0, 4, 'Response Value')
    
    table = 'undefined'
    now = datetime.datetime.utcnow()
    start = datetime.datetime.utcfromtimestamp(0)
    
    row_counter = 1

    for study in Study.objects.filter(slug='mobilyze-2013'):
        for id in study.participant_ids(request.user):
            m = hashlib.md5()
            m.update(id)
    
            hash = m.hexdigest()
            
            if database_exists(hash):
                if table_exists(hash, table):
                    for column in CATEGORICAL_QUESTIONS:
                        values = fetch_data(hash, table, column, start, now, filter=True)
                
                        for value in values:
                            sheet.write(row_counter, 0, row_counter)
                            sheet.write(row_counter, 1, id)
                            sheet.write(row_counter, 2, column.replace('FEATURE_VALUE_DT_', ''))
                            sheet.write(row_counter, 3, value[0].isoformat(' '))
                            sheet.write(row_counter, 4, value[1])
                    
                            row_counter += 1
                else:
                    values = fetch_data(hash, 'mobilyze_eav', 'FEATURE_VALUE_DT_name,FEATURE_VALUE_DT_value', start, now, filter=False)
                
                    last_name = None
                
                    for value in values:
                        name = 'FEATURE_VALUE_DT_' + value[1]
                        
                        if name in CATEGORICAL_QUESTIONS and last_name != name:
                            last_name = name
                            sheet.write(row_counter, 0, row_counter)
                            sheet.write(row_counter, 1, id)
                            sheet.write(row_counter, 2, value[1])
                            sheet.write(row_counter, 3, value[0].isoformat(' '))
                            sheet.write(row_counter, 4, value[2])
                    
                            row_counter += 1
                    
    io_str = StringIO.StringIO()
    workbook.save(io_str)

    response = HttpResponse(io_str.getvalue(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="Mobilyze_Demographic_' + datetime.date.today().strftime('%Y%m%d') + '"'
    
    io_str.close()
    
    return response

@login_required
def mobilyze_numeric(request):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Responses')
    
    sheet.write(0, 0, 'Response ID')
    sheet.write(0, 1, 'Participant ID')
    sheet.write(0, 2, 'Response Key')
    sheet.write(0, 3, 'Response Date')
    sheet.write(0, 4, 'Response Value')
    
    table = 'undefined'
    now = datetime.datetime.utcnow()
    start = datetime.datetime.utcfromtimestamp(0)
    
    row_counter = 1

    for study in Study.objects.filter(slug='mobilyze-2013'):
        for id in study.participant_ids(request.user):
            m = hashlib.md5()
            m.update(id)
    
            hash = m.hexdigest()
            
            if database_exists(hash):
                if table_exists(hash, table):
                    for column in MOBILYZE_QUESTIONS:
                        if column in CATEGORICAL_QUESTIONS:
                            pass
                        else:
                            values = fetch_data(hash, table, column, start, now, filter=True)
                
                            for value in values:
                                sheet.write(row_counter, 0, row_counter)
                                sheet.write(row_counter, 1, id)
                                sheet.write(row_counter, 2, column.replace('FEATURE_VALUE_DT_', ''))
                                sheet.write(row_counter, 3, value[0].isoformat(' '))
                                sheet.write(row_counter, 4, value[1])
                    
                                row_counter += 1
                else:
                    values = fetch_data(hash, 'mobilyze_eav', 'FEATURE_VALUE_DT_name,FEATURE_VALUE_DT_value', start, now, filter=False)
                
                    last_name = None
                
                    for value in values:
                        name = 'FEATURE_VALUE_DT_' + value[1]
                        
                        if name in MOBILYZE_QUESTIONS and (name in CATEGORICAL_QUESTIONS) == False and last_name != name:
                            last_name = name
                            sheet.write(row_counter, 0, row_counter)
                            sheet.write(row_counter, 1, id)
                            sheet.write(row_counter, 2, value[1])
                            sheet.write(row_counter, 3, value[0].isoformat(' '))
                            sheet.write(row_counter, 4, value[2])
                    
                            row_counter += 1
                    
    io_str = StringIO.StringIO()
    workbook.save(io_str)

    response = HttpResponse(io_str.getvalue(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="Mobilyze_Numeric_' + datetime.date.today().strftime('%Y%m%d') + '"'
    
    io_str.close()
    
    return response


@login_required
def mobilyze_nom_stats(request, user_id='group', question=''):
    c = RequestContext(request)
    c['request'] = request
    c['user_id'] = user_id
    c['label'] = question
    
    app_key = user_id + '_' + question
    
    for job in ReportJob.objects.filter(app_key=app_key):
        try:
            c['stats'] = json.loads(job.stats_file.read())
        except:
            pass

    return render_to_response('mobilyze_nominal.html', c)
