#!/usr/bin/env python
"""
Test script to verify API endpoints are working.
This script tests the basic functionality of all REST API endpoints.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlimi_wanzeru.settings')
django.setup()

from django.test import RequestFactory
from locations.views import DistrictViewSet, VillageViewSet, ReverseGeocodeView
from weather.views import CropViewSet, PlantingCalendarView, CropSuitabilityView
from locations.models import District, Village
from weather.models import Crop


def test_district_list():
    """Test district list endpoint."""
    print("\n=== Testing District List Endpoint ===")
    factory = RequestFactory()
    request = factory.get('/api/locations/districts/')
    
    view = DistrictViewSet.as_view({'get': 'list'})
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Type: {type(response.data)}")
    
    if response.status_code == 200:
        print(f"✓ District list endpoint working")
        print(f"  Found {len(response.data)} districts")
        if len(response.data) > 0:
            print(f"  Sample: {response.data[0]}")
    else:
        print(f"✗ District list endpoint failed")
    
    return response.status_code == 200


def test_village_list():
    """Test village list endpoint."""
    print("\n=== Testing Village List Endpoint ===")
    factory = RequestFactory()
    request = factory.get('/api/locations/villages/')
    
    view = VillageViewSet.as_view({'get': 'list'})
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Type: {type(response.data)}")
    
    if response.status_code == 200:
        print(f"✓ Village list endpoint working")
        print(f"  Found {len(response.data)} villages")
        if len(response.data) > 0:
            print(f"  Sample: {response.data[0]}")
    else:
        print(f"✗ Village list endpoint failed")
    
    return response.status_code == 200


def test_reverse_geocode():
    """Test reverse geocode endpoint."""
    print("\n=== Testing Reverse Geocode Endpoint ===")
    factory = RequestFactory()
    
    # Test with coordinates in Malawi (Lilongwe area)
    request = factory.get('/api/locations/reverse/?lat=-13.9833&lon=33.7833')
    
    view = ReverseGeocodeView.as_view()
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✓ Reverse geocode endpoint working")
        print(f"  Result: {response.data}")
    elif response.status_code == 404:
        print(f"⚠ Reverse geocode endpoint working but no data found (expected if no boundaries imported)")
    else:
        print(f"✗ Reverse geocode endpoint failed")
    
    return response.status_code in [200, 404]


def test_crop_list():
    """Test crop list endpoint."""
    print("\n=== Testing Crop List Endpoint ===")
    factory = RequestFactory()
    request = factory.get('/api/advisory/crops/')
    
    view = CropViewSet.as_view({'get': 'list'})
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✓ Crop list endpoint working")
        print(f"  Found {len(response.data)} crops")
        if len(response.data) > 0:
            print(f"  Sample: {response.data[0]['name']}")
    else:
        print(f"✗ Crop list endpoint failed")
    
    return response.status_code == 200


def test_planting_calendar():
    """Test planting calendar endpoint."""
    print("\n=== Testing Planting Calendar Endpoint ===")
    
    # Check if we have any villages
    village = Village.objects.first()
    
    if not village:
        print("⚠ No villages in database, skipping planting calendar test")
        return True
    
    factory = RequestFactory()
    request = factory.get(f'/api/advisory/planting-calendar/?location={village.id}')
    
    view = PlantingCalendarView.as_view()
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✓ Planting calendar endpoint working")
        print(f"  Result: {response.data}")
    elif response.status_code == 503:
        print(f"⚠ Planting calendar endpoint working but external API unavailable (expected)")
    else:
        print(f"✗ Planting calendar endpoint failed: {response.data}")
    
    return response.status_code in [200, 503]


def test_crop_suitability():
    """Test crop suitability endpoint."""
    print("\n=== Testing Crop Suitability Endpoint ===")
    
    # Check if we have any villages
    village = Village.objects.first()
    
    if not village:
        print("⚠ No villages in database, skipping crop suitability test")
        return True
    
    factory = RequestFactory()
    request = factory.get(f'/api/advisory/crop-suitability/?location={village.id}')
    
    view = CropSuitabilityView.as_view()
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✓ Crop suitability endpoint working")
        print(f"  Found {len(response.data)} crops ranked")
        if len(response.data) > 0:
            print(f"  Top crop: {response.data[0]['name']} (score: {response.data[0]['suitability_score']})")
    elif response.status_code == 503:
        print(f"⚠ Crop suitability endpoint working but external API unavailable (expected)")
    else:
        print(f"✗ Crop suitability endpoint failed: {response.data}")
    
    return response.status_code in [200, 503]


def main():
    """Run all tests."""
    print("=" * 60)
    print("API Endpoint Tests")
    print("=" * 60)
    
    results = {
        'District List': test_district_list(),
        'Village List': test_village_list(),
        'Reverse Geocode': test_reverse_geocode(),
        'Crop List': test_crop_list(),
        'Planting Calendar': test_planting_calendar(),
        'Crop Suitability': test_crop_suitability(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
