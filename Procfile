#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --run-syncdb

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
gunicorn config.wsgi
