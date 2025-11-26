# Mlimi Wanzeru - Backend API

A Django-based REST API providing location-based agricultural advisory services for smallholder farmers in Malawi.

## 🌾 About

This backend API provides:

- **Location Services** - District and village boundary data for all of Malawi
- **Crop Information** - Database of 15+ Malawian crops with growing requirements
- **Planting Calendar** - Season-specific planting and harvesting schedules
- **Crop Suitability Analysis** - Recommendations based on location, soil, weather, and elevation
- **Weather Data** - Historical weather data via NASA POWER API
- **Soil Analysis** - Soil properties via SoilGrids API
- **Elevation Data** - SRTM-based elevation for agricultural planning

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10 or higher
- **PostgreSQL** 14+ with PostGIS extension
- **GDAL** library for geospatial data processing

### Installation

#### 1. Install PostgreSQL with PostGIS

**Windows:**

1. Download PostgreSQL from <https://www.postgresql.org/download/windows/>
2. Run installer and select PostGIS in Stack Builder
3. Or download PostGIS separately from <https://postgis.net/windows_downloads/>

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis postgresql-14-postgis-3
sudo service postgresql start
```

**macOS:**

```bash
brew install postgresql postgis
brew services start postgresql
```

#### 2. Install GDAL

**Windows:**

1. Download OSGeo4W from <https://trac.osgeo.org/osgeo4w/>
2. Run installer and select GDAL
3. Or use conda: `conda install -c conda-forge gdal`

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install gdal-bin libgdal-dev python3-gdal
```

**macOS:**

```bash
brew install gdal
```

#### 3. Create Database

**Windows (PowerShell/CMD):**

```powershell
# PostgreSQL service starts automatically
psql -U postgres
```

**Linux/macOS:**

```bash
sudo -u postgres psql
```

In the PostgreSQL shell:

```sql
CREATE DATABASE mlimi_wanzeru;
\c mlimi_wanzeru
CREATE EXTENSION postgis;
\q
```

#### 4. Setup Python Environment

**Windows:**

```powershell
# Clone repository
git clone <repository-url>
cd smart-farmer-backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Linux/macOS:**

```bash
# Clone repository
git clone <repository-url>
cd smart-farmer-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 5. Configure Environment Variables

**Windows:**

```powershell
copy .env.example .env
notepad .env
```

**Linux/macOS:**

```bash
cp .env.example .env
nano .env
```

Edit `.env` with your database credentials:

```env
# Database Configuration
DB_NAME=mlimi_wanzeru
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# External APIs (optional - have defaults)
NASA_POWER_API_URL=https://power.larc.nasa.gov/api/temporal/daily/point
```

**Important Environment Variables:**

- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - PostgreSQL credentials (required)
- `SECRET_KEY` - Django secret key (required for production)
- `DEBUG` - Set to `False` in production
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts in production

#### 6. Run Migrations

```bash
python manage.py migrate
```

#### 7. Download Geospatial Data

The application requires boundary and elevation data. These files are large and not included in the repository.

**Download Administrative Boundaries:**

1. Visit: <https://data.humdata.org/dataset/cod-ab-mwi>
2. Download: `mwi_adm_nso_hotosm_20230405_shp.zip`
3. Extract to the `data/` directory

**Download Elevation Data (SRTM):**

1. Visit: <https://opentopography.org/>
2. Go to "Data" → "Global & Regional DEMs"
3. Select "SRTM GL1 (30m)"
4. Draw bounding box around Malawi:
   - North: -9.5°, South: -17.5°
   - West: 32.5°, East: 36.0°
5. Select output format: **GeoTIFF**
6. Download and extract to `data/` directory

See `data/README.md` for detailed instructions.

#### 8. Import Data

**Convert shapefiles to GeoJSON (if needed):**

```bash
# Install ogr2ogr (comes with GDAL)
ogr2ogr -f GeoJSON -t_srs EPSG:4326 data/malawi_districts.geojson data/mwi_admbnda_adm2_nso_hotosm_20230405.shp
ogr2ogr -f GeoJSON -t_srs EPSG:4326 data/malawi_villages.geojson data/mwi_admbnda_adm3_nso_hotosm_20230405.shp
```

**Import boundaries:**

```bash
python manage.py import_boundaries \
    --districts data/malawi_districts.geojson \
    --villages data/malawi_villages.geojson
```

**Import elevation data:**

```bash
python manage.py import_elevation --raster data/output_SRTMGL1.tif
```

#### 9. Verify Setup

```bash
python verify_setup.py
```

Expected output:

- Districts: 28
- Villages: 400+
- Crops: 15+

#### 10. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

#### 11. Start Development Server

```bash
python manage.py runserver
```

The API will be available at:

- **API Root**: <http://localhost:8000/api/>
- **API Documentation**: <http://localhost:8000/api/docs/>
- **Admin Panel**: <http://localhost:8000/admin/>

## 📁 Project Structure

