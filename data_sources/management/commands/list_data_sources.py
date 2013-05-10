import psycopg2

from django.core.management.base import BaseCommand, CommandError

from data_sources.models import DataSource

class Command(BaseCommand):
    def handle(self, *args, **options):
        source_name = args[0]
        
        for ds in DataSource.objects.filter(name=source_name):
            for name in ds.table_names():
                print(name)
                
