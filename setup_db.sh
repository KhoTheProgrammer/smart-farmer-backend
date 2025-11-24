#!/bin/bash

# Setup script for Mlimi Wanzeru database
# This script creates the PostgreSQL database and enables PostGIS extension

echo "Setting up Mlimi Wanzeru database..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using default values."
    DB_NAME="mlimi_wanzeru"
    DB_USER="postgres"
fi

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "Error: PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Create database
echo "Creating database: $DB_NAME"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database may already exist"

# Enable PostGIS extension
echo "Enabling PostGIS extension..."
sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Verify PostGIS installation
echo "Verifying PostGIS installation..."
sudo -u postgres psql -d $DB_NAME -c "SELECT PostGIS_version();"

echo "Database setup complete!"
echo "You can now run: python manage.py migrate"
