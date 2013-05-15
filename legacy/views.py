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
    c['my_database'] = database

    return render_to_response('legacy_dashboard_user.html', c)

@login_required
def legacy_fetch_data(request, database, table, column, timestamp):
    data = fetch_data(database, table, column, limit=500)
    
    for datum in data:
        if isinstance(datum[0], datetime.datetime):
            timestamp = pytz.utc.localize(datum[0])
            timestamp = timestamp.astimezone(timezone('US/Central'))

            datum[0] = time.mktime(timestamp.timetuple())

        if isinstance(datum[1], datetime.datetime):
            timestamp = pytz.utc.localize(datum[1])
            timestamp = timestamp.astimezone(timezone('US/Central'))

            datum[1] = time.mktime(timestamp.timetuple())
    
    return HttpResponse(json.dumps(data, indent=2), content_type="application/json")
