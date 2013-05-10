import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from participants.models import Study

@login_required
def participants_list(request, slug):
    participants = []
    
    for study in Study.objects.filter(slug=slug):
        participants.extend(study.participant_ids(request.user, active=True))
    
    return HttpResponse(json.dumps(participants, indent=2), content_type='application/json')
