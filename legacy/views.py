import datetime
import hashlib
import json
import pytz
from pytz import timezone
import time
import urllib2

from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.context_processors import *
from django.http import HttpResponse
from django.shortcuts import *
from django.template import *
from django.template.loader import *
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from pr_integration.util import *

@login_required
def legacy_status(request):
    
    c = RequestContext(request)
    
    c['all_databases'] = all_databases()
    
    c['request'] = request

    return render_to_response('legacy_dashboard.html', c)

@login_required
def database_contents(request, database):
    c = RequestContext(request)
    
    c['all_databases'] = all_databases()
    c['request'] = request
    c['tables'] = fetch_tables(database)

    return render_to_response('legacy_dashboard_user.html', c)
