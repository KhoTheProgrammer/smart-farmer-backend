#!/usr/bin/env python
"""
Verification script for crop database.
Validates that all Malawian crops have been added correctly.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlimi_wanzeru.settings')
django.setup()

from weather.models import Crop


def verify_crops():
    """Verify that all expected crops are in the database."""
    print("=" * 60)
    print("CROP DATABASE VERIFICATION")
    print("=" * 60)
    
    expected_crops = [
        'Maize',
        'Tobacco', 
        'Groundnuts',
        'Beans',
        'Cassava',
        'Sweet Potato'
    ]
    
    expected_chichewa = [
        'Chimanga',
        'Fodya',
        'Mtedza',
        'Nyemba',
        'Chinangwa',
        'Mbatata'
    ]
    
    # Get all crops
    crops = Crop.objects.all()
    crop_count = crops.count()
    
    print(f"\nTotal crops in database: {crop_count}")
    print(f"Expected crops: {len(expected_crops)}")
    
    if crop_count == 0:
        print("\n❌ ERROR: No crops found in database!")
        return False
    
    print("\n" + "-" * 60)
    print("CROP DETAILS:")
    print("-" * 60)
    
    all_valid = True
    
    for crop in crops:
        print(f"\n{crop.name} ({crop.name_chichewa})")
        print(f"  Scientific name: {crop.scientific_name}")
        print(f"  Soil pH: {crop.min_ph} - {crop.max_ph}")
        print(f"  Clay content: {crop.min_clay_content}% - {crop.max_clay_content}%")
        print(f"  Organic carbon: {crop.min_organic_carbon}%+")
        print(f"  Rainfall: {crop.min_rainfall} - {crop.max_rainfall} mm")
        print(f"  Temperature: {crop.min_temperature}°C - {crop.max_temperature}°C")
        print(f"  Elevation: {crop.min_elevation}m - {crop.max_elevation}m")
        print(f"  Growing season: {crop.growing_season_days} days")
        
        # Validate requirements
        if crop.name not in expected_crops:
            print(f"  ⚠️  WARNING: Unexpected crop name")
            all_valid = False
        
        if crop.name_chichewa not in expected_chichewa:
            print(f"  ⚠️  WARNING: Unexpected Chichewa name")
            all_valid = False
            
        # Validate ranges
        if crop.min_ph >= crop.max_ph:
            print(f"  ❌ ERROR: Invalid pH range")
            all_valid = False
            
        if crop.min_clay_content >= crop.max_clay_content:
            print(f"  ❌ ERROR: Invalid clay content range")
            all_valid = False
            
        if crop.min_rainfall >= crop.max_rainfall:
            print(f"  ❌ ERROR: Invalid rainfall range")
            all_valid = False
            
        if crop.min_temperature >= crop.max_temperature:
            print(f"  ❌ ERROR: Invalid temperature range")
            all_valid = False
            
        if crop.min_elevation >= crop.max_elevation:
            print(f"  ❌ ERROR: Invalid elevation range")
            all_valid = False
    
    print("\n" + "=" * 60)
    
    # Check for missing crops
    missing_crops = []
    for expected in expected_crops:
        if not crops.filter(name=expected).exists():
            missing_crops.append(expected)
    
    if missing_crops:
        print(f"\n❌ MISSING CROPS: {', '.join(missing_crops)}")
        all_valid = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_valid and crop_count == len(expected_crops):
        print("✅ VERIFICATION PASSED")
        print("All crops have been added correctly with valid requirements.")
        print("=" * 60)
        return True
    else:
        print("❌ VERIFICATION FAILED")
        print("Some crops are missing or have invalid data.")
        print("=" * 60)
        return False


if __name__ == '__main__':
    success = verify_crops()
    sys.exit(0 if success else 1)
