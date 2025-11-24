# Importing Elevation Data

This guide explains how to download and import SRTM elevation data for Malawi.

## Overview

The system uses SRTM (Shuttle Radar Topography Mission) elevation data to determine the elevation of village locations. This data is used for crop suitability calculations.

## Data Source

**SRTM Data via USGS EarthExplorer:**

- URL: https://earthexplorer.usgs.gov/
- Resolution: 30m or 90m
- Format: GeoTIFF
- Coverage: Global

**Alternative: CGIAR-CSI SRTM Data:**

- URL: https://srtm.csi.cgiar.org/srtmdata/
- Resolution: 90m
- Format: GeoTIFF
- Easier to download (no account required)

## Malawi Coverage

Malawi is covered by the following SRTM tiles:

- For 90m resolution: Use tiles covering approximately 9°S-17°S, 32°E-36°E
- The country spans roughly from -9.5° to -17.1° latitude and 32.7° to 35.9° longitude

## Download Instructions

### Option 1: CGIAR-CSI (Recommended for quick setup)

1. Visit: https://srtm.csi.cgiar.org/srtmdata/
2. Download the GeoTIFF tiles that cover Malawi
3. If multiple tiles are needed, you can mosaic them using GDAL

### Option 2: USGS EarthExplorer (Higher resolution)

1. Create a free account at https://earthexplorer.usgs.gov/
2. Use the map interface to select the Malawi region
3. Under "Data Sets", select "Digital Elevation > SRTM > SRTM 1 Arc-Second Global" (30m)
4. Search and download the tiles
5. Extract the .tif files from the downloaded archives

## Preparing the Data

If you have multiple tiles, you can mosaic them into a single file:

```bash
# Install GDAL if not already installed
# Ubuntu/Debian: sudo apt-get install gdal-bin
# macOS: brew install gdal

# Mosaic multiple tiles into one file
gdal_merge.py -o malawi_elevation.tif tile1.tif tile2.tif tile3.tif

# Optional: Clip to Malawi boundaries to reduce file size
gdalwarp -cutline malawi_boundary.geojson -crop_to_cutline \
  malawi_elevation.tif malawi_elevation_clipped.tif
```

## Import Command

Once you have the elevation raster file, import it using:

```bash
# Import elevation data for villages without elevation
python manage.py import_elevation --raster path/to/malawi_elevation.tif

# Update all villages (including those with existing elevation data)
python manage.py import_elevation --raster path/to/malawi_elevation.tif --update-all

# Use custom batch size for large datasets
python manage.py import_elevation --raster path/to/malawi_elevation.tif --batch-size 500
```

## Command Options

- `--raster`: Path to the SRTM GeoTIFF file (required)
- `--update-all`: Update all villages, even those with existing elevation data
- `--batch-size`: Number of villages to update in each batch (default: 100)

## Validation

The import command will:

1. Validate that the raster file exists and can be opened
2. Display raster information (size, bands, SRID)
3. Extract elevation for each village location
4. Skip villages outside the raster bounds
5. Skip NoData values
6. Validate that elevations are reasonable for Malawi (-100m to 4000m)
7. Update villages in batches for efficiency

## Expected Output

```
Loading raster file: data/malawi_elevation.tif
Raster info:
  Size: 3600 x 4800
  Bands: 1
  SRID: 4326
  NoData value: -32768.0
Updating elevation for 1234 villages without elevation data
  Updated batch of 100 villages
  Updated batch of 100 villages
  ...

Elevation import complete:
  Updated: 1234
  Skipped (no data): 0
  Errors: 0
```

## Troubleshooting

### "Raster file not found"

- Check that the file path is correct
- Use absolute path if relative path doesn't work

### "Error loading raster file"

- Ensure the file is a valid GeoTIFF
- Check that GDAL is properly installed
- Verify the file isn't corrupted

### "Village is outside raster bounds"

- Your raster doesn't cover all of Malawi
- Download additional tiles or use a larger coverage area

### "NoData value at location"

- Some areas may have missing data in SRTM
- This is normal for water bodies
- Consider using alternative elevation sources for these locations

## Requirements Validated

- **Requirement 3.3**: Elevation data retrieval for user location
- **Requirement 5.3**: Processing SRTM raster files using GDAL
