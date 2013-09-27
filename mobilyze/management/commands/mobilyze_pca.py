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

'''

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
'''

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        
        admin_user = DashboardUser.objects.get(username=args[0])

        mobilyze = Study.objects.get(slug='mobilyze-2013')

        table = 'undefined'
        now = datetime.datetime.utcnow()
        start = datetime.datetime.utcfromtimestamp(0)
        
        all_values = {} # date, name, value

        for study in Study.objects.filter(slug='mobilyze-2013'):
            for id in study.participant_ids(admin_user):
                m = hashlib.md5()
                m.update(id)
    
                hash = m.hexdigest()
                
                readings = []

                try:
                    readings = all_values[id]
                except KeyError:
                    pass
                    
                if database_exists(hash):
                    if table_exists(hash, table):
                        for column in MOBILYZE_QUESTIONS:
                            if column in CATEGORICAL_QUESTIONS:
                                pass
                            else:
                                values = fetch_data(hash, table, column, start, now, filter=True)
                
                                for value in values:
                                    if True: # try:
                                        readings.append((value[0], id, column, float(value[1])))
                                    # except:
                                    
                all_values[id] = readings
                
        for k,v in all_values.iteritems():
            all_values[k].sort(key=lambda x: x[0])
                                    
        print(json.dumps(all_values, indent=2, cls=DjangoJSONEncoder))
        
        
#                    else:
#                        values = fetch_data(hash, 'mobilyze_eav', 'FEATURE_VALUE_DT_name,FEATURE_VALUE_DT_value', start, now, filter=False)
#                
#                        last_name = None
#                
#                        for value in values:
#                            name = 'FEATURE_VALUE_DT_' + value[1]
#                        
#                            if name in MOBILYZE_QUESTIONS and (name in CATEGORICAL_QUESTIONS) == False and last_name != name:
#                                last_name = name
#                                sheet.write(row_counter, 0, row_counter)
#                                sheet.write(row_counter, 1, id)
#                                sheet.write(row_counter, 2, value[1])
#                                sheet.write(row_counter, 3, value[0].isoformat(' '))
#                            
#                                try:
#                                    sheet.write(row_counter, 4, float(value[2]))
#                                except:
#                                    sheet.write(row_counter, 4, value[2])


