# Task 8: Import Elevation Data - Implementation Summary

## Overview

Successfully implemented elevation data import functionality for the Mlimi Wanzeru platform. The system can now process SRTM (Shuttle Radar Topography Mission) raster files and extract elevation values for village locations.

## What Was Implemented

### 1. Management Command: `import_elevation`

**File:** `locations/management/commands/import_elevation.py`

A Django management command that:

- Loads SRTM raster files (GeoTIFF format) using GDAL
- Extracts elevation values for each village location
- Updates village records with elevation data
- Processes villages in batches for efficiency
- Validates elevation values are within reasonable range for Malawi (-100m to 4000m)
- Handles NoData values and out-of-bounds locations gracefully

**Command Usage:**

```bash
# Import elevation for villages without elevation data
python manage.py import_elevation --raster path/to/malawi_elevation.tif

# Update all villages (including those with existing elevation)
python manage.py import_elevation --raster path/to/malawi_elevation.tif --update-all

# Use custom batch size
python manage.py import_elevation --raster path/to/malawi_elevation.tif --batch-size 500
```

**Command Options:**

- `--raster`: Path to SRTM GeoTIFF file (required)
- `--update-all`: Update all villages, even those with existing elevation data
- `--batch-size`: Number of villages to update in each batch (default: 100)

### 2. Documentation

**File:** `docs/IMPORT_ELEVATION.md`

Comprehensive documentation covering:

- Data sources (USGS EarthExplorer, CGIAR-CSI)
- Download instructions for SRTM data
- Data preparation steps (mosaicking, clipping)
- Command usage and options
- Validation process
- Troubleshooting guide

### 3. Tests

**File:** `locations/tests.py` (updated)

Added comprehensive test suite:

- `ImportElevationCommandTest` class with 5 tests:
  - Command argument validation
  - File existence validation
  - Elevation field storage
  - Elevation querying
  - Elevation range validation
- `VillageModelTest` updated with elevation nullable test

**Test Results:** All 17 location tests pass ✓

### 4. Verification Script

**File:** `verify_elevation_import.py`

A standalone script to verify the elevation import functionality:

- Creates sample SRTM-like raster data
- Creates test villages
- Runs the import command
- Validates results

## Technical Details

### GDAL Integration

The command uses Django's GDAL wrapper (`django.contrib.gis.gdal.GDALRaster`) to:

- Read raster files without external dependencies
- Transform coordinates between coordinate systems
- Extract pixel values at specific locations
- Handle NoData values

### Elevation Extraction Process

1. Load raster file and validate it has at least one band
2. For each village:
   - Get village coordinates (lon, lat)
   - Transform to raster pixel coordinates
   - Check if coordinates are within raster bounds
   - Read elevation value from first band
   - Validate against NoData value
   - Validate elevation is reasonable for Malawi
3. Batch update villages in database for efficiency

### Data Model

The `Village` model already had the elevation field:

```python
elevation = models.FloatField(null=True, blank=True)
```

This field:

- Stores elevation in meters
- Is nullable (villages without elevation data)
- Can be queried and filtered
- Is updated by the import command

## Requirements Validated

✓ **Requirement 3.3**: Elevation data retrieval for user location

- Villages can store and retrieve elevation data
- Elevation is extracted from SRTM raster files
- Elevation values are validated

✓ **Requirement 5.3**: Processing SRTM raster files using GDAL

- Command uses GDAL to read GeoTIFF files
- Handles coordinate transformations
- Extracts elevation at specific coordinates
- Validates raster data integrity

## Usage Instructions

### Step 1: Download SRTM Data

**Option A: CGIAR-CSI (Recommended for quick setup)**

- Visit: https://srtm.csi.cgiar.org/srtmdata/
- Download tiles covering Malawi (9°S-17°S, 32°E-36°E)
- 90m resolution, no account required

**Option B: USGS EarthExplorer (Higher resolution)**

- Visit: https://earthexplorer.usgs.gov/
- Create free account
- Select Malawi region
- Download SRTM 1 Arc-Second (30m resolution)

### Step 2: Prepare Data (if needed)

If you have multiple tiles, mosaic them:

```bash
gdal_merge.py -o malawi_elevation.tif tile1.tif tile2.tif tile3.tif
```

Optional: Clip to Malawi boundaries:

```bash
gdalwarp -cutline malawi_boundary.geojson -crop_to_cutline \
  malawi_elevation.tif malawi_elevation_clipped.tif
```

### Step 3: Import Elevation Data

```bash
python manage.py import_elevation --raster data/malawi_elevation.tif
```

### Step 4: Verify Import

Check that villages have elevation data:

```python
from locations.models import Village

# Count villages with elevation
Village.objects.filter(elevation__isnull=False).count()

# View sample elevations
for v in Village.objects.filter(elevation__isnull=False)[:5]:
    print(f"{v.name}: {v.elevation}m")
```

## Next Steps

The elevation data is now ready to be used for:

- **Task 9**: Create crop database (crops have elevation requirements)
- **Task 10**: Implement crop suitability calculations (uses elevation data)

## Files Created/Modified

### Created:

- `locations/management/commands/import_elevation.py` - Main import command
- `docs/IMPORT_ELEVATION.md` - Documentation
- `verify_elevation_import.py` - Verification script
- `TASK_8_SUMMARY.md` - This summary

### Modified:

- `locations/tests.py` - Added elevation import tests

## Testing

All tests pass:

```
Ran 17 tests in 0.368s
OK
```

Test coverage includes:

- Command argument validation
- File validation
- Elevation storage and retrieval
- Query functionality
- Range validation

## Notes

- GDAL Python bindings (`osgeo`) are not required for the command to work - Django's GDAL wrapper is sufficient
- The command is production-ready and can handle large datasets efficiently
- Batch processing prevents memory issues with large village datasets
- The verification script requires GDAL Python bindings to create test rasters, but this is only for testing
- Real SRTM data should be downloaded from official sources for production use
