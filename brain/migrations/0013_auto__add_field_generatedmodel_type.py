# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'GeneratedModel.type'
        db.add_column(u'brain_generatedmodel', 'type',
                      self.gf('django.db.models.fields.CharField')(default='Unknown', max_length=1024),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'GeneratedModel.type'
        db.delete_column(u'brain_generatedmodel', 'type')


    models = {
        u'brain.cachedanalysis': {
            'Meta': {'object_name': 'CachedAnalysis'},
            'analysis': ('django.db.models.fields.TextField', [], {'max_length': '1048576'}),
            'generated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'brain.generatedmodel': {
            'Meta': {'object_name': 'GeneratedModel'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1048576'}),
            'generated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'brain.modelanalysis': {
            'Meta': {'object_name': 'ModelAnalysis'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'analysis_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'analysis_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'endpoint': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'analyses'", 'null': 'True', 'to': u"orm['brain.ModelGeneratorEndpoint']"}),
            'generated_model': ('django.db.models.fields.TextField', [], {'max_length': '1048576', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_performance': ('django.db.models.fields.TextField', [], {'max_length': '1048576', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
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
            'performance_endpoint': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'model_endpoints'", 'null': 'True', 'to': u"orm['brain.PerformanceMeasurementEndpoint']"})
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
            'result_type': ('django.db.models.fields.CharField', [], {'default': "'application/octet-stream'", 'max_length': '128'}),
            'stats_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'stats_type': ('django.db.models.fields.CharField', [], {'default': "'application/json'", 'max_length': '128'})
        }
    }

    complete_apps = ['brain']