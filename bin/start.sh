#!/bin/bash

set -e

echo "${0}: running migrations."
./manage.py makemigrations --merge
./manage.py migrate

echo "${0}: collecting statics."
./manage.py collectstatic --noinput

echo "Starting $NAME as `whoami`"
gunicorn ${DJANGO_WSGI_MODULE}:application --bind=0.0.0.0:${PORT} --log-level=${DJANGO_LOG_LEVEL} --access-logfile '-' --error-logfile '-'
