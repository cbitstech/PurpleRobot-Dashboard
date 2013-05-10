# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DashboardUser.is_active'
        db.add_column(u'users_dashboarduser', 'is_active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'DashboardUser.is_admin'
        db.add_column(u'users_dashboarduser', 'is_admin',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DashboardUser.is_active'
        db.delete_column(u'users_dashboarduser', 'is_active')

        # Deleting field 'DashboardUser.is_admin'
        db.delete_column(u'users_dashboarduser', 'is_admin')


    models = {
        u'users.dashboarduser': {
            'Meta': {'object_name': 'DashboardUser'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512'})
        }
    }

    complete_apps = ['users']