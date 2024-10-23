#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Execute CMD from Dockerfile (i.e., start Gunicorn)
exec "$@"
