# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CachedMobilyzeReport'
        db.create_table(u'mobilyze_cachedmobilyzereport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('generated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('report_type', self.gf('django.db.models.fields.CharField')(default='status', max_length=512)),
            ('report', self.gf('django.db.models.fields.TextField')(max_length=1048576)),
        ))
        db.send_create_signal(u'mobilyze', ['CachedMobilyzeReport'])


    def backwards(self, orm):
        # Deleting model 'CachedMobilyzeReport'
        db.delete_table(u'mobilyze_cachedmobilyzereport')


    models = {
        u'mobilyze.cachedmobilyzereport': {
            'Meta': {'object_name': 'CachedMobilyzeReport'},
            'generated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.TextField', [], {'max_length': '1048576'}),
            'report_type': ('django.db.models.fields.CharField', [], {'default': "'status'", 'max_length': '512'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['mobilyze']