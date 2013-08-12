import datetime
import psycopg2

from django.contrib.gis.db import models

from dashboard import settings

from users.models import DashboardUser

class DataSource(models.Model):
    objects = models.GeoManager()
    
    name = models.CharField(max_length=512)
    location = models.CharField(max_length=512)
    
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='data_sources')

    def __unicode__(self):
        return self.name
        
    
    def table_names(self):
        names = []
        conn = psycopg2.connect(self.location)
        
        cursor = conn.cursor()
        
        cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\';')
        
        for result in cursor:
            names.append(result[0])
        
        conn.close()
        cursor.close()
        
        if names.count('SourceValue') > 0:
            names.remove('SourceValue')
        
        if names.count('window1') > 0:
            names.remove('window1')

        if names.count('window2') > 0:
            names.remove('window2')

        if names.count('window3') > 0:
            names.remove('window3')

        if names.count('WifiAccessPointsProbe.ACCESS_POINTS') > 0:
            names.remove('WifiAccessPointsProbe.ACCESS_POINTS')

        if names.count('user_data') > 0:
            names.remove('user_data')

        return names
        
        
    def table_columns(self, table_name):
        columns = []
        
        conn = psycopg2.connect(self.location)
        cursor = conn.cursor()
        
        cursor.execute('SELECT column_name,data_type FROM information_schema.columns WHERE table_name = \'' + table_name + '\';')
        
        skip_columns = ['id', 'sampleId', 'arrayIdx', 'timestamp', 'eventDateTime', 'insertedTime', 'EVENT_TIMESTAMP',  'GUID', 'TIMESTAMP', 'SCHEME_CONFIG', 'JSON_CONFIG']

        for result in cursor:
            if skip_columns.count(result[0]) == 0:
                columns.append((result[0], result[1],))
        
        conn.close()
        cursor.close()
        
        return columns
        

    def fetch_data(self, table_name, column_name, start, end):
        values = []
        
        conn = psycopg2.connect(self.location)
        
        cursor = conn.cursor()

        try:
            # print(cursor.mogrify('SELECT "eventDateTime","' + column_name + '" FROM "' + table_name + '" WHERE ("eventDateTime" >= %s AND "eventDateTime" <= %s);', (start, end,)))
            cursor.execute('SELECT "eventDateTime","' + column_name + '" FROM "' + table_name + '" WHERE ("eventDateTime" >= %s AND "eventDateTime" <= %s AND "' + column_name + '" IS NOT NULL);', (start, end,))
            
            for result in cursor:
                if result[1] == '':
                    result[1] = 'empty-string'
                    
                values.append((result[0], result[1],))
        except psycopg2.ProgrammingError:
            pass
        
        conn.close()
        cursor.close()
        
        return values


    def fetch_nearest(self, point_time, table_name, original_names):
        if len(original_names) < 1:
            return []
        
        column_names = []
    
        for i in range(0, len(original_names)):
            column_names.append('"' + original_names[i][0] + '"')
        
        # names_string = ','.join(column_names)
        
        conn = psycopg2.connect(self.location)
        
        fetched = []

        if len(column_names) > 0:
            for column in column_names:
                cursor = conn.cursor()
                cursor.execute('SELECT ' + column + ' FROM "' + table_name + '" WHERE ("eventDateTime" <= %s AND ' + column + ' IS NOT NULL) ORDER BY "eventDateTime" DESC LIMIT 1;', (point_time,))
                
                if cursor.rowcount > 0:
                    for result in cursor:
                        fetched.append(result[0])
                else:
                    fetched.append(None)
        
                cursor.close()
        conn.close()
        
        return fetched
    

class DataReport(models.Model):
    objects = models.GeoManager()
    
    name = models.CharField(max_length=512)
    source = models.ForeignKey(DataSource, related_name='data_reports')
    table = models.CharField(max_length=512)

    report_type = models.CharField(max_length=512)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    report_json = models.TextField(max_length=4194304)

    
