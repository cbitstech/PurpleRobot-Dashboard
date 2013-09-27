#!/bin/bash

source /var/www/django/venv/bin/activate
cd /var/www/django/dashboard
./manage.py update_mobilyze_user_states cjkarr
./manage.py update_mobilyze_user_responses cjkarr

