#!/bin/sh
source venv/bin/activate
flask db upgrade
exec gunicorn --bind 0.0.0.0:443 --access-logfile - --error-logfile - microblog:app
