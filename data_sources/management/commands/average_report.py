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
            
            bin_size = 1 # Second bins by default
            
            if time_delta.days < 1 and time_delta.seconds < 3600:
                bin_size = 1
            elif time_delta.days < 1:
                bin_size = 60
            elif time_delta.days < 7:
                bin_size = 900
            else:
                bin_size = 3600
            
            bin_delta = datetime.timedelta(seconds=bin_size)
            
            output = {}
            
            output['bin_size'] = bin_size
            output['bins'] = []
            
            bin_start = start_time
            
            total = 0
            
            while bin_start < end_time:
                bin_end = bin_start + bin_delta
                
                bin_contents = filter(lambda x: x[0] >= bin_start and x[0] <= bin_end, data_points)
                
                sum = 0
                
                for item in bin_contents:
                    sum += item[1]
                    
                bin_obj = {}

                if len(bin_contents) > 0:
                    bin_obj['count'] = sum / len(bin_contents)
                else:
                    bin_obj['count'] = -25
                    
                bin_obj['start'] = bin_start.strftime(time_format)
                bin_obj['end'] = bin_end.strftime(time_format)
                
                output['bins'].append(bin_obj);
                
                bin_start = bin_end
            
            report = DataReport(name='Average' + table_name)
            report.source = ds
            report.table = table_name
            report.report_type = 'average'
            
            report.start_time = start_time
            report.end_time = end_time
            
            report.report_json = json.dumps(output, indent=2)
            
            report.save()
            
            print(str(total) + ' found');
