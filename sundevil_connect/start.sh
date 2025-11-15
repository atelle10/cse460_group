#!/bin/bash

python manage.py makemigrations portal
python manage.py makemigrations core
python manage.py migrate

python manage.py shell < create_test_users.py 2>/dev/null || true

python manage.py shell < create_test_events.py 2>/dev/null || true

python manage.py runserver 0.0.0.0:8000
