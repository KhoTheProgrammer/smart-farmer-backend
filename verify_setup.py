#!/usr/bin/env python
"""
Verification script for Mlimi Wanzeru setup
Tests that all components are properly configured
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlimi_wanzeru.settings')
django.setup()

from django.conf import settings
from django.db import connection
from django.contrib.gis.geos import Point, Polygon


def test_database_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def test_postgis():
    """Test PostGIS extension."""
    print("\nTesting PostGIS extension...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT PostGIS_version();")
            version = cursor.fetchone()[0]
            print(f"✓ PostGIS version: {version}")
        return True
    except Exception as e:
        print(f"✗ PostGIS test failed: {e}")
        return False


def test_geodjango():
    """Test GeoDjango functionality."""
    print("\nTesting GeoDjango...")
    try:
        # Test Point creation
        point = Point(-13.9626, 33.7741)  # Lilongwe coordinates
        print(f"✓ Created Point: {point}")
        
        # Test Polygon creation
        polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        print(f"✓ Created Polygon with area: {polygon.area}")
        
        # Test spatial operations
        point2 = Point(0.5, 0.5)
        contains = polygon.contains(point2)
        print(f"✓ Spatial operation (contains): {contains}")
        
        return True
    except Exception as e:
        print(f"✗ GeoDjango test failed: {e}")
        return False


def test_environment_variables():
    """Test environment variables are loaded."""
    print("\nTesting environment variables...")
    try:
        db_name = settings.DATABASES['default']['NAME']
        print(f"✓ Database name: {db_name}")
        
        secret_key = settings.SECRET_KEY
        print(f"✓ Secret key loaded: {'Yes' if secret_key else 'No'}")
        
        debug = settings.DEBUG
        print(f"✓ Debug mode: {debug}")
        
        return True
    except Exception as e:
        print(f"✗ Environment variables test failed: {e}")
        return False


def test_installed_apps():
    """Test required apps are installed."""
    print("\nTesting installed apps...")
    try:
        required_apps = [
            'django.contrib.gis',
            'rest_framework',
        ]
        
        for app in required_apps:
            if app in settings.INSTALLED_APPS:
                print(f"✓ {app} is installed")
            else:
                print(f"✗ {app} is NOT installed")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Installed apps test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Mlimi Wanzeru Setup Verification")
    print("=" * 60)
    
    tests = [
        test_database_connection,
        test_postgis,
        test_geodjango,
        test_environment_variables,
        test_installed_apps,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All tests passed! Setup is complete.")
        print("\nNext steps:")
        print("1. Create Django apps for your features")
        print("2. Define models with spatial fields")
        print("3. Run migrations: python manage.py makemigrations && python manage.py migrate")
        print("4. Start development server: python manage.py runserver")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
