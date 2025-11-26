# Quick Start Guide

Get the backend API running quickly!

## Prerequisites

- Python 3.10+ installed
- PostgreSQL 14+ with PostGIS installed
- GDAL library installed

## Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create database
psql -U postgres
CREATE DATABASE mlimi_wanzeru;
\c mlimi_wanzeru
CREATE EXTENSION postgis;
\q

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Run migrations
python manage.py migrate

# 6. Start server
python manage.py runserver
```

API available at: <http://localhost:8000/api/>

## Common Commands

```bash
python manage.py runserver          # Start dev server
python manage.py migrate            # Run migrations
python manage.py test               # Run tests
python verify_setup.py              # Verify installation
```

## Import Data

```bash
# Import boundaries (after downloading data)
python manage.py import_boundaries \
    --districts data/malawi_districts.geojson \
    --villages data/malawi_villages.geojson

# Import elevation
python manage.py import_elevation --raster data/output_SRTMGL1.tif
```

## Need Help?

- Read [README.md](./README.md) for detailed setup
- Check [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines
- See [API_README.md](./API_README.md) for API documentation

## Project Structure

```
locations/     # Location models and services
weather/       # Crop models and advisory
mlimi_wanzeru/ # Django settings
```

Happy coding! 🌱
