import psycopg2

from django.core.management.base import BaseCommand, CommandError

from data_sources.models import DataSource

class Command(BaseCommand):
    def handle(self, *args, **options):
        for ds in DataSource.objects.all():
            print(ds.name)
