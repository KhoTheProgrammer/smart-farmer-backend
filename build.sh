#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies for GDAL and PostGIS
apt-get update
apt-get install -y gdal-bin libgdal-dev python3-gdal

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Import initial data (crops are in migrations)
echo "Database setup complete"
