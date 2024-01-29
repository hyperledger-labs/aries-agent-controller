#!/bin/bash
echo "Running migrations"
./manage.py migrate

echo "Compiling admin panel static assets"
./manage.py collectstatic --noinput

echo "Starting $NAME as `whoami`"
gunicorn ${DJANGO_WSGI_MODULE}:application --bind=0.0.0.0:${PORT} --log-level=${DJANGO_LOG_LEVEL}
