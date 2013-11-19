import datetime
import hashlib
import json
import numbers
import numpy
import pytz
import math
from pytz import timezone
import scipy
import scipy.stats
from sexpy import String as S
import StringIO
import string
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

from models import *

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
    reports = CachedMobilyzeReport.objects.filter(user_id=id, report_type='responses').order_by('-pk')
    
    if reports.count() > 0:
        return json.loads(reports[0].report)

    report = { 'status': 'Error', 'errors': ['No cached copy available yet.'], 'id': id,  'hash': hash }
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
    reports = CachedMobilyzeReport.objects.filter(user_id=id, report_type='status').order_by('-pk')

    if reports.count() > 0:
        return json.loads(reports[0].report)

    report = { 'status': 'Error', 'errors': ['No cached copy available yet.'], 'id': id,  'hash': hash }
    return report

def fetch_completion(id):
    reports = CachedMobilyzeReport.objects.filter(user_id=id, report_type='completion').order_by('-pk')
    
    if reports.count() > 0:
        return json.loads(reports[0].report)

    report = { 'status': 'Error', 'errors': ['No cached copy available yet.'], 'id': id,  'hash': hash }
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

                                try:
                                    sheet.write(row_counter, 4, float(value[1]))
                                except:
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
                            
                            try:
                                sheet.write(row_counter, 4, float(value[2]))
                            except:
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

def sexp(obj):
    if isinstance(obj, S):
        return '"' + str(obj) + '"'
    elif isinstance(obj, bool):
        if obj:
            return '#t'
        
        return '#f'
    elif isinstance(obj, (list, tuple)):
        output = '('
        
        for item in list(obj):
            if len(output) > 1:
                output += ' '
                
            output += sexp(item)
            
        output += ')'
        
        return output
    elif obj != None:
        return str(obj)
    
    return '()'

@csrf_exempt
def scheme_config(request):
    values_list = []
    
    for key,value in request.REQUEST.iteritems():
        if value == 'TRUE':
            values_list.append((S(key), '.', True))
        elif value == 'FALSE':
            values_list.append((S(key), '.', False))
        else:
            values_list.append((S(key), '.', S(value)))
        
    config = ("begin", ("pr-update-config", ("quote", values_list)))
    
    return HttpResponse(sexp(config), content_type="text/plain")
            
            
@login_required
def mobilyze_data_report(request, user_id='group', question=''):
    workbook = xlwt.Workbook()
    categorical = workbook.add_sheet('Categorical')

    keys = []
    
    for job in ReportJob.objects.all():
        keys.append(job.app_key)

    matrices = {}
    labels = []

    for key in keys:
        job = ReportJob.objects.filter(app_key=key).order_by('-job_end')[0]
