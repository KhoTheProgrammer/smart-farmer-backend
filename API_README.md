# Mlimi Wanzeru REST API Documentation

## Overview

The Mlimi Wanzeru REST API provides location-based agricultural advisory services for smallholder farmers in Malawi. The API offers endpoints for location management, planting calendar calculations, and crop suitability analysis.

## Base URL

```
http://localhost:8000/api/
```

## API Documentation

Visit `http://localhost:8000/api/` for interactive HTML documentation.

## Authentication

Currently, the API is open and does not require authentication. Rate limiting is set to 100 requests per minute per IP address.

## Response Format

All endpoints return JSON. Successful responses have HTTP status 200.

### Error Responses

- **400 Bad Request**: Invalid parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: External API unavailable

## Endpoints

### Location Endpoints

#### List Districts

```
GET /api/locations/districts/
```

Returns a list of all districts in Malawi.

**Response:**

```json
[
  {
    "id": "uuid",
    "name": "Lilongwe City",
    "name_chichewa": "Lilongwe City"
  }
]
```

#### Get District Details

```
GET /api/locations/districts/{id}/
```

Returns detailed information about a specific district including GeoJSON boundary.

**Response:**

```json
{
  "id": "uuid",
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [...]
  },
  "properties": {
    "name": "Lilongwe City",
    "name_chichewa": "Lilongwe City",
    "centroid": {...}
  }
}
```

#### List Villages in District

```
GET /api/locations/districts/{id}/villages/
```

Returns all villages within a specific district.

**Response:**

```json
[
  {
    "id": "uuid",
    "name": "Area 1",
    "name_chichewa": "Area 1",
    "district": "uuid",
    "district_name": "Lilongwe City",
    "latitude": -14.0029,
    "longitude": 33.781,
    "elevation": 1200.5
  }
]
```

#### List All Villages

```
GET /api/locations/villages/
```

Returns a list of all villages. Can be filtered by district.

**Query Parameters:**

- `district` (optional): UUID of district to filter by

**Response:**

```json
[
  {
    "id": "uuid",
    "name": "Area 1",
    "name_chichewa": "Area 1",
    "district": "uuid",
    "district_name": "Lilongwe City",
    "latitude": -14.0029,
    "longitude": 33.781,
    "elevation": 1200.5
  }
]
```

#### Get Village Details

```
GET /api/locations/villages/{id}/
```

Returns detailed information about a specific village including GeoJSON location.

**Response:**

```json
{
  "id": "uuid",
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [33.781, -14.0029]
  },
  "properties": {
    "name": "Area 1",
    "name_chichewa": "Area 1",
    "district": "uuid",
    "district_name": "Lilongwe City",
    "latitude": -14.0029,
    "longitude": 33.781,
    "elevation": 1200.5
  }
}
```

#### Reverse Geocode

```
GET /api/locations/reverse/?lat={lat}&lon={lon}
```

Finds the district and village for given coordinates.

**Query Parameters:**

- `lat` (required): Latitude (-90 to 90)
- `lon` (required): Longitude (-180 to 180)

**Response:**

```json
{
  "district": {
    "id": "uuid",
    "name": "Lilongwe City",
    "name_chichewa": "Lilongwe City"
  },
  "village": {
    "id": "uuid",
    "name": "Area 2",
    "name_chichewa": "Area 2",
    "latitude": -13.9874,
    "longitude": 33.7786,
    "elevation": 1200.5
  }
}
```

### Agricultural Advisory Endpoints

#### List Crops

```
GET /api/advisory/crops/
```

Returns a list of all crops in the database with their requirements.

**Response:**

```json
[
  {
    "id": "uuid",
    "name": "Maize",
    "name_chichewa": "Chimanga",
    "scientific_name": "Zea mays",
    "min_ph": 5.5,
    "max_ph": 7.5,
    "min_clay_content": 10.0,
    "max_clay_content": 40.0,
    "min_organic_carbon": 1.0,
    "min_rainfall": 500.0,
    "max_rainfall": 1200.0,
    "min_temperature": 18.0,
    "max_temperature": 32.0,
    "min_elevation": 0.0,
    "max_elevation": 2000.0,
    "growing_season_days": 120
  }
]
```

#### Get Crop Details

```
GET /api/advisory/crops/{id}/
```

Returns detailed information about a specific crop.

**Response:**

