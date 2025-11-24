#!/usr/bin/env python
"""
Verification script for elevation import functionality.
Tests the import_elevation management command with sample data.
"""

import os
import sys
import django
import numpy as np
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlimi_wanzeru.settings')
django.setup()

from django.contrib.gis.geos import Point
from django.contrib.gis.gdal import GDALRaster, SpatialReference
from locations.models import District, Village


def create_sample_raster(output_path: str) -> None:
    """
    Create a sample SRTM-like raster for testing.
    Covers Malawi's approximate bounds with synthetic elevation data.
    """
    print("Creating sample elevation raster...")
    
    try:
        from osgeo import gdal, osr
    except ImportError:
        print("⚠ GDAL Python bindings not available, skipping raster creation")
        print("  This is expected in development. For production, install GDAL.")
        print("  The import_elevation command will still work with real SRTM data.")
        raise ImportError("GDAL not available")
    
    # Malawi approximate bounds
    min_lon, max_lon = 32.5, 36.0
    min_lat, max_lat = -17.5, -9.0
    
    # Create a small raster (100x100 pixels)
    width, height = 100, 100
    
    # Calculate pixel size
    pixel_width = (max_lon - min_lon) / width
    pixel_height = (max_lat - min_lat) / height
    
    # Create elevation data (simple gradient from 0 to 3000m)
    # This simulates elevation increasing from south to north
    elevation_data = np.zeros((height, width), dtype=np.float32)
    for i in range(height):
        # Elevation increases from bottom (south) to top (north)
        base_elevation = 500 + (i / height) * 2000
        # Add some variation across longitude
        for j in range(width):
            variation = np.sin(j / width * np.pi) * 200
            elevation_data[i, j] = base_elevation + variation
    
    # Create GeoTIFF using GDAL
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(
        output_path,
        width,
        height,
        1,  # Number of bands
        gdal.GDT_Float32
    )
    
    # Set geotransform (defines the raster's position and resolution)
    # Format: [top-left x, pixel width, rotation, top-left y, rotation, pixel height]
    geotransform = [
        min_lon,  # top-left x
        pixel_width,  # pixel width
        0,  # rotation (0 for north-up)
        max_lat,  # top-left y
        0,  # rotation (0 for north-up)
        -pixel_height  # pixel height (negative because y decreases downward)
    ]
    dataset.SetGeoTransform(geotransform)
    
    # Set projection (WGS84)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    dataset.SetProjection(srs.ExportToWkt())
    
    # Write elevation data
    band = dataset.GetRasterBand(1)
    band.WriteArray(elevation_data)
    band.SetNoDataValue(-32768)
    band.FlushCache()
    
    # Close dataset
    dataset = None
    
    print(f"✓ Created sample raster: {output_path}")
    print(f"  Coverage: {min_lon}°E to {max_lon}°E, {min_lat}°N to {max_lat}°N")
    print(f"  Size: {width}x{height} pixels")
    print(f"  Elevation range: 500-2700m")


def create_test_villages() -> None:
    """
    Create test villages if they don't exist.
    """
    print("\nChecking for test villages...")
    
    # Check if we have any villages
    village_count = Village.objects.count()
    
    if village_count == 0:
        print("No villages found. Creating test villages...")
        
        # Create a test district if needed
        district, created = District.objects.get_or_create(
            name="Test District",
            defaults={
                'name_chichewa': "Test District",
                'boundary': Point(34.0, -13.0).buffer(1),  # Simple square boundary
                'centroid': Point(34.0, -13.0)
            }
        )
        
        if created:
            print(f"✓ Created test district: {district.name}")
        
        # Create test villages at various locations in Malawi
        test_locations = [
            ("Lilongwe Village", 33.7875, -13.9833, "Lilongwe"),
            ("Blantyre Village", 35.0085, -15.7861, "Blantyre"),
            ("Mzuzu Village", 34.0150, -11.4500, "Mzuzu"),
            ("Zomba Village", 35.3188, -15.3850, "Zomba"),
            ("Karonga Village", 33.9333, -9.9333, "Karonga"),
        ]
        
        for name, lon, lat, district_name in test_locations:
            village, created = Village.objects.get_or_create(
                name=name,
                district=district,
                defaults={
                    'name_chichewa': name,
                    'location': Point(lon, lat),
                    'elevation': None
                }
            )
            if created:
                print(f"✓ Created test village: {name} at ({lon}, {lat})")
    else:
        print(f"✓ Found {village_count} existing villages")


def verify_elevation_import() -> bool:
    """
    Verify that elevation import works correctly.
    """
    print("\n" + "="*60)
    print("ELEVATION IMPORT VERIFICATION")
    print("="*60)
    
    # Create sample raster
    raster_path = "data/test_elevation.tif"
    os.makedirs("data", exist_ok=True)
    
    try:
        create_sample_raster(raster_path)
    except Exception as e:
        print(f"✗ Failed to create sample raster: {e}")
        return False
    
    # Create test villages
    try:
        create_test_villages()
    except Exception as e:
        print(f"✗ Failed to create test villages: {e}")
        return False
    
    # Get villages without elevation
    villages_before = Village.objects.filter(elevation__isnull=True).count()
    print(f"\nVillages without elevation: {villages_before}")
    
    # Run import command
    print("\nRunning import_elevation command...")
    from django.core.management import call_command
    
    try:
        call_command('import_elevation', raster=raster_path, verbosity=2)
    except Exception as e:
        print(f"✗ Import command failed: {e}")
        return False
    
    # Verify results
    print("\nVerifying results...")
    villages_after = Village.objects.filter(elevation__isnull=True).count()
    villages_with_elevation = Village.objects.filter(elevation__isnull=False).count()
    
    print(f"Villages without elevation after import: {villages_after}")
    print(f"Villages with elevation: {villages_with_elevation}")
    
    if villages_with_elevation > 0:
        # Show some sample elevations
        print("\nSample elevations:")
        for village in Village.objects.filter(elevation__isnull=False)[:5]:
            print(f"  {village.name}: {village.elevation:.1f}m")
        
        # Verify elevation values are reasonable
        elevations = Village.objects.filter(
            elevation__isnull=False
        ).values_list('elevation', flat=True)
        
        min_elev = min(elevations)
        max_elev = max(elevations)
        avg_elev = sum(elevations) / len(elevations)
        
        print(f"\nElevation statistics:")
        print(f"  Min: {min_elev:.1f}m")
        print(f"  Max: {max_elev:.1f}m")
        print(f"  Average: {avg_elev:.1f}m")
        
        # Validate range
        if min_elev < -100 or max_elev > 4000:
            print("✗ Elevation values outside expected range!")
            return False
        
        print("\n" + "="*60)
        print("✓ ELEVATION IMPORT VERIFICATION PASSED")
        print("="*60)
        return True
    else:
        print("✗ No villages were updated with elevation data")
        return False


if __name__ == '__main__':
    try:
        success = verify_elevation_import()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
