import json
import datetime

from django.core.management.base import BaseCommand, CommandError

from data_sources.models import DataSource, DataReport

class Command(BaseCommand):
    def handle(self, *args, **options):
        source_name = args[0]
        table_name = args[1]
        column_name = args[2]
        
        time_format = '%Y-%m-%d %H:%M:%S'
        
        start_time = datetime.datetime.strptime(args[3], time_format)
        end_time = datetime.datetime.strptime(args[4], time_format)
        
        for ds in DataSource.objects.filter(name=source_name):
            data_points = ds.fetch_data(table_name, column_name, start=start_time, end=end_time)
            
            time_delta = end_time - start_time
            
            output = {}
            
            output['bin_size'] = 0
            output['bins'] = []
            
            for x in data_points:
                bin_obj = {}
                bin_obj['count'] = x[1]
                bin_obj['start'] = x[0].strftime(time_format)
                bin_obj['end'] = x[0].strftime(time_format)
                
                output['bins'].append(bin_obj);
            
            report = DataReport(name='Values ' + table_name)
            report.source = ds
            report.table = table_name
            report.report_type = 'values'
            
            report.start_time = start_time.strftime(time_format)
            report.end_time = end_time.strftime(time_format)
            
            report.report_json = json.dumps(output, indent=2)
            
            report.save()
            
            print(str(len(data_points)) + ' found');
