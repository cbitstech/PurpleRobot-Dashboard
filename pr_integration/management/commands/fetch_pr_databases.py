import psycopg2

from django.core.management.base import BaseCommand, CommandError

from data_sources.models import DataSource

class Command(BaseCommand):
    def handle(self, *args, **options):
        db_string = 'host=\'db2.cbits.northwestern.edu\' dbname=\'postgres\' user=\'postgres\' password=\'mohrLab1\''

        conn = psycopg2.connect(db_string)
        
        cursor = conn.cursor()
        
        cursor.execute('SELECT datname FROM pg_database;')
        
        for result in cursor:
            if len(result[0]) > 16:
                location_str = 'host=\'db2.cbits.northwestern.edu\' dbname=\'' + result[0] + '\' user=\'postgres\' password=\'mohrLab1\''
                name_str = 'Purple Robot: ' + result[0]
                
                ds = None
                
                for source in DataSource.objects.filter(location=location_str):
                    ds = source
                    
                if ds == None:
                    ds = DataSource(location=location_str, name=name_str)
                    
                ds.save()
                print(str(result))
                
                ds.table_names()
        
        cursor.close()
        conn.close()