```json
{
  "id": "uuid",
  "name": "Maize",
  "name_chichewa": "Chimanga",
  "scientific_name": "Zea mays",
  "min_ph": 5.5,
  "max_ph": 7.5,
  "min_clay_content": 10.0,
  "max_clay_content": 40.0,
  "min_organic_carbon": 1.0,
  "min_rainfall": 500.0,
  "max_rainfall": 1200.0,
  "min_temperature": 18.0,
  "max_temperature": 32.0,
  "min_elevation": 0.0,
  "max_elevation": 2000.0,
  "growing_season_days": 120
}
```

#### Get Planting Calendar

```
GET /api/advisory/planting-calendar/?location={village_id}
```

Returns optimal planting window based on 10-year rainfall analysis.

**Query Parameters:**

- `location` (required): UUID of village
- `crop` (optional): UUID of crop
- `force_refresh` (optional): Boolean to force recalculation (default: false)

**Response:**

```json
{
  "id": "uuid",
  "village": "uuid",
  "village_name": "Area 1",
  "village_name_chichewa": "Area 1",
  "crop": null,
  "crop_name": null,
  "crop_name_chichewa": null,
  "start_date": "2025-01-20",
  "end_date": "2025-02-19",
  "confidence_level": 0.85,
  "calculated_at": "2025-11-25T01:00:08.978912+02:00"
}
```

#### Get Crop Suitability

```
GET /api/advisory/crop-suitability/?location={village_id}
```

Returns ranked list of crops by suitability score for a location.

**Query Parameters:**

- `location` (required): UUID of village

**Response:**

```json
[
  {
    "crop_id": "uuid",
    "name": "Maize",
    "name_chichewa": "Chimanga",
    "scientific_name": "Zea mays",
    "suitability_score": 85.5,
    "soil_requirements": {
      "min_ph": 5.5,
      "max_ph": 7.5,
      "min_clay_content": 10.0,
      "max_clay_content": 40.0,
      "min_organic_carbon": 1.0
    },
    "elevation_requirements": {
      "min_elevation": 0.0,
      "max_elevation": 2000.0
    }
  }
]
```

#### Get Crop Suitability Map Data

```
GET /api/advisory/crop-suitability-map/?crop={crop_id}&bounds={bbox}
```

Returns grid of suitability scores for map visualization.

**Query Parameters:**

- `crop` (required): UUID of crop
- `bounds` (required): Bounding box as "min_lat,min_lon,max_lat,max_lon"
- `resolution` (optional): Grid resolution in degrees (default: 0.01)

**Response:**

```json
{
  "crop_id": "uuid",
  "crop_name": "Maize",
  "bounds": {
    "min_lat": -14.0,
    "min_lon": 33.0,
    "max_lat": -13.0,
    "max_lon": 34.0
  },
  "resolution": 0.01,
  "data": [
    {
      "lat": -14.0,
      "lon": 33.0,
      "suitability_score": 75.5
    }
  ]
}
```

## Data Caching

The API implements intelligent caching for external data sources:

- **Weather Data**: Cached for 24 hours
- **Soil Data**: Cached for 24 hours
- **Planting Windows**: Recalculated every 30 days

When external APIs are unavailable, the system falls back to cached data and includes a warning in the response.

## Rate Limiting

API requests are limited to 100 requests per minute per IP address. If you exceed this limit, you'll receive a 429 Too Many Requests response.

## Testing the API

You can test the API using curl:

```bash
# List districts
curl http://localhost:8000/api/locations/districts/

# Get planting calendar for a village
curl "http://localhost:8000/api/advisory/planting-calendar/?location=VILLAGE_UUID"

# Get crop suitability for a village
curl "http://localhost:8000/api/advisory/crop-suitability/?location=VILLAGE_UUID"
```

Or use the provided test script:

```bash
python test_api_endpoints.py
```

## Running the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## Requirements Validation

This API implementation validates the following requirements:

- **Requirements 1.1-1.5**: Location management and coordinate retrieval
- **Requirements 2.1-2.5**: Planting calendar with rainfall analysis
- **Requirements 3.1-3.6**: Crop suitability with soil and elevation data
- **Requirements 4.1-4.4**: Map visualization data
- **Requirements 9.1-9.5**: Weather API integration with caching

## Support

For issues or questions, please refer to the main project README or contact the development team.
