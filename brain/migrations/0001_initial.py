# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ReportJob'
        db.create_table(u'brain_reportjob', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('parameters', self.gf('django.db.models.fields.TextField')(max_length=1048576)),
            ('job_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('job_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('result_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('result_type', self.gf('django.db.models.fields.CharField')(default='application/octet-stream', max_length=128)),
        ))
        db.send_create_signal(u'brain', ['ReportJob'])


    def backwards(self, orm):
        # Deleting model 'ReportJob'
        db.delete_table(u'brain_reportjob')


    models = {
        u'brain.reportjob': {
            'Meta': {'object_name': 'ReportJob'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'job_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'parameters': ('django.db.models.fields.TextField', [], {'max_length': '1048576'}),
            'result_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'result_type': ('django.db.models.fields.CharField', [], {'default': "'application/octet-stream'", 'max_length': '128'})
        }
    }

    complete_apps = ['brain']