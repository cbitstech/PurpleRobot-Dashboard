# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ModelAnalysis.model_performance'
        db.alter_column(u'brain_modelanalysis', 'model_performance', self.gf('django.db.models.fields.TextField')(max_length=1048576, null=True))

        # Changing field 'ModelAnalysis.generated_model'
        db.alter_column(u'brain_modelanalysis', 'generated_model', self.gf('django.db.models.fields.TextField')(max_length=1048576, null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'ModelAnalysis.model_performance'
        raise RuntimeError("Cannot reverse this migration. 'ModelAnalysis.model_performance' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'ModelAnalysis.generated_model'
        raise RuntimeError("Cannot reverse this migration. 'ModelAnalysis.generated_model' and its values cannot be restored.")

    models = {
        u'brain.modelanalysis': {
            'Meta': {'object_name': 'ModelAnalysis'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'analysis_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'analysis_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'generated_model': ('django.db.models.fields.TextField', [], {'max_length': '1048576', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_performance': ('django.db.models.fields.TextField', [], {'max_length': '1048576', 'null': 'True', 'blank': 'True'}),
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