# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'DashboardUser.last_name'
        db.delete_column(u'users_dashboarduser', 'last_name')

        # Deleting field 'DashboardUser.is_active'
        db.delete_column(u'users_dashboarduser', 'is_active')

        # Deleting field 'DashboardUser.is_staff'
        db.delete_column(u'users_dashboarduser', 'is_staff')

        # Deleting field 'DashboardUser.date_joined'
        db.delete_column(u'users_dashboarduser', 'date_joined')

        # Deleting field 'DashboardUser.first_name'
        db.delete_column(u'users_dashboarduser', 'first_name')

        # Deleting field 'DashboardUser.is_superuser'
        db.delete_column(u'users_dashboarduser', 'is_superuser')

        # Deleting field 'DashboardUser.email'
        db.delete_column(u'users_dashboarduser', 'email')

        # Removing M2M table for field groups on 'DashboardUser'
        db.delete_table('users_dashboarduser_groups')

        # Removing M2M table for field user_permissions on 'DashboardUser'
        db.delete_table('users_dashboarduser_user_permissions')


        # Changing field 'DashboardUser.username'
        db.alter_column(u'users_dashboarduser', 'username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=512))
        # Removing index on 'DashboardUser', fields ['username']
        db.delete_index(u'users_dashboarduser', ['username'])


    def backwards(self, orm):
        # Adding index on 'DashboardUser', fields ['username']
        db.create_index(u'users_dashboarduser', ['username'])

        # Adding field 'DashboardUser.last_name'
        db.add_column(u'users_dashboarduser', 'last_name',
                      self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True),
                      keep_default=False)

        # Adding field 'DashboardUser.is_active'
        db.add_column(u'users_dashboarduser', 'is_active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'DashboardUser.is_staff'
        db.add_column(u'users_dashboarduser', 'is_staff',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'DashboardUser.date_joined'
        raise RuntimeError("Cannot reverse this migration. 'DashboardUser.date_joined' and its values cannot be restored.")
        # Adding field 'DashboardUser.first_name'
        db.add_column(u'users_dashboarduser', 'first_name',
                      self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True),
                      keep_default=False)

        # Adding field 'DashboardUser.is_superuser'
        db.add_column(u'users_dashboarduser', 'is_superuser',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'DashboardUser.email'
        raise RuntimeError("Cannot reverse this migration. 'DashboardUser.email' and its values cannot be restored.")
        # Adding M2M table for field groups on 'DashboardUser'
        db.create_table(u'users_dashboarduser_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dashboarduser', models.ForeignKey(orm[u'users.dashboarduser'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(u'users_dashboarduser_groups', ['dashboarduser_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'DashboardUser'
        db.create_table(u'users_dashboarduser_user_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dashboarduser', models.ForeignKey(orm[u'users.dashboarduser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(u'users_dashboarduser_user_permissions', ['dashboarduser_id', 'permission_id'])


        # Changing field 'DashboardUser.username'
        db.alter_column(u'users_dashboarduser', 'username', self.gf('django.db.models.fields.CharField')(max_length=30, unique=True))

    models = {
        u'users.dashboarduser': {
            'Meta': {'object_name': 'DashboardUser'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512'})
        }
    }

    complete_apps = ['users']