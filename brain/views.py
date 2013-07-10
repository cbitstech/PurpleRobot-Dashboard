
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from models import *

def report_contents(request, report_id):
    report = get_object_or_404(ReportJob, pk=report_id, result_file__isnull=False)
    
    return HttpResponse(report.result_file.read(), content_type=report.result_type)

@login_required
def all_analyses(request):
    analyses = ModelAnalysis.objects.all()
    
    context = RequestContext(request, {})
    context['analyses'] = analyses
    context['request'] = request
    
    return render_to_response('all_analyses.html', context)
    