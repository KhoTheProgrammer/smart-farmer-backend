#!/usr/bin/env python
"""
Script to verify soil service implementation.
Demonstrates how to use the SoilService to fetch soil properties.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlimi_wanzeru.settings')
django.setup()

from weather.services import SoilService, SoilServiceError
from weather.models import SoilCache


def test_soil_service():
    """Test the soil service with sample coordinates."""
    print("=" * 60)
    print("Soil Service Verification")
    print("=" * 60)
    
    # Test coordinates (Lilongwe, Malawi)
    lat = -13.9626
    lon = 33.7741
    
    print(f"\nTesting with coordinates: lat={lat}, lon={lon}")
    print("-" * 60)
    
    # Test 1: Coordinate validation
    print("\n1. Testing coordinate validation...")
    if SoilService._validate_coordinates(lat, lon):
        print("   ✓ Coordinates are valid")
    else:
        print("   ✗ Coordinates are invalid")
        return
    
    # Test 2: Check cache
    print("\n2. Checking cache...")
    location_key = SoilCache.create_location_key(lat, lon)
    print(f"   Location key: {location_key}")
    
    cached = SoilCache.get_cached_data(location_key)
    if cached:
        print(f"   ✓ Found cached data (expires: {cached.expires_at})")
        print(f"   Cache data keys: {list(cached.data.keys())}")
    else:
        print("   ℹ No cached data found")
    
    # Test 3: Fetch soil properties (will use cache if available)
    print("\n3. Fetching soil properties...")
    print("   Note: This will attempt to call the SoilGrids API")
    print("   If the API is unavailable, it will use cached data or fail gracefully")
    
    try:
        soil_data = SoilService.fetch_soil_properties(lat, lon)
        print("   ✓ Successfully retrieved soil data")
        
        # Display soil properties
        print("\n   Soil Properties:")
        print(f"   - Clay content: {soil_data.get('clay_content', 'N/A')}%")
        print(f"   - Sand content: {soil_data.get('sand_content', 'N/A')}%")
        print(f"   - pH level: {soil_data.get('ph_level', 'N/A')}")
        print(f"   - Organic carbon: {soil_data.get('organic_carbon', 'N/A')} g/kg")
        
        # Check if using stale cache
        if soil_data.get('_stale_cache'):
            print(f"\n   ⚠ Warning: {soil_data.get('_cache_warning')}")
        
        # Display metadata
        metadata = soil_data.get('metadata', {})
        if metadata:
            print("\n   Metadata:")
            print(f"   - Source: {metadata.get('source', 'N/A')}")
            print(f"   - Depth: {metadata.get('depth', 'N/A')}")
            print(f"   - Fetched at: {metadata.get('fetched_at', 'N/A')}")
        
    except SoilServiceError as e:
        print(f"   ✗ Error fetching soil data: {e}")
        print("   This is expected if the SoilGrids API is unavailable and no cache exists")
    
    # Test 4: Verify cache was created/updated
    print("\n4. Verifying cache...")
    cache_count = SoilCache.objects.count()
    print(f"   Total cached locations: {cache_count}")
    
    cached_after = SoilCache.get_cached_data(location_key)
    if cached_after:
        print(f"   ✓ Cache exists for location {location_key}")
        print(f"   Cache expires at: {cached_after.expires_at}")
    else:
        print(f"   ℹ No cache for location {location_key}")
    
    print("\n" + "=" * 60)
    print("Verification complete!")
    print("=" * 60)


def test_invalid_coordinates():
    """Test error handling with invalid coordinates."""
    print("\n\nTesting error handling with invalid coordinates...")
    print("-" * 60)
    
    invalid_coords = [
        (100, 50, "Latitude out of range"),
        (-100, 50, "Latitude out of range"),
        (0, 200, "Longitude out of range"),
        (0, -200, "Longitude out of range"),
    ]
    
    for lat, lon, reason in invalid_coords:
        try:
            SoilService.fetch_soil_properties(lat, lon)
            print(f"✗ Should have raised error for ({lat}, {lon}) - {reason}")
        except SoilServiceError as e:
            print(f"✓ Correctly rejected ({lat}, {lon}) - {reason}")


if __name__ == "__main__":
    test_soil_service()
    test_invalid_coordinates()
    
    print("\n\nNote: To test with real API calls, ensure you have internet connectivity.")
    print("The SoilGrids API endpoint is: https://rest.isric.org/soilgrids/v2.0/properties/query")
