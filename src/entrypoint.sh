#!/usr/bin/env bash
set -e
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput 2>/dev/null || true
python manage.py runserver 0.0.0.0:8000