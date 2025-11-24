# Mlimi Wanzeru Project Structure

## Current Setup Status

✅ Django project created with GeoDjango configuration
✅ PostgreSQL database created with PostGIS extension
✅ Environment variables configured
✅ Initial migrations applied
✅ All components verified and working

## Directory Structure

```
smart-farmer-backend/
├── .kiro/                          # Kiro specs directory
│   └── specs/
│       └── smart-farmer-platform/
│           ├── design.md           # Design document
│           ├── requirements.md     # Requirements document
│           └── tasks.md            # Implementation tasks
│
├── mlimi_wanzeru/                  # Django project directory
│   ├── __init__.py
│   ├── settings.py                 # Project settings (GeoDjango configured)
│   ├── urls.py                     # URL routing
│   ├── wsgi.py                     # WSGI application
│   └── asgi.py                     # ASGI application
│
├── venv/                           # Virtual environment
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not in git)
├── .env.example                    # Example environment variables
├── .gitignore                      # Git ignore file
├── setup_db.sh                     # Database setup script (bash)
├── setup_db.py                     # Database setup script (Python)
├── verify_setup.py                 # Setup verification script
├── README.md                       # Project documentation
└── PROJECT_STRUCTURE.md            # This file
```

## Database Configuration

- **Database Name:** mlimi_wanzeru
- **Database Engine:** PostgreSQL with PostGIS 3.4
- **User:** postgres
- **Host:** localhost
- **Port:** 5432

## Installed Python Packages

- Django 4.2.26
- djangorestframework 3.16.1
- psycopg2-binary 2.9.11 (PostgreSQL adapter)
- python-decouple 3.8 (environment variables)
- requests 2.32.5 (HTTP library)
- hypothesis 6.148.2 (property-based testing)

## GeoDjango Configuration

The project is configured to use GeoDjango with the following settings:

- **Database Backend:** `django.contrib.gis.db.backends.postgis`
- **Spatial Reference System:** WGS84 (EPSG:4326)
- **PostGIS Version:** 3.4

## Environment Variables

See `.env.example` for all available environment variables:

- Database configuration (DB_NAME, DB_USER, DB_PASSWORD, etc.)
- API keys (NASA_POWER_API_KEY, SOILGRIDS_API_KEY)
- Django settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)

## Verification

Run the verification script to ensure everything is set up correctly:

```bash
venv/bin/python verify_setup.py
```

This will test:

- Database connection
- PostGIS extension
- GeoDjango functionality
- Environment variables
- Installed apps

## Next Steps

According to the implementation plan in `.kiro/specs/smart-farmer-platform/tasks.md`:

1. ✅ Task 1: Set up project infrastructure and database (COMPLETED)
2. ⏭️ Task 2: Implement location models and services
3. ⏭️ Task 3: Import administrative boundary data
4. ⏭️ Task 4: Implement weather data integration
5. ... (see tasks.md for full list)

## Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS

# Run Django development server
venv/bin/python manage.py runserver

# Create migrations
venv/bin/python manage.py makemigrations

# Apply migrations
venv/bin/python manage.py migrate

# Create superuser
venv/bin/python manage.py createsuperuser

# Django shell
venv/bin/python manage.py shell

# Run tests
venv/bin/python manage.py test

# Check for issues
venv/bin/python manage.py check
```

## API Endpoints (To Be Implemented)

See design.md for the complete API specification. Key endpoints include:

- `/api/locations/districts/` - List all districts
- `/api/locations/villages/` - List villages
- `/api/advisory/planting-calendar/` - Get planting windows
- `/api/advisory/crop-suitability/` - Get crop recommendations
- `/api/advisory/crop-suitability-map/` - Get map data

## Testing Strategy

The project uses both unit testing and property-based testing:

- **Unit Tests:** Django's built-in test framework
- **Property-Based Tests:** Hypothesis library (configured for 100+ iterations)

See design.md for the complete testing strategy.
