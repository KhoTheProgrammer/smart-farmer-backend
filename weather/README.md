# Weather App

This Django app handles weather data integration with NASA POWER API for the Mlimi Wanzeru platform.

## Features

- **WeatherCache Model**: Stores weather data with 24-hour TTL
- **WeatherService**: Integrates with NASA POWER API
- **PlantingWindow Model**: Stores calculated planting windows
- **Crop Model**: Stores crop requirements for suitability analysis
- **PlantingCalendarService**: Calculates optimal planting dates
- **Automatic Caching**: Reduces API calls by caching responses
- **Fallback Mechanism**: Uses stale cache when API is unavailable
- **Error Handling**: Comprehensive error handling for API failures
- **Configurable API URL**: NASA POWER API URL is configurable via environment variables

## Models

### WeatherCache

Stores cached weather data from NASA POWER API.

**Fields:**

- `location_key`: Unique identifier for location (format: "lat_lon")
- `latitude`: Latitude coordinate
- `longitude`: Longitude coordinate
- `data`: JSON field containing weather data
- `cached_at`: Timestamp when data was cached
- `expires_at`: Expiration timestamp (24 hours from cache time)

### PlantingWindow

Stores calculated optimal planting windows for villages.

**Fields:**

- `village`: Foreign key to Village
- `crop`: Optional foreign key to Crop
- `start_date`: Planting window start date
- `end_date`: Planting window end date
- `confidence_level`: Confidence level (0-1) based on rainfall variability
- `calculated_at`: Timestamp of calculation

### Crop

Stores crop information and requirements.

**Fields:**

- `name`: Crop name in English
- `name_chichewa`: Crop name in Chichewa
- `scientific_name`: Scientific name
- Soil requirements: pH, clay content, organic carbon
- Climate requirements: rainfall, temperature
- Elevation requirements: min/max elevation
- `growing_season_days`: Length of growing season

## Services

### WeatherService

Main service class for weather data operations.

**Key Methods:**

- `fetch_rainfall_data(lat, lon, start_year, end_year)`: Fetches historical weather data
  - Checks cache first
  - Falls back to API if cache expired
  - Falls back to stale cache if API fails
- `_fetch_from_api(lat, lon, start_year, end_year)`: Direct API fetch

  - Queries NASA POWER API
  - Parses JSON response
  - Extracts precipitation, temperature, and solar radiation

- `_parse_api_response(response_data)`: Parses API response

  - Extracts weather parameters
  - Validates data completeness
  - Returns structured data

- `calculate_planting_window(rainfall_data)`: Calculates optimal planting dates

  - Analyzes 10 years of rainfall patterns
  - Identifies rainy season onset
  - Calculates confidence level based on variability

- `_analyze_rainfall_patterns(precipitation)`: Analyzes historical rainfall

  - Groups data by year and day of year
  - Calculates cumulative rainfall
  - Identifies rainy season onset (20% threshold)
  - Returns statistics on onset timing and variability

- `_calculate_confidence_level(analysis)`: Calculates confidence
  - Uses coefficient of variation
  - Lower variability = higher confidence
  - Returns value between 0 and 1

### PlantingCalendarService

Service for managing planting calendar calculations.

**Key Methods:**

- `get_planting_window_for_village(village, crop, force_refresh)`: Get/calculate window

  - Checks for recent calculations (30 days)
  - Fetches weather data if needed
  - Calculates and stores planting window
  - Returns PlantingWindow instance

- `get_planting_windows_for_district(district, crop)`: Batch calculate
  - Processes all villages in district
  - Returns list of PlantingWindow instances

## Configuration

Add the following to your `.env` file:

```bash
# NASA POWER API Configuration
NASA_POWER_API_URL=https://power.larc.nasa.gov/api/temporal/daily/point
NASA_POWER_API_KEY=not_required_for_nasa_power
```

The API URL is configurable to allow for:

- Testing with mock servers
- Using alternative endpoints
- Adapting to API changes without code modifications

## Management Commands

### calculate_planting_windows

Calculate planting windows for villages.

```bash
# Calculate for all villages
python manage.py calculate_planting_windows

# Calculate for specific district
python manage.py calculate_planting_windows --district "Lilongwe"

# Calculate for specific village
python manage.py calculate_planting_windows --village "Chinsapo"

# Force recalculation
python manage.py calculate_planting_windows --force
```

## Usage Examples

### Fetching Weather Data

```python
from weather.services import WeatherService

# Fetch 10 years of weather data for Lilongwe
try:
    data = WeatherService.fetch_rainfall_data(
        lat=-13.9626,
        lon=33.7741,
        start_year=2014,
        end_year=2023
    )

    # Access precipitation data
    precipitation = data['precipitation']
    temperature = data['temperature']
    solar_radiation = data['solar_radiation']

except WeatherServiceError as e:
    print(f"Error fetching weather data: {e}")
```

### Calculating Planting Windows

```python
from locations.models import Village
from weather.services import PlantingCalendarService

# Get a village
village = Village.objects.get(name="Chinsapo")

# Calculate planting window
window = PlantingCalendarService.get_planting_window_for_village(village)

print(f"Planting window: {window.start_date} to {window.end_date}")
print(f"Confidence: {window.confidence_level:.2%}")
```

## Testing

Run tests with:

```bash
python manage.py test weather
```

All tests include:

- Model tests for caching logic
- Service tests for API integration
- Cache expiration tests
- Fallback mechanism tests
- Coordinate validation tests

## Requirements Validated

### Weather Data Integration

- **2.1**: Weather API integration with NASA POWER
- **9.1**: NASA POWER API with latitude/longitude parameters
- **9.2**: JSON response parsing
- **9.3**: 24-hour cache TTL
- **9.4**: Fallback to cache on API failure
- **9.5**: Extract precipitation, temperature, and solar radiation values

### Planting Calendar

- **2.2**: 10-year historical rainfall analysis
- **2.3**: Optimal planting window calculation based on rainy season onset
- **2.4**: Display start and end dates
- **2.5**: Confidence level based on rainfall variability
