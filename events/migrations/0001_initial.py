# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table(u'events_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=512, db_index=True)),
            ('event_type', self.gf('django.db.models.fields.CharField')(max_length=256, db_index=True)),
            ('logged', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('recorded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('altitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('time_drift_ms', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('properties', self.gf('django.db.models.fields.TextField')(max_length=16384, null=True, blank=True)),
        ))
        db.send_create_signal(u'events', ['Event'])


    def backwards(self, orm):
        # Deleting model 'Event'
        db.delete_table(u'events_event')


    models = {
        u'events.event': {
            'Meta': {'object_name': 'Event'},
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'logged': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'properties': ('django.db.models.fields.TextField', [], {'max_length': '16384', 'null': 'True', 'blank': 'True'}),
            'recorded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'time_drift_ms': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'})
        }
    }

    complete_apps = ['events']