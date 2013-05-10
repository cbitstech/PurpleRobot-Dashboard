from django.contrib import admin
from participants.models import *

class StudyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)

admin.site.register(Study, StudyAdmin)

class StudyParticipantAdmin(admin.ModelAdmin):
    list_display = ('participant_id', 'study', 'active',)

admin.site.register(StudyParticipant, StudyParticipantAdmin)
