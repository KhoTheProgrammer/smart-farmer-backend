#!/bin/bash
# Script to import full geospatial data to production database
# This connects to your Render PostgreSQL database and imports all districts and villages

set -e  # Exit on error

echo "=========================================="
echo "Import Full Dataset to Production"
echo "=========================================="
echo ""

# Check if DATABASE_URL is set
if [ -z "$PRODUCTION_DATABASE_URL" ]; then
    echo "❌ Error: PRODUCTION_DATABASE_URL environment variable not set"
    echo ""
    echo "Please set it first:"
    echo "  export PRODUCTION_DATABASE_URL='postgresql://user:pass@host:port/dbname'"
    echo ""
    echo "Get this URL from:"
    echo "  1. Go to https://dashboard.render.com"
    echo "  2. Open your database (mlimi-wanzeru-db)"
    echo "  3. Copy the 'External Database URL'"
    echo ""
    exit 1
fi

# Check if data files exist
if [ ! -f "data/malawi_districts.geojson" ]; then
    echo "❌ Error: data/malawi_districts.geojson not found"
    exit 1
fi

if [ ! -f "data/malawi_villages.geojson" ]; then
    echo "❌ Error: data/malawi_villages.geojson not found"
    exit 1
fi

echo "✓ Found data files"
echo "  - Districts: $(du -h data/malawi_districts.geojson | cut -f1)"
echo "  - Villages: $(du -h data/malawi_villages.geojson | cut -f1)"
echo ""

# Backup current DATABASE_URL
ORIGINAL_DATABASE_URL="${DATABASE_URL:-}"

# Set production database URL
export DATABASE_URL="$PRODUCTION_DATABASE_URL"

echo "🔗 Connecting to production database..."
echo ""

# Test connection
python -c "
import os
import psycopg2
from urllib.parse import urlparse

url = urlparse(os.environ['DATABASE_URL'])
try:
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        database=url.path[1:]
    )
    conn.close()
    print('✓ Database connection successful')
except Exception as e:
    print(f'❌ Connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "Failed to connect to database. Please check your DATABASE_URL."
    exit 1
fi

echo ""
echo "⚠️  WARNING: This will import data to PRODUCTION database"
echo "   Database: $(echo $PRODUCTION_DATABASE_URL | sed 's/:[^:]*@/@/g')"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Import cancelled."
    exit 0
fi

echo ""
echo "📥 Starting import..."
echo ""

# Import districts
echo "1/2 Importing districts..."
python manage.py import_boundaries --districts data/malawi_districts.geojson

echo ""
echo "2/2 Importing villages..."
python manage.py import_boundaries --villages data/malawi_villages.geojson

# Restore original DATABASE_URL
if [ -n "$ORIGINAL_DATABASE_URL" ]; then
    export DATABASE_URL="$ORIGINAL_DATABASE_URL"
else
    unset DATABASE_URL
fi

echo ""
echo "=========================================="
echo "✅ Import Complete!"
echo "=========================================="
echo ""
echo "Imported:"
echo "  - 28 districts with boundaries"
echo "  - 400+ villages with locations"
echo ""
echo "Your production API now has full location data!"
echo ""
