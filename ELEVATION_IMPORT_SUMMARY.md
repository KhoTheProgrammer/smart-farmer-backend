# Elevation Data Import Summary

## Overview

Successfully imported SRTM elevation data for all villages in Malawi using OpenTopography data source.

## Data Source

- **Provider**: OpenTopography
- **Dataset**: SRTM GL1 (30m resolution)
- **Format**: GeoTIFF
- **File**: `output_SRTMGL1.tif` (352MB)
- **Coverage**: Malawi bounding box (-9.5° to -17.5°, 32.5° to 36.0°)
- **CRS**: WGS84 (EPSG:4326)

## Import Results

- **Total Villages**: 433
- **Successfully Updated**: 433
- **Skipped (no data)**: 0
- **Errors**: 0
- **Success Rate**: 100%

## Sample Elevations

| Location             | Elevation | Notes                                  |
| -------------------- | --------- | -------------------------------------- |
| Karonga Town         | 491m      | Northern region, near Lake Malawi      |
| Mulanje Boma         | 624m      | Southern region, near Mulanje Mountain |
| Zomba Central Ward   | 918m      | Central region, plateau area           |
| Blantyre City Centre | 1000m     | Commercial capital                     |
| Blantyre South Ward  | 1014m     | Southern highlands                     |

## Technical Details

### Import Command

```bash
python manage.py import_elevation --raster data/output_SRTMGL1.tif
```

### Processing

- Batch size: 100 villages per transaction
- Coordinate transformation: Manual calculation using geotransform
- Validation: Elevation range check (-100m to 4000m)
- NoData handling: Automatic detection and skipping

### Code Changes

Fixed GDAL API compatibility issue:

- Changed from `raster.transform.inverse_transform()` (not available)
- To manual calculation using `raster.geotransform` parameters
- File: `locations/management/commands/import_elevation.py`

## Data Management

### Git Repository

Large data files are **NOT** committed to Git:

- ✅ Small sample files (`sample_*.geojson`, `test_*.geojson`)
- ✅ Documentation (`data/README.md`, `IMPORT_SUMMARY.md`)
- ❌ SRTM raster files (`*.tif`, `*.tar.gz`) - 350MB+
- ❌ Boundary data (`malawi_*.geojson`) - 8-48MB each
- ❌ Shapefiles (`*.shp`, `*.dbf`, etc.)

### Download Instructions

Developers must download data separately following instructions in:

- `data/README.md` - Detailed download and import instructions
- `README.md` - Complete setup guide with data import steps
- `SETUP_GUIDE.md` - Quick start guide

## Verification

### Database Check

```bash
python manage.py shell -c "from locations.models import Village; print(f'Villages with elevation: {Village.objects.exclude(elevation__isnull=True).count()}')"
```

Expected output: `Villages with elevation: 433`

### Sample Query

```python
from locations.models import Village

# Get villages with elevation data
villages = Village.objects.exclude(elevation__isnull=True).order_by('elevation')

# Lowest elevation
lowest = villages.first()
print(f"{lowest.name}: {lowest.elevation}m")

# Highest elevation
highest = villages.last()
print(f"{highest.name}: {highest.elevation}m")
```

## API Usage

Elevation data is now available through the API:

```bash
# Get village with elevation
GET /api/locations/villages/1/

# Response includes:
{
  "id": 1,
  "name": "Blantyre City Centre Ward",
  "location": {
    "type": "Point",
    "coordinates": [35.0, -15.7833]
  },
  "elevation": 1000.0,
  "district": {...}
}
```

## Next Steps

1. ✅ Elevation data imported
2. ✅ Documentation updated
3. ✅ Git repository cleaned (large files removed)
4. 🔄 Ready for crop suitability analysis using elevation
5. 🔄 Ready for climate zone classification
6. 🔄 Ready for water drainage analysis

## Notes

- Elevation data is stored in the database, so the raster file is only needed during initial setup or updates
- To update all villages (including those with existing data): `python manage.py import_elevation --raster data/output_SRTMGL1.tif --update-all`
- Elevation values are in meters above sea level
- Data is suitable for agricultural planning and crop suitability analysis

## Date

November 25, 2025
