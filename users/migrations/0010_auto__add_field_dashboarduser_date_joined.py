# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DashboardUser.date_joined'
        db.add_column(u'users_dashboarduser', 'date_joined',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 5, 9, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DashboardUser.date_joined'
        db.delete_column(u'users_dashboarduser', 'date_joined')


    models = {
        u'users.dashboarduser': {
            'Meta': {'object_name': 'DashboardUser'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '512'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512'})
        }
    }

    complete_apps = ['users']