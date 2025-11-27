#!/usr/bin/env python
"""
Import full geospatial dataset to production database.
Connects to Render PostgreSQL and imports all districts and villages.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlimi_wanzeru.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from locations.models import District, Village


def check_database_connection():
    """Test database connection."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_data_files():
    """Check if data files exist."""
    districts_file = BASE_DIR / 'data' / 'malawi_districts.geojson'
    villages_file = BASE_DIR / 'data' / 'malawi_villages.geojson'
    
    if not districts_file.exists():
        print(f"❌ Error: {districts_file} not found")
        return False, None, None
    
    if not villages_file.exists():
        print(f"❌ Error: {villages_file} not found")
        return False, None, None
    
    # Get file sizes
    districts_size = districts_file.stat().st_size / (1024 * 1024)  # MB
    villages_size = villages_file.stat().st_size / (1024 * 1024)  # MB
    
    print(f"✓ Found data files:")
    print(f"  - Districts: {districts_size:.1f} MB")
    print(f"  - Villages: {villages_size:.1f} MB")
    
    return True, str(districts_file), str(villages_file)


def get_current_counts():
    """Get current record counts."""
    try:
        districts_count = District.objects.count()
        villages_count = Village.objects.count()
        return districts_count, villages_count
    except Exception as e:
        print(f"⚠️  Warning: Could not get current counts: {e}")
        return 0, 0


def main():
    """Main import function."""
    print("=" * 50)
    print("Import Full Dataset to Production")
    print("=" * 50)
    print()
    
    # Check if PRODUCTION_DATABASE_URL is set
    prod_db_url = os.environ.get('PRODUCTION_DATABASE_URL')
    if not prod_db_url:
        print("❌ Error: PRODUCTION_DATABASE_URL environment variable not set")
        print()
        print("Please set it first:")
        print("  export PRODUCTION_DATABASE_URL='postgresql://user:pass@host:port/dbname'")
        print()
        print("Get this URL from:")
        print("  1. Go to https://dashboard.render.com")
        print("  2. Open your database (mlimi-wanzeru-db)")
        print("  3. Copy the 'External Database URL'")
        print()
        sys.exit(1)
    
    # Temporarily set DATABASE_URL to production
    original_db_url = os.environ.get('DATABASE_URL')
    os.environ['DATABASE_URL'] = prod_db_url
    
    # Reload Django settings with new DATABASE_URL
    from django.conf import settings
    from django.db import connections
    
    # Close existing connections
    for conn in connections.all():
        conn.close()
    
    # Reconfigure database
    import dj_database_url
    settings.DATABASES['default'] = dj_database_url.config(
        default=prod_db_url,
        conn_max_age=600,
        conn_health_checks=True,
        engine='django.contrib.gis.db.backends.postgis'
    )
    
    print("🔗 Connecting to production database...")
    print()
    
    # Test connection
    if not check_database_connection():
        print()
        print("Failed to connect to database. Please check your DATABASE_URL.")
        sys.exit(1)
    
    print("✓ Database connection successful")
    print()
    
    # Check data files
    files_ok, districts_file, villages_file = check_data_files()
    if not files_ok:
        sys.exit(1)
    
    print()
    
    # Get current counts
    current_districts, current_villages = get_current_counts()
    print(f"Current database contents:")
    print(f"  - Districts: {current_districts}")
    print(f"  - Villages: {current_villages}")
    print()
    
    # Confirm
    print("⚠️  WARNING: This will import data to PRODUCTION database")
    db_info = prod_db_url.split('@')[1] if '@' in prod_db_url else 'unknown'
    print(f"   Database: {db_info}")
    print()
    
    if current_districts > 0 or current_villages > 0:
        print("⚠️  Database already contains location data!")
        print("   This import will ADD to existing data (may create duplicates)")
        print()
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Import cancelled.")
        sys.exit(0)
    
    print()
    print("📥 Starting import...")
    print()
    
    try:
        # Import districts
        print("1/2 Importing districts...")
        print("-" * 50)
        call_command('import_boundaries', districts=districts_file, verbosity=2)
        
        print()
        print("2/2 Importing villages...")
        print("-" * 50)
        call_command('import_boundaries', villages=villages_file, verbosity=2)
        
        # Get final counts
        final_districts, final_villages = get_current_counts()
        
        print()
        print("=" * 50)
        print("✅ Import Complete!")
        print("=" * 50)
        print()
        print("Final database contents:")
        print(f"  - Districts: {final_districts} (added {final_districts - current_districts})")
        print(f"  - Villages: {final_villages} (added {final_villages - current_villages})")
        print()
        print("Your production API now has full location data!")
        print()
        
    except Exception as e:
        print()
        print(f"❌ Import failed: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Restore original DATABASE_URL
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']


if __name__ == '__main__':
    main()

