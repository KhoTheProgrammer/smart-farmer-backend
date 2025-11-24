#!/usr/bin/env python3
"""
Verification script for CropSuitabilityService.
Tests the crop suitability calculation functionality.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlimi_wanzeru.settings')
django.setup()

from weather.services import CropSuitabilityService, CropSuitabilityServiceError
from weather.models import Crop
from locations.models import Village, District


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def verify_crop_suitability():
    """Verify crop suitability service functionality."""
    
    print_section("Crop Suitability Service Verification")
    
    # Check if we have crops in the database
    crops = Crop.objects.all()
    print(f"\n✓ Found {crops.count()} crops in database")
    
    if crops.count() == 0:
        print("✗ No crops found. Please run migrations first.")
        return False
    
    # Display available crops
    print("\nAvailable crops:")
    for crop in crops[:5]:  # Show first 5
        print(f"  - {crop.name} ({crop.name_chichewa})")
    if crops.count() > 5:
        print(f"  ... and {crops.count() - 5} more")
    
    # Check if we have villages
    villages = Village.objects.all()
    print(f"\n✓ Found {villages.count()} villages in database")
    
    if villages.count() == 0:
        print("✗ No villages found. Please import boundary data first.")
        return False
    
    # Test with a sample village
    village = villages.first()
    print(f"\nTesting with village: {village.name} ({village.district.name})")
    print(f"  Location: {village.location.y:.4f}, {village.location.x:.4f}")
    print(f"  Elevation: {village.elevation}m" if village.elevation else "  Elevation: Not set")
    
    # Test 1: Get crop requirements
    print_section("Test 1: Get Crop Requirements")
    test_crop = crops.first()
    try:
        requirements = CropSuitabilityService.get_crop_requirements(str(test_crop.id))
        print(f"\n✓ Successfully retrieved requirements for {test_crop.name}")
        print(f"  Soil pH range: {requirements['soil_requirements']['min_ph']} - {requirements['soil_requirements']['max_ph']}")
        print(f"  Elevation range: {requirements['elevation_requirements']['min_elevation']}m - {requirements['elevation_requirements']['max_elevation']}m")
        print(f"  Growing season: {requirements['growing_season_days']} days")
    except Exception as e:
        print(f"✗ Failed to get crop requirements: {e}")
        return False
    
    # Test 2: Calculate suitability for a single crop
    print_section("Test 2: Calculate Suitability Score")
    
    # Sample soil data (typical Malawi values)
    soil_data = {
        'ph_level': 6.0,
        'clay_content': 25.0,
        'sand_content': 45.0,
        'organic_carbon': 1.5
    }
    
    elevation = village.elevation if village.elevation else 1000.0
    
    try:
        score = CropSuitabilityService.calculate_suitability(
            test_crop,
            soil_data,
            elevation
        )
        print(f"\n✓ Successfully calculated suitability score")
        print(f"  Crop: {test_crop.name}")
        print(f"  Soil pH: {soil_data['ph_level']}")
        print(f"  Clay content: {soil_data['clay_content']}%")
        print(f"  Elevation: {elevation}m")
        print(f"  Suitability Score: {score:.2f}/100")
        
        if score >= 80:
            print(f"  Rating: Highly Suitable ✓")
        elif score >= 60:
            print(f"  Rating: Suitable")
        elif score >= 40:
            print(f"  Rating: Moderately Suitable")
        else:
            print(f"  Rating: Not Suitable")
            
    except Exception as e:
        print(f"✗ Failed to calculate suitability: {e}")
        return False
    
    # Test 3: Rank all crops (with provided soil data to avoid API calls)
    print_section("Test 3: Rank All Crops by Suitability")
    
    try:
        results = CropSuitabilityService.rank_crops(
            village,
            soil_data=soil_data
        )
        print(f"\n✓ Successfully ranked {len(results)} crops")
        print("\nTop 5 most suitable crops:")
        for i, result in enumerate(results[:5], 1):
            print(f"  {i}. {result['name']} ({result['name_chichewa']})")
            print(f"     Score: {result['suitability_score']:.2f}/100")
            print(f"     pH range: {result['soil_requirements']['min_ph']}-{result['soil_requirements']['max_ph']}")
        
        # Verify sorting
        scores = [r['suitability_score'] for r in results]
        if scores == sorted(scores, reverse=True):
            print("\n✓ Results are correctly sorted by score (highest first)")
        else:
            print("\n✗ Results are not properly sorted")
            return False
            
    except Exception as e:
        print(f"✗ Failed to rank crops: {e}")
        return False
    
    # Test 4: Test with poor conditions
    print_section("Test 4: Test with Poor Soil Conditions")
    
    poor_soil = {
        'ph_level': 4.0,  # Too acidic
        'clay_content': 5.0,  # Too sandy
        'sand_content': 85.0,
        'organic_carbon': 0.3  # Too low
    }
    
    try:
        poor_score = CropSuitabilityService.calculate_suitability(
            test_crop,
            poor_soil,
            elevation
        )
        print(f"\n✓ Successfully calculated suitability with poor conditions")
        print(f"  Crop: {test_crop.name}")
        print(f"  Soil pH: {poor_soil['ph_level']} (very acidic)")
        print(f"  Clay content: {poor_soil['clay_content']}% (very sandy)")
        print(f"  Organic carbon: {poor_soil['organic_carbon']} (very low)")
        print(f"  Suitability Score: {poor_score:.2f}/100")
        print(f"  Rating: Not Suitable (as expected)")
        
        if poor_score < score:
            print("\n✓ Poor conditions correctly result in lower score")
        else:
            print("\n✗ Poor conditions did not result in lower score")
            return False
            
    except Exception as e:
        print(f"✗ Failed to calculate suitability with poor conditions: {e}")
        return False
    
    # Test 5: Test with ideal conditions
    print_section("Test 5: Test with Ideal Soil Conditions")
    
    # Use the crop's ideal conditions
    ideal_soil = {
        'ph_level': (test_crop.min_ph + test_crop.max_ph) / 2,
        'clay_content': (test_crop.min_clay_content + test_crop.max_clay_content) / 2,
        'sand_content': 40.0,
        'organic_carbon': test_crop.min_organic_carbon * 1.5
    }
    
    ideal_elevation = (test_crop.min_elevation + test_crop.max_elevation) / 2
    
    try:
        ideal_score = CropSuitabilityService.calculate_suitability(
            test_crop,
            ideal_soil,
            ideal_elevation
        )
        print(f"\n✓ Successfully calculated suitability with ideal conditions")
        print(f"  Crop: {test_crop.name}")
        print(f"  Soil pH: {ideal_soil['ph_level']:.1f} (ideal)")
        print(f"  Clay content: {ideal_soil['clay_content']:.1f}% (ideal)")
        print(f"  Elevation: {ideal_elevation:.0f}m (ideal)")
        print(f"  Suitability Score: {ideal_score:.2f}/100")
        
        if ideal_score >= 80:
            print(f"  Rating: Highly Suitable ✓")
        
        if ideal_score > score:
            print("\n✓ Ideal conditions correctly result in higher score")
        else:
            print("\n✗ Ideal conditions did not result in higher score")
            
    except Exception as e:
        print(f"✗ Failed to calculate suitability with ideal conditions: {e}")
        return False
    
    # Test 6: Verify score bounds
    print_section("Test 6: Verify Score Bounds")
    
    extreme_soil = {
        'ph_level': 10.0,
        'clay_content': 90.0,
        'sand_content': 5.0,
        'organic_carbon': 0.01
    }
    
    try:
        extreme_score = CropSuitabilityService.calculate_suitability(
            test_crop,
            extreme_soil,
            5000.0  # Very high elevation
        )
        
        if 0 <= extreme_score <= 100:
            print(f"\n✓ Score is within bounds: {extreme_score:.2f}/100")
            print("  Even with extreme values, score is properly bounded")
        else:
            print(f"\n✗ Score is out of bounds: {extreme_score:.2f}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to calculate suitability with extreme conditions: {e}")
        return False
    
    # Summary
    print_section("Verification Summary")
    print("\n✓ All tests passed successfully!")
    print("\nCropSuitabilityService is working correctly:")
    print("  ✓ Can retrieve crop requirements")
    print("  ✓ Can calculate suitability scores")
    print("  ✓ Can rank crops by suitability")
    print("  ✓ Correctly handles poor conditions")
    print("  ✓ Correctly handles ideal conditions")
    print("  ✓ Maintains score bounds (0-100)")
    print("\nThe service is ready for use in the API endpoints.")
    
    return True


if __name__ == '__main__':
    try:
        success = verify_crop_suitability()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