```
smart-farmer-backend/
├── mlimi_wanzeru/              # Django project settings
│   ├── settings.py             # Main settings with GeoDjango
│   ├── urls.py                 # URL routing
│   ├── api_docs.py             # API documentation config
│   └── wsgi.py                 # WSGI application
│
├── locations/                  # Location app
│   ├── models.py               # District and Village models
│   ├── views.py                # API views
│   ├── serializers.py          # DRF serializers
│   ├── services.py             # Elevation and soil services
│   └── management/commands/    # Data import commands
│       ├── import_boundaries.py
│       └── import_elevation.py
│
├── weather/                    # Weather and crop app
│   ├── models.py               # Crop and PlantingCalendar models
│   ├── views.py                # API views
│   ├── serializers.py          # DRF serializers
│   ├── services.py             # Weather and soil services
│   └── migrations/
│       └── 0004_add_malawian_crops.py
│
├── data/                       # Geospatial data (not in Git)
│   ├── README.md               # Data download instructions
│   └── sample_*.geojson        # Sample data for testing
│
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
├── verify_setup.py             # Setup verification script
├── test_api_endpoints.py       # API endpoint tests
└── README.md                   # This file
```

## 🔌 API Endpoints

### Core Endpoints

- `GET /api/` - API root with all available endpoints
- `GET /api/docs/` - Interactive API documentation (Swagger UI)
- `GET /api/schema/` - OpenAPI 3.0 schema

### Location Endpoints

```
GET  /api/locations/districts/              # List all districts
GET  /api/locations/districts/{id}/         # District details
GET  /api/locations/districts/{id}/villages/ # Villages in district
GET  /api/locations/villages/               # List all villages
GET  /api/locations/villages/{id}/          # Village details
GET  /api/locations/villages/nearby/        # Find nearby villages
```

### Crop Endpoints

```
GET  /api/weather/crops/                    # List all crops
GET  /api/weather/crops/{id}/               # Crop details
GET  /api/weather/crops/{id}/suitability/   # Crop suitability analysis
```

### Advisory Endpoints

```
GET  /api/weather/planting-calendar/        # Planting calendar for location
```

### Query Parameters

**Location-based queries:**

```bash
# Find villages in a district
GET /api/locations/villages/?district=Lilongwe

# Find nearby villages (within 10km)
GET /api/locations/villages/nearby/?lat=-13.9833&lon=33.7833&radius=10

# Get crop suitability for a location
GET /api/weather/crops/1/suitability/?lat=-13.9833&lon=33.7833

# Get planting calendar
GET /api/weather/planting-calendar/?lat=-13.9833&lon=33.7833&season=rainy
```

See [API_README.md](./API_README.md) for complete API documentation with examples.

## 🛠️ Technology Stack

- **Framework**: Django 4.2 with GeoDjango
- **Database**: PostgreSQL 14+ with PostGIS 3.x
- **API**: Django REST Framework 3.14
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Geospatial**: GDAL, GeoDjango, PostGIS
- **Testing**: Django TestCase, Hypothesis

## 🌐 External APIs

- **NASA POWER API**: Historical weather data (temperature, rainfall)
- **SoilGrids API**: Soil properties (pH, organic carbon, texture)

No API keys required for these services.

## 🧪 Testing

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

## 🐛 Troubleshooting

### GDAL Installation Issues

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

Use OSGeo4W or conda to install GDAL, then install matching Python bindings.

### PostGIS Extension Error

```sql
-- Connect to database
\c mlimi_wanzeru

-- Enable PostGIS
CREATE EXTENSION postgis;

-- Verify
SELECT PostGIS_version();
```

### Database Connection Error

1. Check PostgreSQL is running
2. Verify credentials in `.env` file
3. Ensure database exists: `psql -U postgres -l`
4. Check `DATABASES` configuration in `settings.py`

### Data Import Errors

1. Verify files exist in `data/` directory
2. Check file format (GeoJSON for boundaries, GeoTIFF for elevation)
3. Ensure CRS is WGS84 (EPSG:4326)
4. See `data/README.md` for detailed instructions

### "ModuleNotFoundError: No module named 'osgeo'"

GDAL is not installed or not in Python path. Reinstall GDAL Python bindings.

## 🚀 Production Deployment

### Security Checklist

1. Set `DEBUG=False` in `.env`
2. Generate strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` with your domain
4. Use environment variables for sensitive data
5. Enable HTTPS
6. Configure CORS properly
7. Use a production database with backups

### Recommended Setup

- **Web Server**: Nginx or Apache
- **WSGI Server**: Gunicorn or uWSGI
- **Database**: PostgreSQL with regular backups
- **Static Files**: WhiteNoise or CDN
- **Monitoring**: Sentry for error tracking

### Example Gunicorn Command

```bash
gunicorn mlimi_wanzeru.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 📖 Additional Documentation

- [API_README.md](./API_README.md) - Complete API reference
- [data/README.md](./data/README.md) - Data download and import guide
- Django Documentation: <https://docs.djangoproject.com/>
- GeoDjango Documentation: <https://docs.djangoproject.com/en/4.2/ref/contrib/gis/>
- PostGIS Documentation: <https://postgis.net/documentation/>

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Commit with clear messages
6. Push and create a pull request

## 📄 License

Educational project for agricultural development in Malawi.

## 🙏 Acknowledgments

- Malawi Ministry of Agriculture for crop guidelines
- Humanitarian Data Exchange for boundary data
- NASA POWER for weather data
- ISRIC for SoilGrids data
- OpenTopography for elevation data

---

**Built with ❤️ for Malawian farmers**
