from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from models import ReportJob

def report_contents(request, report_id):
    report = get_object_or_404(ReportJob, pk=report_id, result_file__isnull=False)
    
    return HttpResponse(report.result_file.read(), content_type=report.result_type)