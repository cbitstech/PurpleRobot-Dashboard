from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from data_sources.models import DataReport

def render_report(request, report_key):
    report_key = int(report_key)
    c = RequestContext(request)
    
    report = DataReport.objects.get(pk=report_key)
    
    c['report'] = report
    
    return render_to_response('report_graph.html', c)

def home(request):
    c = RequestContext(request)

    return render_to_response('home.html', c)

