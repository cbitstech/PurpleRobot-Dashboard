from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

def home(request):
    c = RequestContext(request)

    return render_to_response('home.html', c)

