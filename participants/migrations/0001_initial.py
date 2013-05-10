# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Study'
        db.create_table(u'participants_study', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal(u'participants', ['Study'])

        # Adding model 'StudyParticipant'
        db.create_table(u'participants_studyparticipant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant_id', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('study', self.gf('django.db.models.fields.related.ForeignKey')(related_name='participants', to=orm['participants.Study'])),
        ))
        db.send_create_signal(u'participants', ['StudyParticipant'])


    def backwards(self, orm):
        # Deleting model 'Study'
        db.delete_table(u'participants_study')

        # Deleting model 'StudyParticipant'
        db.delete_table(u'participants_studyparticipant')


    models = {
        u'participants.study': {
            'Meta': {'object_name': 'Study'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'participants.studyparticipant': {
            'Meta': {'object_name': 'StudyParticipant'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant_id': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'study': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'participants'", 'to': u"orm['participants.Study']"})
        }
    }

    complete_apps = ['participants']