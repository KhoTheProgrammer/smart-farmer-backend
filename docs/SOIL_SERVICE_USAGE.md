# Soil Service Usage Guide

## Overview

The SoilService provides integration with the SoilGrids API to retrieve soil properties for any location in Malawi (or globally). It includes automatic caching with 24-hour TTL and fallback mechanisms.

## Basic Usage

### Fetching Soil Properties

```python
from weather.services import SoilService, SoilServiceError

# Coordinates for a location in Malawi
latitude = -13.9626
longitude = 33.7741

try:
    soil_data = SoilService.fetch_soil_properties(latitude, longitude)

    # Access soil properties
    clay_content = soil_data['clay_content']  # Percentage (%)
    sand_content = soil_data['sand_content']  # Percentage (%)
    ph_level = soil_data['ph_level']          # pH scale (0-14)
    organic_carbon = soil_data['organic_carbon']  # g/kg

    print(f"Clay: {clay_content}%")
    print(f"Sand: {sand_content}%")
    print(f"pH: {ph_level}")
    print(f"Organic Carbon: {organic_carbon} g/kg")

except SoilServiceError as e:
    print(f"Error fetching soil data: {e}")
```

### Response Structure

```python
{
    'clay_content': 17.3,        # Percentage
    'sand_content': 73.8,        # Percentage
    'ph_level': 6.2,             # pH scale
    'organic_carbon': 12.9,      # g/kg
    'metadata': {
        'latitude': -13.9626,
        'longitude': 33.7741,
        'source': 'SoilGrids API',
        'depth': '0-5cm',
        'fetched_at': '2025-11-24T20:56:44.045348+00:00'
    }
}
```

### Using with Village Model

```python
from locations.models import Village
from weather.services import SoilService

# Get village
village = Village.objects.get(name="Lilongwe")

# Extract coordinates from village location
lat = village.location.y
lon = village.location.x

# Fetch soil data
soil_data = SoilService.fetch_soil_properties(lat, lon)
```

## Caching Behavior

### Automatic Caching

- All API responses are automatically cached for 24 hours
- Subsequent requests within 24 hours use cached data
- No manual cache management required

### Cache Key Format

```python
from weather.models import SoilCache

# Cache keys are formatted as "lat_lon" with 2 decimal places
location_key = SoilCache.create_location_key(-13.9626, 33.7741)
# Result: "-13.96_33.77"
```

### Checking Cache Status

```python
from weather.models import SoilCache

location_key = SoilCache.create_location_key(lat, lon)
cached = SoilCache.get_cached_data(location_key)

if cached:
    print(f"Cache exists, expires at: {cached.expires_at}")
    print(f"Is expired: {cached.is_expired()}")
else:
    print("No cache found")
```

## Error Handling

### Invalid Coordinates

```python
try:
    # Invalid latitude (must be -90 to 90)
    soil_data = SoilService.fetch_soil_properties(100, 50)
except SoilServiceError as e:
    print(e)  # "Invalid coordinates: lat=100, lon=50..."
```

### API Unavailable with Cache

```python
# If API fails but cache exists (even if expired), stale cache is used
soil_data = SoilService.fetch_soil_properties(lat, lon)

if soil_data.get('_stale_cache'):
    warning = soil_data.get('_cache_warning')
    print(f"Warning: {warning}")
    # "Using cached data due to API unavailability"
```

### API Unavailable without Cache

```python
try:
    # If API fails and no cache exists, error is raised
    soil_data = SoilService.fetch_soil_properties(lat, lon)
except SoilServiceError as e:
    print(f"Failed to fetch soil data: {e}")
```

## Advanced Usage

### Manual Cache Management

