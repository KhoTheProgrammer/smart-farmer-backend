# Geospatial Data for Malawi

This directory contains administrative boundary and elevation data for Malawi.

## Data Sources

### Malawi Administrative Boundaries

**Source:** Humanitarian Data Exchange (HDX)  
**URL:** https://data.humdata.org/dataset/cod-ab-mwi  
**Format:** GeoJSON or Shapefile  
**License:** Public Domain / Open Data

### Download Instructions

1. Visit the HDX website: https://data.humdata.org/dataset/cod-ab-mwi
2. Download the following files:

   - **Districts (Admin Level 1):** `mwi_admbnda_adm1_nso_20181016.geojson` or similar
   - **Sub-districts/Villages (Admin Level 2 or 3):** `mwi_admbnda_adm2_nso_20181016.geojson` or similar

3. Place the downloaded files in this directory

### Alternative: Convert Shapefiles to GeoJSON

If you download Shapefiles instead of GeoJSON, you can convert them using GDAL:

```bash
# Install GDAL (if not already installed)
# Ubuntu/Debian: sudo apt-get install gdal-bin
# macOS: brew install gdal

# Convert shapefile to GeoJSON
ogr2ogr -f GeoJSON -t_srs EPSG:4326 districts.geojson mwi_admbnda_adm1.shp
ogr2ogr -f GeoJSON -t_srs EPSG:4326 villages.geojson mwi_admbnda_adm2.shp
```

## Import Data

Once you have the GeoJSON files, import them using the Django management command:

```bash
# Import districts only
python manage.py import_boundaries --districts data/districts.geojson

# Import villages only
python manage.py import_boundaries --villages data/villages.geojson

# Import both (recommended)
python manage.py import_boundaries --districts data/districts.geojson --villages data/villages.geojson

# Clear existing data and import fresh
python manage.py import_boundaries --districts data/districts.geojson --villages data/villages.geojson --clear
```

## Data Requirements

### Districts File

- **Geometry Type:** Polygon or MultiPolygon
- **CRS:** WGS84 (EPSG:4326)
- **Required Properties:**
  - `name` or `NAME` or `district` or `DISTRICT` - District name in English
  - `name_chichewa` or `name_local` (optional) - District name in Chichewa

### Villages File

- **Geometry Type:** Point (or Polygon, which will be converted to centroid)
- **CRS:** WGS84 (EPSG:4326)
- **Required Properties:**
  - `name` or `NAME` or `village` or `VILLAGE` - Village name in English
  - `district` or `DISTRICT` or `district_name` - Parent district name
  - `name_chichewa` or `name_local` (optional) - Village name in Chichewa

## Sample Data Structure

### Districts GeoJSON Example

```json
{
  "type": "FeatureCollection",
  "crs": {
    "type": "name",
    "properties": {
      "name": "EPSG:4326"
    }
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Lilongwe",
        "name_chichewa": "Lilongwe"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [33.7, -14.0],
            [34.0, -14.0],
            [34.0, -13.7],
            [33.7, -13.7],
            [33.7, -14.0]
          ]
        ]
      }
    }
  ]
}
```

### Villages GeoJSON Example

```json
{
  "type": "FeatureCollection",
  "crs": {
    "type": "name",
    "properties": {
      "name": "EPSG:4326"
    }
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Kauma",
        "name_chichewa": "Kauma",
        "district": "Lilongwe"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [33.85, -13.85]
      }
    }
  ]
}
```

## Validation

The import command automatically validates:

- ✓ CRS is WGS84 (EPSG:4326)
- ✓ Geometry is valid
- ✓ Required properties are present
- ✓ District-village associations are correct

Any errors or warnings will be displayed during import.

## Troubleshooting

### "District not found" errors when importing villages

- Make sure you import districts before villages
- Check that district names in the villages file match the district names in the districts file
- The import command will attempt to find the district by checking if the village point falls within any district boundary

### "Invalid CRS" errors

- Ensure your GeoJSON files use WGS84 (EPSG:4326)
- If using Shapefiles, convert them with the `-t_srs EPSG:4326` flag as shown above

### "Invalid geometry" errors

- The import command will attempt to fix invalid geometries automatically
- If this fails, you may need to clean the data using QGIS or another GIS tool

---

## Elevation Data (SRTM)

### Data Source

**Source:** OpenTopography  
**URL:** https://opentopography.org/  
**Dataset:** SRTM GL1 (30m resolution)  
**Format:** GeoTIFF  
**License:** Public Domain

### Download Instructions

1. Visit OpenTopography: https://opentopography.org/
2. Go to "Data" → "Global & Regional DEMs"
3. Select "SRTM GL1 (30m)" or "SRTM GL3 (90m)"
4. Draw a bounding box around Malawi (approximately):
   - North: -9.5°
   - South: -17.5°
   - West: 32.5°
   - East: 36.0°
5. Select output format: **GeoTIFF**
6. Leave raster visualization options **unchecked** (we only need raw elevation data)
7. Download the file (will be named something like `rasters_SRTMGL1.tar.gz`)
8. Extract to this directory:
   ```bash
   tar -xzf rasters_SRTMGL1.tar.gz -C data/
   ```

### Import Elevation Data

Once you have the SRTM GeoTIFF file, import elevations for all villages:

```bash
# Import elevation data for villages without elevation
python manage.py import_elevation --raster data/output_SRTMGL1.tif

# Update all villages (including those with existing elevation data)
python manage.py import_elevation --raster data/output_SRTMGL1.tif --update-all

# Use custom batch size for performance tuning
python manage.py import_elevation --raster data/output_SRTMGL1.tif --batch-size 200
```

### Data Requirements

- **Format:** GeoTIFF (.tif)
- **CRS:** WGS84 (EPSG:4326)
- **Resolution:** 30m (SRTM GL1) or 90m (SRTM GL3)
- **Coverage:** Must cover Malawi's extent

### Notes

- The SRTM files are large (300-400MB) and are **not committed to Git**
- Each developer/deployment needs to download the data separately
- Elevation values are stored in the database after import, so the raster file is only needed during initial setup or updates
