# Quick Start: Elevation Data Import

## TL;DR

```bash
# 1. Download SRTM data for Malawi from https://srtm.csi.cgiar.org/srtmdata/
# 2. Place the .tif file in the data/ directory
# 3. Run the import command
python manage.py import_elevation --raster data/malawi_elevation.tif
```

## What You Need

1. **SRTM elevation data** covering Malawi (9°S-17°S, 32°E-36°E)

   - Format: GeoTIFF (.tif)
   - Resolution: 30m or 90m
   - CRS: WGS84 (EPSG:4326)

2. **Villages imported** in the database
   - Run `python manage.py import_boundaries --villages <file>` first if needed

## Quick Download (CGIAR-CSI)

1. Go to: https://srtm.csi.cgiar.org/srtmdata/
2. Download tiles that cover Malawi:
   - Look for tiles around 9°S-17°S latitude
   - And 32°E-36°E longitude
3. Save to `data/` directory

## Import Command

```bash
# Basic import (updates villages without elevation)
python manage.py import_elevation --raster data/malawi_elevation.tif

# Update all villages (including those with existing elevation)
python manage.py import_elevation --raster data/malawi_elevation.tif --update-all

# Large datasets (adjust batch size)
python manage.py import_elevation --raster data/malawi_elevation.tif --batch-size 500
```

## Verify Import

```bash
# Check how many villages have elevation
python manage.py shell
>>> from locations.models import Village
>>> Village.objects.filter(elevation__isnull=False).count()
```

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

**"Raster file not found"**

- Check the file path is correct
- Use absolute path: `/full/path/to/file.tif`

**"Village is outside raster bounds"**

- Your raster doesn't cover all of Malawi
- Download additional tiles

**"NoData value at location"**

- Some areas have missing data (water bodies)
- This is normal, those villages will be skipped

## Next Steps

After importing elevation data:

1. Create crop database (Task 9)
2. Calculate crop suitability (Task 10)

## Full Documentation

See `docs/IMPORT_ELEVATION.md` for complete documentation.
