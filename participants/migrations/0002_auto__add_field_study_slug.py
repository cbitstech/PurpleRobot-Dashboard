# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Study.slug'
        db.add_column(u'participants_study', 'slug',
                      self.gf('django.db.models.fields.SlugField')(default='', unique=True, max_length=512),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Study.slug'
        db.delete_column(u'participants_study', 'slug')


    models = {
        u'participants.study': {
            'Meta': {'object_name': 'Study'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '512'})
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