#
        if hasattr(job.stats_file, 'url'):
            response = urllib2.urlopen('http://dashboard.cbits.northwestern.edu' + job.stats_file.url)
            json_obj = json.loads(response.read())
        
            if json_obj['model_type'] == 'decision-tree':
                key = key.replace('FEATURE_VALUE_DT_', '').replace('R1', '')
                tokens = key.split('_')
                    
                matrix = parse_matrix(json_obj['confusion_matrix'])
                
                for k,v in matrix['counts'].iteritems():
                    label = tokens[1] + '_' + k
                    
                    if (label in labels) == False:
                        labels.append(label)
                
                matrices[job.app_key] = matrix
                matrices[job.app_key + ' (Forest)'] = matrix

    categorical.write(0, 0, 'Subject')
    categorical.write(0, 1, 'Question')
    categorical.write(0, 2, 'Number of instances')
    categorical.write(0, 3, 'Number correct')
    categorical.write(0, 4, 'Number incorrect')
    categorical.write(0, 5, 'Percent Correct')
    categorical.write(0, 6, 'Cohen\'s Kappa')
    categorical.write(0, 7, 'Shannon Entropy')
    
    labels.sort()
    
    for i in range(len(labels)):
        label = labels[i]
        
        categorical.write(0, 8 + i, label)

    forest = workbook.add_sheet('Forest')

    forest.write(0, 0, 'Subject')
    forest.write(0, 1, 'Question')
    forest.write(0, 2, 'Number of instances')
    forest.write(0, 3, 'Number correct')
    forest.write(0, 4, 'Number incorrect')
    forest.write(0, 5, 'Percent Correct')
    forest.write(0, 6, 'Cohen\'s Kappa')
    forest.write(0, 7, 'Shannon Entropy')
    
    labels.sort()
    
    for i in range(len(labels)):
        label = labels[i]
        
        forest.write(0, 8 + i, label)

    continuous = workbook.add_sheet('Continuous')

    continuous.write(0, 0, 'Subject')
    continuous.write(0, 1, 'Question')
    continuous.write(0, 2, 'Number of instances')
    continuous.write(0, 3, 'RMS Error')
    continuous.write(0, 4, 'Correlation Coef.')
    continuous.write(0, 5, 'R-Squared')
    continuous.write(0, 6, 'No. of Sensors')
    
    index = 1
    continuous_index = 1
    forest_index = 1
                
    for key in keys:
        job = ReportJob.objects.filter(app_key=key).order_by('-job_end')[0]

        if hasattr(job.stats_file, 'url'):
            response = urllib2.urlopen('http://dashboard.cbits.northwestern.edu' + job.stats_file.url)
            json_obj = json.loads(response.read())
        
            if json_obj['model_type'] == 'decision-tree':
                summary = json_obj['summary'].strip()
        
                lines = []
        
                for line in summary.split('\n'):
                    line = string.replace(line, '  ', '\t')
            
                    while string.find(line, '\t\t') != -1:
                        line = string.replace(line, '\t\t', '\t')
                
                    lines.append(line.strip())
                
                key = key.replace('FEATURE_VALUE_DT_', '').replace('R1', '')
                tokens = key.split('_')
                
                row_question = tokens[1]
        
                categorical.write(index, 0, tokens[0])
                categorical.write(index, 1, row_question)
        
                tokens = lines[0].split('\t')
                correct = int(tokens[1])
                percent_correct = float(string.replace(tokens[2], '%', '').strip())

                tokens = lines[1].split('\t')
                incorrect = int(tokens[1])

                tokens = lines[2].split('\t')
                kappa = float(tokens[1])
        
                categorical.write(index, 2, correct + incorrect)
                categorical.write(index, 3, correct)
                categorical.write(index, 4, incorrect)
                categorical.write(index, 5, percent_correct)
                categorical.write(index, 6, kappa)

                shannon_labels = []

                for i in range(len(labels)):
                    label = labels[i]
                    label_tokens = label.split('_')
                    
                    question = label_tokens[0]
                    answer = label_tokens[1]
                    
                    if question.startswith(row_question):
                        matrix = matrices[job.app_key]               
                        counts = matrix['counts']
    
                        label = labels[i]
                        
                        label_tokens = label.split('_')
                        
                        try:
                            count = counts[label_tokens[1]]
                        except KeyError:
                            count = 0
                            
                        shannon_labels.append(count)
            
                        categorical.write(index, 8 + i, count)
                    else:
                        categorical.write(index, 8 + i, '')

                categorical.write(index, 7, shannon(shannon_labels))
        
                index += 1

            elif json_obj['model_type'] == 'forest':
                summary = json_obj['summary'].strip()
        
                lines = []
        
                for line in summary.split('\n'):
                    line = string.replace(line, '  ', '\t')
            
                    while string.find(line, '\t\t') != -1:
                        line = string.replace(line, '\t\t', '\t')
                
                    lines.append(line.strip())
                
                key = key.replace('FEATURE_VALUE_DT_', '').replace('R1', '').replace(' (Forest)', '')
                tokens = key.split('_')
                
                row_question = tokens[1]
        
                forest.write(forest_index, 0, tokens[0])
                forest.write(forest_index, 1, row_question)
        
                tokens = lines[0].split('\t')
                correct = int(tokens[1])
                percent_correct = float(string.replace(tokens[2], '%', '').strip())

                tokens = lines[1].split('\t')
                incorrect = int(tokens[1])

                tokens = lines[2].split('\t')
                kappa = float(tokens[1])
        
                forest.write(forest_index, 2, correct + incorrect)
                forest.write(forest_index, 3, correct)
                forest.write(forest_index, 4, incorrect)
                forest.write(forest_index, 5, percent_correct)
                forest.write(forest_index, 6, kappa)

                shannon_labels = []

                for i in range(len(labels)):
                    label = labels[i]
                    label_tokens = label.split('_')
                    
                    question = label_tokens[0]
                    answer = label_tokens[1]
                    
                    if question.startswith(row_question):
                        matrix = matrices[job.app_key]               
                        counts = matrix['counts']
    
                        label = labels[i]
                        
                        label_tokens = label.split('_')
                        
                        try:
                            count = counts[label_tokens[1]]
                        except KeyError:
                            count = 0
                            
                        shannon_labels.append(count)
            
                        forest.write(forest_index, 8 + i, count)
                    else:
                        forest.write(forest_index, 8 + i, '')

                forest.write(forest_index, 7, shannon(shannon_labels))
        
                forest_index += 1
            elif json_obj['model_type'] == 'regression':
                summary = json_obj['summary'].strip()
        
                lines = []
        
                for line in summary.split('\n'):
                    line = string.replace(line, '  ', '\t')
            
                    while string.find(line, '\t\t') != -1:
                        line = string.replace(line, '\t\t', '\t')
                
                    lines.append(line.strip())
                    
                model = json_obj['model'].strip()

                while string.find(model, '\n\n') != -1:
                    model = string.replace(model, '\n\n', '\n')
                
                model_lines = model.split('\n')    

                key = key.replace('FEATURE_VALUE_DT_', '').replace('R1', '')
                tokens = key.split('_')
        
                continuous.write(continuous_index, 0, tokens[0])
                continuous.write(continuous_index, 1, tokens[1])
        
                tokens = lines[5].split('\t')
                num_instances = int(tokens[1].strip())

                tokens = lines[2].split('\t')
                rms_error = float(tokens[1])
        
                continuous.write(continuous_index, 2, num_instances)
                continuous.write(continuous_index, 3, rms_error)
                continuous.write(continuous_index, 4, json_obj['correlation'])
                continuous.write(continuous_index, 5, json_obj['correlation'] * json_obj['correlation'])
                continuous.write(continuous_index, 6, len(model_lines) - 4)
                continuous_index += 1

    io_str = StringIO.StringIO()
    workbook.save(io_str)

    response = HttpResponse(io_str.getvalue(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="Mobilyze_' + datetime.date.today().strftime('%Y%m%d') + '.xls"'
    
    io_str.close()
    
    return response


def parse_matrix(matrix_str):
    lines = matrix_str.strip().split('\n')[3:]
    
    matrix_obj = {}
    
    counts = {}
    
    for line_index in range(len(lines)):
        line = lines[line_index].strip()
        
        while string.find(line, '  ') != -1:
            line = string.replace(line, '  ', ' ')
            
        line_tokens = line.split(' ')
        
        label = line_tokens[-1]
        
        label_count = 0.0

        for token_index in range(len(lines)):
            label_count += float(line_tokens[token_index])
        
        counts[label] = label_count
        
    matrix_obj['counts'] = counts
    
    return matrix_obj

        
def shannon(counts):
    if len(counts) == 0:
        return 0
    
    n_labels = numpy.sum(counts)

    if n_labels <= 1:
        return 0

    probs = counts / n_labels
    n_classes = numpy.count_nonzero(probs)

    if n_classes <= 1:
        return 0

    ent = 0.0

    for i in probs:
        if i > 0:
            ent -= i * math.log(i, n_classes)

    return ent
    
    
# === Confusion Matrix ===
#  a  b  c  d  e   <-- classified as
#  0  0  0  0  0 |  a = ?
#  0 15  0  9  1 |  b = alone
#  0  0  5  0  0 |  c = strangers
#  0  9  0  0  3 |  d = acquaintances
#  0  2  0  4  0 |  e = friends
# 
# === Confusion Matrix ===
#  a  b  c  d  e  f  g  h   <-- classified as
# 21  1  2  0  0  0  0  2 |  a = personal_space
#  0  0  0  0  1  0  0  0 |  b = shopping
#  1  0  2  0  0  0  0  0 |  c = other_persons_space
#  0  0  0  0  0  0  0  0 |  d = ?
#  0  1  0  0  0  0  0  0 |  e = transit
#  0  1  0  0  0  0  0  0 |  f = self_care
#3  0  1  0  0  0  1  0  0 |  g = dining
#  3  0  0  0  0  0  0  0 |  h = work_or_school
#  
# === Confusion Matrix ===
#  a  b  c  d  e  f  g   <-- classified as
# 29  0  0  0  0  2  0 |  a = personal_space
#  1  0  0  0  0  0  0 |  b = other_persons_space
#  1  0  0  0  0  0  0 |  c = entertainment
#  0  0  0  0  0  0  0 |  d = ?
#  1  0  0  0  0  0  0 |  e = transit
#  2  0  0  0  0  0  0 |  f = self_care
#  2  0  0  0  0  0  0 |  g = dining
