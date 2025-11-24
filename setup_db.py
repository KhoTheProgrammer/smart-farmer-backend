#!/usr/bin/env python
"""
Database setup script for Mlimi Wanzeru
Creates PostgreSQL database and enables PostGIS extension
"""

import os
import sys
import subprocess
from decouple import config


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"{description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("=" * 50)
    print("Mlimi Wanzeru Database Setup")
    print("=" * 50)
    
    # Load environment variables
    try:
        db_name = config('DB_NAME', default='mlimi_wanzeru')
        db_user = config('DB_USER', default='postgres')
        print(f"\nDatabase name: {db_name}")
        print(f"Database user: {db_user}")
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
        print("Using default values...")
        db_name = 'mlimi_wanzeru'
        db_user = 'postgres'
    
    # Check if PostgreSQL is running
    print("\nChecking PostgreSQL status...")
    if not run_command("pg_isready", "Checking PostgreSQL"):
        print("\nError: PostgreSQL is not running.")
        print("Please start PostgreSQL first:")
        print("  Linux: sudo service postgresql start")
        print("  macOS: brew services start postgresql")
        sys.exit(1)
    
    print("✓ PostgreSQL is running")
    
    # Create database
    create_db_cmd = f'sudo -u {db_user} psql -c "CREATE DATABASE {db_name};"'
    if sys.platform == 'darwin':  # macOS
        create_db_cmd = f'psql -U {db_user} -c "CREATE DATABASE {db_name};"'
    
    print(f"\nCreating database: {db_name}")
    run_command(create_db_cmd, "Creating database")
    
    # Enable PostGIS extension
    enable_postgis_cmd = f'sudo -u {db_user} psql -d {db_name} -c "CREATE EXTENSION IF NOT EXISTS postgis;"'
    if sys.platform == 'darwin':  # macOS
        enable_postgis_cmd = f'psql -U {db_user} -d {db_name} -c "CREATE EXTENSION IF NOT EXISTS postgis;"'
    
    if run_command(enable_postgis_cmd, "Enabling PostGIS extension"):
        print("✓ PostGIS extension enabled")
    
    # Verify PostGIS installation
    verify_cmd = f'sudo -u {db_user} psql -d {db_name} -c "SELECT PostGIS_version();"'
    if sys.platform == 'darwin':  # macOS
        verify_cmd = f'psql -U {db_user} -d {db_name} -c "SELECT PostGIS_version();"'
    
    if run_command(verify_cmd, "Verifying PostGIS installation"):
        print("✓ PostGIS is working correctly")
    
    print("\n" + "=" * 50)
    print("Database setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run migrations: python manage.py migrate")
    print("2. Create superuser: python manage.py createsuperuser")
    print("3. Start server: python manage.py runserver")


if __name__ == '__main__':
    main()