```python
from weather.models import SoilCache
from django.utils import timezone
from datetime import timedelta

# Create custom cache entry
SoilCache.objects.create(
    location_key="custom_key",
    latitude=-13.96,
    longitude=33.77,
    data={
        'clay_content': 25.0,
        'sand_content': 45.0,
        'ph_level': 6.5,
        'organic_carbon': 1.2
    },
    expires_at=timezone.now() + timedelta(hours=24)
)

# Clear expired caches
expired_caches = SoilCache.objects.filter(
    expires_at__lt=timezone.now()
)
expired_caches.delete()
```

### Batch Processing

```python
from locations.models import Village
from weather.services import SoilService

villages = Village.objects.all()

for village in villages:
    try:
        lat = village.location.y
        lon = village.location.x

        soil_data = SoilService.fetch_soil_properties(lat, lon)

        # Process soil data
        print(f"{village.name}: Clay={soil_data['clay_content']}%")

    except SoilServiceError as e:
        print(f"Error for {village.name}: {e}")
        continue
```

## API Details

### SoilGrids API

- **Endpoint**: `https://rest.isric.org/soilgrids/v2.0/properties/query`
- **Method**: GET
- **Timeout**: 30 seconds
- **Depth Layer**: 0-5cm (topsoil)

### Properties Retrieved

1. **clay**: Clay content in g/kg (converted to %)
2. **sand**: Sand content in g/kg (converted to %)
3. **phh2o**: pH in H2O (pH\*10, converted to pH scale)
4. **soc**: Soil organic carbon in dg/kg (converted to g/kg)

### Unit Conversions

The service automatically converts SoilGrids units to standard units:

- Clay/Sand: g/kg → % (divide by 10)
- pH: pH\*10 → pH scale (divide by 10)
- Organic Carbon: dg/kg → g/kg (divide by 10)

## Integration with Crop Suitability

```python
from weather.services import SoilService
from locations.models import Village

def calculate_crop_suitability(village, crop):
    """Calculate crop suitability based on soil properties."""

    # Get soil data
    lat = village.location.y
    lon = village.location.x
    soil_data = SoilService.fetch_soil_properties(lat, lon)

    # Check soil requirements
    clay_ok = crop.min_clay_content <= soil_data['clay_content'] <= crop.max_clay_content
    ph_ok = crop.min_ph <= soil_data['ph_level'] <= crop.max_ph
    oc_ok = soil_data['organic_carbon'] >= crop.min_organic_carbon

    if clay_ok and ph_ok and oc_ok:
        return "Suitable"
    else:
        return "Not Suitable"
```

## Admin Interface

View and manage cached soil data in Django admin:

1. Navigate to `/admin/weather/soilcache/`
2. View all cached locations
3. Filter by date or expiration status
4. Search by location key
5. View detailed soil properties in JSON format

## Performance Considerations

### Cache Hit Rate

- First request: ~1-2 seconds (API call)
- Cached requests: <10ms (database lookup)
- Cache duration: 24 hours

### Optimization Tips

1. Pre-fetch soil data for all villages during off-peak hours
2. Use batch processing to minimize API calls
3. Monitor cache hit rate in admin interface
4. Consider increasing cache TTL for stable soil data

## Troubleshooting

### Common Issues

**Issue**: "Invalid coordinates" error

- **Solution**: Verify latitude is between -90 and 90, longitude between -180 and 180

**Issue**: API timeout

- **Solution**: Service will automatically use cached data if available

**Issue**: Missing soil properties in response

- **Solution**: Check if coordinates are within SoilGrids coverage area

**Issue**: Empty layers in API response

- **Solution**: Verify depth parameter is "0-5cm" (not "0-30cm")

## Testing

Run the verification script:

```bash
python verify_soil_service.py
```

Run unit tests:

```bash
python manage.py test weather.tests.SoilCacheModelTest weather.tests.SoilServiceTest
```

## References

- [SoilGrids API Documentation](https://rest.isric.org/soilgrids/v2.0/docs)
- [ISRIC World Soil Information](https://www.isric.org/)
- Requirements: 3.1, 3.2
