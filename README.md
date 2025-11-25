# Mlimi Wanzeru (Smart Farmer)

A location-based agricultural advisory platform for smallholder farmers in Malawi. Provides crop recommendations, planting calendars, and agricultural insights based on location, soil, weather, and elevation data.

## Features

- 🌍 **Location-based Services**: District and village boundary data for all of Malawi
- 🌾 **Crop Recommendations**: Suitability analysis for 15+ Malawian crops
- 📅 **Planting Calendar**: Season-specific planting and harvesting schedules
- 🌡️ **Weather Integration**: Historical weather data via NASA POWER API
- 🗺️ **Elevation Data**: SRTM-based elevation for agricultural planning
- 🌱 **Soil Analysis**: Soil properties via SoilGrids API
- 📊 **RESTful API**: Comprehensive API with interactive documentation

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ with PostGIS extension
- GDAL library (for geospatial data processing)

## Installation

### 1. Install PostgreSQL with PostGIS

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis postgresql-14-postgis-3
```

**macOS (using Homebrew):**

```bash
brew install postgresql postgis
brew services start postgresql
```

**Windows:**

1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Run installer and select PostGIS in the Stack Builder
3. Or download PostGIS separately from https://postgis.net/windows_downloads/

### 2. Install GDAL

**Ubuntu/Debian:**

```bash
sudo apt-get install gdal-bin libgdal-dev python3-gdal
```

**macOS (using Homebrew):**

```bash
brew install gdal
```

**Windows:**

1. Download OSGeo4W installer from https://trac.osgeo.org/osgeo4w/
2. Run installer and select GDAL
3. Or use conda: `conda install -c conda-forge gdal`

### 3. Create Database

**Linux/macOS:**

```bash
# Start PostgreSQL service
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# Create database and enable PostGIS
sudo -u postgres psql
```

**Windows:**

```bash
# PostgreSQL service starts automatically after installation
# Open Command Prompt or PowerShell and run:
psql -U postgres
```

In the PostgreSQL shell:

```sql
CREATE DATABASE mlimi_wanzeru;
\c mlimi_wanzeru
CREATE EXTENSION postgis;
\q
```

### 4. Clone Repository and Setup Python Environment

```bash
# Clone the repository
git clone <repository-url>
cd smart-farmer-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env            # Linux/macOS
copy .env.example .env          # Windows

# Edit .env with your database credentials
# Update these values:
# DB_NAME=mlimi_wanzeru
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
```

### 6. Run Database Migrations

```bash
python manage.py migrate
```

### 7. Download Geospatial Data

The application requires boundary and elevation data. These files are large and not included in the repository.

#### Download Administrative Boundaries

1. Visit: https://data.humdata.org/dataset/cod-ab-mwi
2. Download the shapefile package: `mwi_adm_nso_hotosm_20230405_shp.zip`
3. Extract to the `data/` directory

#### Download Elevation Data (SRTM)

1. Visit: https://opentopography.org/
2. Go to "Data" → "Global & Regional DEMs"
3. Select "SRTM GL1 (30m)"
4. Draw a bounding box around Malawi:
   - North: -9.5°, South: -17.5°
   - West: 32.5°, East: 36.0°
5. Select output format: **GeoTIFF**
6. Leave visualization options unchecked
7. Download and extract to `data/` directory

See `data/README.md` for detailed instructions.

### 8. Import Data into Database

```bash
# Import administrative boundaries (districts and villages)
python manage.py import_boundaries \
    --districts data/malawi_districts.geojson \
    --villages data/malawi_villages.geojson

# Or if using shapefiles, convert first:
ogr2ogr -f GeoJSON -t_srs EPSG:4326 data/malawi_districts.geojson data/mwi_admbnda_adm2_nso_hotosm_20230405.shp
ogr2ogr -f GeoJSON -t_srs EPSG:4326 data/malawi_villages.geojson data/mwi_admbnda_adm3_nso_hotosm_20230405.shp

# Import elevation data for all villages
python manage.py import_elevation --raster data/output_SRTMGL1.tif
```

### 9. Verify Setup

```bash
# Run verification script
python verify_setup.py

