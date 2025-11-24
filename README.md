# Mlimi Wanzeru (Smart Farmer)

A location-based agricultural advisory platform for smallholder farmers in Malawi.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ with PostGIS extension
- GDAL library

## Setup Instructions

### 1. Install PostgreSQL with PostGIS

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis
```

**macOS (using Homebrew):**

```bash
brew install postgresql postgis
```

### 2. Create Database

```bash
# Start PostgreSQL service
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# Create database and enable PostGIS
sudo -u postgres psql
```

In the PostgreSQL shell:

```sql
CREATE DATABASE mlimi_wanzeru;
\c mlimi_wanzeru
CREATE EXTENSION postgis;
\q
```

### 3. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The application will be available at http://localhost:8000

## Project Structure

```
mlimi_wanzeru/
├── mlimi_wanzeru/          # Django project settings
│   ├── settings.py         # Main settings with GeoDjango config
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI application
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Technology Stack

- **Backend:** Django 4.2 with GeoDjango
- **Database:** PostgreSQL with PostGIS extension
- **API Framework:** Django REST Framework
- **Testing:** Hypothesis (property-based testing)

## External APIs

- **NASA POWER API:** Historical weather data
- **SoilGrids API:** Soil properties data

## License

Educational project for geospatial computing class.
