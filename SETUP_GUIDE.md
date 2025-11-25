# Quick Setup Guide

This is a condensed setup guide. For detailed instructions, see [README.md](README.md).

## Quick Start (All Platforms)

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14+ with PostGIS
- GDAL library

### 2. Database Setup

```bash
# Create database (in psql)
CREATE DATABASE mlimi_wanzeru;
\c mlimi_wanzeru
CREATE EXTENSION postgis;
\q
```

### 3. Python Environment

```bash
# Clone and setup
git clone <repository-url>
cd smart-farmer-backend
python -m venv venv

# Activate (choose your platform)
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration

```bash
# Copy and edit .env file
cp .env.example .env            # Linux/macOS
copy .env.example .env          # Windows

# Edit .env with your database credentials
```

### 5. Database Migration

```bash
python manage.py migrate
```

### 6. Download Data

**Administrative Boundaries:**

- Visit: https://data.humdata.org/dataset/cod-ab-mwi
- Download: `mwi_adm_nso_hotosm_20230405_shp.zip`
- Extract to `data/` directory

**Elevation Data:**

- Visit: https://opentopography.org/
- Select: SRTM GL1 (30m)
- Bounding box: Malawi (-9.5° to -17.5°, 32.5° to 36.0°)
- Format: GeoTIFF
- Extract to `data/` directory

### 7. Import Data

```bash
# Convert shapefiles to GeoJSON (if needed)
ogr2ogr -f GeoJSON -t_srs EPSG:4326 data/malawi_districts.geojson data/mwi_admbnda_adm2_nso_hotosm_20230405.shp
ogr2ogr -f GeoJSON -t_srs EPSG:4326 data/malawi_villages.geojson data/mwi_admbnda_adm3_nso_hotosm_20230405.shp

# Import boundaries
python manage.py import_boundaries \
    --districts data/malawi_districts.geojson \
    --villages data/malawi_villages.geojson

# Import elevation
python manage.py import_elevation --raster data/output_SRTMGL1.tif
```

### 8. Verify Setup

```bash
python verify_setup.py
```

### 9. Run Server

```bash
python manage.py runserver
```

Visit:

- API: http://localhost:8000/api/
- Docs: http://localhost:8000/api/docs/

## Platform-Specific Notes

### Windows

- Use PowerShell or Command Prompt
- PostgreSQL service starts automatically
- Use `copy` instead of `cp`
- Use `venv\Scripts\activate` for virtual environment
- Install GDAL via OSGeo4W or conda

### macOS

- Use Homebrew for dependencies: `brew install postgresql postgis gdal`
- Start PostgreSQL: `brew services start postgresql`

### Linux (Ubuntu/Debian)

- Install packages: `sudo apt-get install postgresql postgis gdal-bin libgdal-dev`
- Start PostgreSQL: `sudo service postgresql start`

## Expected Results

After successful setup:

- **Districts**: 28
- **Villages**: 400+
- **Crops**: 15+
- **Planting Calendar Entries**: 30+

## Troubleshooting

### GDAL Issues

```bash
# Linux
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL==$(gdal-config --version)

# macOS
brew install gdal
pip install GDAL==$(gdal-config --version)

# Windows
# Use OSGeo4W or: conda install -c conda-forge gdal
```

### PostGIS Not Found

```sql
-- In psql
\c mlimi_wanzeru
CREATE EXTENSION postgis;
SELECT PostGIS_version();
```

### Import Errors

- Check files exist in `data/` directory
- Verify CRS is EPSG:4326
- See `data/README.md` for details

## Next Steps

1. Create superuser: `python manage.py createsuperuser`
2. Explore API docs: http://localhost:8000/api/docs/
3. Test endpoints: `python test_api_endpoints.py`
4. Read full documentation: [README.md](README.md) and [API_README.md](API_README.md)