# Check that data was imported correctly
python manage.py shell -c "from locations.models import District, Village; print(f'Districts: {District.objects.count()}, Villages: {Village.objects.count()}')"
```

Expected output:

- Districts: 28
- Villages: 400+

### 10. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 11. Run Development Server

```bash
python manage.py runserver
```

The application will be available at:

- **API Root**: http://localhost:8000/api/
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

## API Endpoints

Once the server is running, explore the API:

### Core Endpoints

- `GET /api/` - API root with all available endpoints
- `GET /api/docs/` - Interactive API documentation (Swagger UI)

### Location Endpoints

- `GET /api/locations/districts/` - List all districts
- `GET /api/locations/districts/{id}/` - District details
- `GET /api/locations/villages/` - List all villages
- `GET /api/locations/villages/{id}/` - Village details
- `GET /api/locations/villages/nearby/` - Find nearby villages

### Weather Endpoints

- `GET /api/weather/crops/` - List all crops
- `GET /api/weather/crops/{id}/` - Crop details
- `GET /api/weather/crops/{id}/suitability/` - Crop suitability for location
- `GET /api/weather/planting-calendar/` - Planting calendar for location

### Query Parameters

Most endpoints support filtering:

```bash
# Find villages in a specific district
GET /api/locations/villages/?district=Lilongwe

# Find nearby villages (within 10km)
GET /api/locations/villages/nearby/?lat=-13.9833&lon=33.7833&radius=10

# Get crop suitability for a location
GET /api/weather/crops/1/suitability/?lat=-13.9833&lon=33.7833

# Get planting calendar for a location and season
GET /api/weather/planting-calendar/?lat=-13.9833&lon=33.7833&season=rainy
```

See `API_README.md` for complete API documentation.

## Project Structure

```
smart-farmer-backend/
├── mlimi_wanzeru/              # Django project settings
│   ├── settings.py             # Main settings with GeoDjango config
│   ├── urls.py                 # URL routing
│   ├── api_docs.py             # API documentation config
│   └── wsgi.py                 # WSGI application
├── locations/                  # Location app (districts, villages)
│   ├── models.py               # District and Village models
│   ├── views.py                # API views
│   ├── serializers.py          # DRF serializers
│   ├── services.py             # Business logic (elevation, soil)
│   └── management/commands/    # Import commands
│       ├── import_boundaries.py
│       └── import_elevation.py
├── weather/                    # Weather/crop app
│   ├── models.py               # Crop and PlantingCalendar models
│   ├── views.py                # API views
│   ├── serializers.py          # DRF serializers
│   ├── services.py             # Weather and soil services
│   └── migrations/
│       └── 0004_add_malawian_crops.py
├── data/                       # Geospatial data (not in Git)
│   ├── README.md               # Data download instructions
│   ├── sample_*.geojson        # Sample data for testing
│   └── test_*.geojson          # Test fixtures
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
├── verify_setup.py             # Setup verification script
├── verify_crops.py             # Crop data verification
├── test_api_endpoints.py       # API endpoint tests
└── README.md                   # This file
```

## Technology Stack

- **Backend:** Django 4.2 with GeoDjango
- **Database:** PostgreSQL 14+ with PostGIS 3.x
- **API Framework:** Django REST Framework 3.14
- **API Documentation:** drf-spectacular (OpenAPI 3.0)
- **Geospatial:** GDAL, GeoDjango, PostGIS
- **Testing:** Hypothesis (property-based testing)

## External APIs

- **NASA POWER API:** Historical weather data (temperature, rainfall)
- **SoilGrids API:** Soil properties (pH, organic carbon, texture)

## Data Sources

- **Administrative Boundaries:** Humanitarian Data Exchange (HDX)
- **Elevation Data:** SRTM via OpenTopography
- **Crop Data:** Malawi Ministry of Agriculture guidelines
- **Planting Calendar:** Local agricultural extension services

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test locations
python manage.py test weather

# Run verification scripts
python verify_setup.py
python verify_crops.py
python test_api_endpoints.py
```

### Database Management

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (careful!)
python manage.py flush

# Re-import data
python manage.py import_boundaries --districts data/malawi_districts.geojson --villages data/malawi_villages.geojson --clear
python manage.py import_elevation --raster data/output_SRTMGL1.tif --update-all
```

## Troubleshooting

### GDAL Installation Issues

If you encounter GDAL-related errors:

**Linux:**

```bash
sudo apt-get install libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL==$(gdal-config --version)
```

**macOS:**

```bash
brew install gdal
pip install GDAL==$(gdal-config --version)
```

**Windows:**
Use OSGeo4W or conda to install GDAL, then install the matching Python bindings.

### PostGIS Extension Error

If you get "PostGIS extension not found":

```sql
-- Connect to your database
\c mlimi_wanzeru

-- Enable PostGIS
CREATE EXTENSION postgis;

-- Verify installation
SELECT PostGIS_version();
```

### Data Import Errors

If boundary or elevation import fails:

1. Check that files exist in `data/` directory
2. Verify file format (GeoJSON for boundaries, GeoTIFF for elevation)
3. Ensure CRS is WGS84 (EPSG:4326)
4. Check `data/README.md` for detailed instructions

## Contributing

This is an educational project. For questions or issues, please contact the development team.

## License

Educational project for geospatial computing class.
