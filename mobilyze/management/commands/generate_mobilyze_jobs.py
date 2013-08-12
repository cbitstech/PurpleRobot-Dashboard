import arff
import datetime
import hashlib
import json
import tempfile
import uuid
import urllib
import urllib2
import subprocess

from xml.dom.minidom import *

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from brain.models import *
from data_sources.models import DataSource, DataReport
from participants.models import *

MOBILYZE_QUESTIONS = [
    'FEATURE_VALUE_DT_CalmR1',
    'FEATURE_VALUE_DT_StressR1',
    'FEATURE_VALUE_DT_AnxietyR1',
    'FEATURE_VALUE_DT_RelaxednessR1',
#    'FEATURE_VALUE_DT_TenseTODOR1',
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

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0

        mobilyze = Study.objects.get(slug='mobilyze-2013')
                
        for participant in StudyParticipant.objects.filter(study=mobilyze):
            part_id = participant.participant_id

            m = hashlib.md5()
            m.update(part_id)
            hash = m.hexdigest()
            
            for question in CATEGORICAL_QUESTIONS:
                app_key = part_id + '_' + question
                
                reports = ReportJob.objects.filter(app_key=app_key)
                
                if reports.count() == 0:
                    count += 1
                    job = ReportJob(app_key=app_key)
                    job.name = 'Mobilyze ' + part_id + ': ' + question
                    
                    params = {}
                    params['database'] = hash
                    params['arff_name'] = question
                    label = { "undefined": question }
                    params['label'] = label
                    params['type'] = 'nominal'
                    
                    job.parameters = json.dumps(params, indent=2)
                    
                    job.save()

            for question in MOBILYZE_QUESTIONS:
                app_key = part_id + '_' + question
                
                reports = ReportJob.objects.filter(app_key=app_key)
                
                if reports.count() == 0:
                    count += 1
                    job = ReportJob(app_key=app_key)
                    job.name = 'Mobilyze ' + part_id + ': ' + question
                    
                    params = {}
                    params['database'] = hash
                    params['arff_name'] = question
                    label = { "undefined": question }
                    params['label'] = label
                    params['type'] = 'numeric'
                    
                    job.parameters = json.dumps(params, indent=2)
                    
                    job.save()
            
        print(str(count) + ' job(s) created.')
