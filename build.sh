#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "from puja.models import CustomUser; CustomUser.objects.filter(username='admin').exists() or CustomUser.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='SUPER_ADMIN')"
