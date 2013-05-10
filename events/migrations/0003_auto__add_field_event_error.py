# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Event.error'
        db.add_column(u'events_event', 'error',
                      self.gf('django.db.models.fields.CharField')(db_index=True, max_length=512, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Event.error'
        db.delete_column(u'events_event', 'error')


    models = {
        u'events.event': {
            'Meta': {'object_name': 'Event'},
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'logged': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'properties': ('django.db.models.fields.TextField', [], {'max_length': '1048576', 'null': 'True', 'blank': 'True'}),
            'recorded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'time_drift_ms': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'})
        }
    }

    complete_apps = ['events']