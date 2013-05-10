import arff
import json
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify


from data_sources.models import DataSource, DataReport

class Command(BaseCommand):
    def handle(self, *args, **options):
        params = json.load(open(args[0]))

        source_name = params['database']
        
        label_table_name = None
        label_column_name = None
        
        for key,value in params['label'].iteritems():
            label_table_name = key
            label_column_name = value
        
        # Add parameters for setting ranges...
        
        past = datetime.datetime(datetime.MINYEAR, 1, 1)
        future = datetime.datetime(datetime.MAXYEAR, 12, 31)
        
        for ds in DataSource.objects.filter(name__contains=source_name):
            table_names = ds.table_names()

            table_columns = {}
            
            for name in table_names:
                table_columns[name] = ds.table_columns(name)
                
#            print(json.dumps(table_columns, indent=2))
        
            points = ds.fetch_data(label_table_name, label_column_name, past, future)

            label_value_name = label_table_name + '_' + label_column_name
            
            categorical_values = {}
            rows = []
            row_keys = []
            
            for point in points:
                row_dict = {}
                
                point_time = point[0]
                label_value = point[1]

# FOR WifiAccessPointsProbe: [(u'ACCESS_POINT_COUNT', u'integer'), (u'CURRENT_BSSID', u'text'), (u'CURRENT_LINK_SPEED', u'integer'), (u'CURRENT_RSSI', u'integer'), (u'CURRENT_SSID', u'text')]
# GOT [37, u'd8:c7:c8:6d:ec:f8', 65, -57, u'"Northwestern"']
# FOR RunningSoftwareProbe: [(u'RUNNING_TASK_COUNT', u'integer')]
# GOT [9]

                row_dict[label_value_name] = label_value
                
                for table, columns in table_columns.iteritems():
                    fetched = ds.fetch_nearest(point_time, table, columns)
                    
                    if len(fetched) > 0:
                        for i in range(0, len(columns)):
                            column = columns[i]
                            
                            column_key = table + '_' + column[0]
                            
                            if row_keys.count(column_key) == 0:
                                row_keys.append(column_key)
                            
                            if column[1] == 'text' or column[1] == 'boolean':
                                column_values = set(['?'])

                                try:
                                    column_values = categorical_values[column_key]
                                except KeyError:
                                    categorical_values[column_key] = column_values
                                
                                column_values.add(slugify(unicode(str(fetched[i]))))
                                
                            if fetched[i] == True or fetched[i] == False:
                                row_dict[column_key] = slugify(unicode(str(fetched[i])))
                            elif column[1] == 'text':
                                row_dict[column_key] = slugify(unicode(fetched[i]))
                            else:
                                row_dict[column_key] = fetched[i]
                        
                rows.append(row_dict)

            row_keys.sort()            
                
            data = { 'relation': label_table_name + '_' + label_column_name, 'description': '' }
            
            attributes = []
            
            ignore = []

            for row_key in row_keys:
                value_def = 'REAL'

                if row_key in categorical_values:
                    value_def = []
                    
                    for value in categorical_values[row_key]:
                        value_def.append(value)
                
                if value_def == 'REAL' or len(value_def) > 1:        
                    attributes.append((row_key, value_def))
                else:
                    ignore.append(row_key)
                
            data['attributes'] = attributes
            
            data_rows = []
            
            for row_dict in rows:
                data_row = []
                
                for row_key in row_keys:
                    if ignore.count(row_key) == 0:
                        try:
                            data_row.append(row_dict[row_key])
                        except KeyError:
                            data_row.append('?')
                
                data_rows.append(data_row)
            
            data['data'] = data_rows
            
            print(arff.dumps(data))
#            print(json.dumps(data, indent=1))
#            
#                
#                print(str(point))
#            
#            report = DataReport(name='Average' + table_name)
#            report.source = ds
#            report.table = table_name
#            report.report_type = 'average'
#            
#            report.start_time = start_time
#            report.end_time = end_time
#            
#            report.report_json = json.dumps(output, indent=2)
#            
#            report.save()
#            
#            print(str(total) + ' found');


