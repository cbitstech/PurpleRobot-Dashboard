import arff
import datetime
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

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        
        for analysis in ModelAnalysis.objects.filter(analysis_start=None):
            analysis.analysis_start = datetime.datetime.now()
            analysis.save()
            
            analysis_params = json.loads(analysis.parameters)
            analysis_params['url'] = 'http://dashboard.cbits.northwestern.edu' + reverse('brain_report_contents', args=[analysis.report.pk])
            
            job_params = json.loads(analysis.report.parameters)
            
            analysis_url = analysis.endpoint.endpoint
            
            query_string = urllib.urlencode(analysis_params)
            
            analysis_url += ('?' + query_string)
            
            print('ANALYSIS_URL: ' + analysis_url)

            model = urllib2.urlopen(analysis_url)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(model.read())
            temp_file.close()
            
            print('FILE: ' + temp_file.name)

            output_file = tempfile.NamedTemporaryFile()
            subprocess.call(['/usr/bin/java', '-jar', '/var/www/django/dashboard/brain/lib/obj_to_js.jar', temp_file.name], stdout=output_file)

            output_file.seek(0)
            analysis.generated_model = '/* ' + json.dumps(analysis_params, indent=2) + ' */\n\n' + output_file.read() 
            
            performance_url = analysis.endpoint.performance_endpoint.endpoint
            performance_url += ('?' + query_string)
            
            performance = urllib2.urlopen(performance_url)
            
            perf_txt = performance.read()
            perf_xml = parseString(perf_txt)
            
            print(perf_xml.getElementsByTagName('PerformanceVector')[0].firstChild.nodeValue)
            
            analysis.model_performance = perf_xml.getElementsByTagName('PerformanceVector')[0].firstChild.nodeValue.strip()

            analysis.analysis_end = datetime.datetime.now()
            analysis.save()

            count += 1
            
        print(str(count) + ' analyses(s) run.')
