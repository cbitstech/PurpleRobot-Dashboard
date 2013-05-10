#!/bin/bash

source /var/www/django/venv/bin/activate
cd /var/www/django/dashboard
./manage.py cron
