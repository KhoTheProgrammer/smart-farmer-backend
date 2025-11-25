#!/usr/bin/env python3
"""Fetch actual API responses for documentation"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlimi_wanzeru.settings')
django.setup()

from rest_framework.test import APIClient
from locations.models import District, Village
from weather.models import Crop

client = APIClient()

def get_response(url, description):
    """Fetch and format API response"""
    print(f"\n=== {description} ===")
    print(f"URL: {url}")
    response = client.get(url)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # Limit array responses to first 2 items for brevity
        if isinstance(data, list) and len(data) > 2:
            data = data[:2]
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(response.json(), indent=2, ensure_ascii=False)

# Get sample IDs
district = District.objects.first()
village = Village.objects.first()
crop = Crop.objects.first()

print("Sample IDs:")
print(f"District: {district.id}")
print(f"Village: {village.id}")
print(f"Crop: {crop.id}")

# Fetch all responses
responses = {}

responses['districts_list'] = get_response('/api/locations/districts/', 'List Districts')
responses['district_detail'] = get_response(f'/api/locations/districts/{district.id}/', 'District Detail')
responses['district_villages'] = get_response(f'/api/locations/districts/{district.id}/villages/', 'District Villages')
responses['villages_list'] = get_response('/api/locations/villages/', 'List Villages')
responses['village_detail'] = get_response(f'/api/locations/villages/{village.id}/', 'Village Detail')
responses['reverse_geocode'] = get_response(f'/api/locations/reverse/?lat={village.latitude}&lon={village.longitude}', 'Reverse Geocode')
responses['crops_list'] = get_response('/api/advisory/crops/', 'List Crops')
responses['crop_detail'] = get_response(f'/api/advisory/crops/{crop.id}/', 'Crop Detail')
responses['planting_calendar'] = get_response(f'/api/advisory/planting-calendar/?location={village.id}', 'Planting Calendar')

# Try crop suitability (may fail if external API unavailable)
try:
    responses['crop_suitability'] = get_response(f'/api/advisory/crop-suitability/?location={village.id}', 'Crop Suitability')
except:
    responses['crop_suitability'] = '{\n  "error": "External API unavailable"\n}'

# Save to file
with open('api_responses.json', 'w') as f:
    json.dump(responses, f, indent=2, ensure_ascii=False)

print("\n\n=== Responses saved to api_responses.json ===")
