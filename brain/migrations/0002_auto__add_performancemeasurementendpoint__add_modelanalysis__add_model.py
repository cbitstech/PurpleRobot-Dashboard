# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PerformanceMeasurementEndpoint'
        db.create_table(u'brain_performancemeasurementendpoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('endpoint', self.gf('django.db.models.fields.URLField')(unique=True, max_length=256)),
        ))
        db.send_create_signal(u'brain', ['PerformanceMeasurementEndpoint'])

        # Adding model 'ModelAnalysis'
        db.create_table(u'brain_modelanalysis', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(related_name='analyses', to=orm['brain.ReportJob'])),
            ('analysis_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('analysis_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('parameters', self.gf('django.db.models.fields.TextField')(max_length=1048576)),
            ('generated_model', self.gf('django.db.models.fields.TextField')(max_length=1048576)),
            ('model_performance', self.gf('django.db.models.fields.TextField')(max_length=1048576)),
            ('accuracy', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('standard_deviation', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal(u'brain', ['ModelAnalysis'])

        # Adding model 'ModelGeneratorEndpoint'
        db.create_table(u'brain_modelgeneratorendpoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('endpoint', self.gf('django.db.models.fields.URLField')(unique=True, max_length=256)),
            ('expect_type', self.gf('django.db.models.fields.CharField')(default='application/octet-stream', max_length=128)),
            ('parameters', self.gf('django.db.models.fields.TextField')(max_length=1048576)),
            ('performance_endpoint', self.gf('django.db.models.fields.related.ForeignKey')(related_name='model_endpoints', unique=True, to=orm['brain.PerformanceMeasurementEndpoint'])),
        ))
        db.send_create_signal(u'brain', ['ModelGeneratorEndpoint'])


    def backwards(self, orm):
        # Deleting model 'PerformanceMeasurementEndpoint'
        db.delete_table(u'brain_performancemeasurementendpoint')

        # Deleting model 'ModelAnalysis'
        db.delete_table(u'brain_modelanalysis')

        # Deleting model 'ModelGeneratorEndpoint'
        db.delete_table(u'brain_modelgeneratorendpoint')


    models = {
        u'brain.modelanalysis': {
            'Meta': {'object_name': 'ModelAnalysis'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'analysis_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'analysis_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'generated_model': ('django.db.models.fields.TextField', [], {'max_length': '1048576'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_performance': ('django.db.models.fields.TextField', [], {'max_length': '1048576'}),
            'parameters': ('django.db.models.fields.TextField', [], {'max_length': '1048576'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'analyses'", 'to': u"orm['brain.ReportJob']"}),
            'standard_deviation': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        u'brain.modelgeneratorendpoint': {
            'Meta': {'object_name': 'ModelGeneratorEndpoint'},
            'endpoint': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '256'}),
            'expect_type': ('django.db.models.fields.CharField', [], {'default': "'application/octet-stream'", 'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'parameters': ('django.db.models.fields.TextField', [], {'max_length': '1048576'}),
            'performance_endpoint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'model_endpoints'", 'unique': 'True', 'to': u"orm['brain.PerformanceMeasurementEndpoint']"})
        },
        u'brain.performancemeasurementendpoint': {
            'Meta': {'object_name': 'PerformanceMeasurementEndpoint'},
            'endpoint': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
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