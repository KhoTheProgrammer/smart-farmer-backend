# Mlimi Wanzeru REST API Documentation

## Overview

The Mlimi Wanzeru REST API provides location-based agricultural advisory services for smallholder farmers in Malawi. The API offers endpoints for location management, planting calendar calculations, and crop suitability analysis.

## Base URL

```text
http://localhost:8000/api/
```

## API Documentation

Visit `http://localhost:8000/api/` for interactive HTML documentation.

## Authentication

Currently, the API is open and does not require authentication. Rate limiting is set to 100 requests per minute per IP address.

## Response Format

All endpoints return JSON. Successful responses have HTTP status 200.

### Error Responses

All error responses follow a consistent JSON format:

**400 Bad Request** - Invalid or missing parameters

```json
{
  "error": "location parameter is required"
}
```

**404 Not Found** - Resource not found

```json
{
  "detail": "Not found."
}
```

or

```json
{
  "error": "No district found for the given coordinates"
}
```

**429 Too Many Requests** - Rate limit exceeded

```json
{
  "detail": "Request was throttled. Expected available in 60 seconds."
}
```

**500 Internal Server Error** - Server error

```json
{
  "error": "Internal server error",
  "detail": "An unexpected error occurred"
}
```

**503 Service Unavailable** - External API unavailable

```json
{
  "error": "External API unavailable and no cached data available"
}
```

## Endpoints

### Location Endpoints

#### List Districts

```http
GET /api/locations/districts/
```

Returns a list of all districts in Malawi (32 total).

**Response:** `200 OK`

```json
[
  {
    "id": "e00de446-86ac-497f-84cb-92ce85c4fd70",
    "name": "Balaka",
    "name_chichewa": "Balaka"
  },
  {
    "id": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "name": "Lilongwe City",
    "name_chichewa": "Lilongwe City"
  },
  {
    "id": "f8a3c2d1-5b4e-4a9c-8d7f-1e2a3b4c5d6e",
    "name": "Mzimba",
    "name_chichewa": "Mzimba"
  }
]
```

#### Get District Details

```http
GET /api/locations/districts/{id}/
```

Returns detailed information about a specific district including GeoJSON boundary.

**Parameters:**

- `id` (path): District UUID

**Response:** `200 OK`

```json
{
  "id": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [
      [
        [
          [33.7786, -13.9874],
          [33.7812, -13.9901],
          [33.785, -13.992],
          [33.7786, -13.9874]
        ]
      ]
    ]
  },
  "properties": {
    "name": "Lilongwe City",
    "name_chichewa": "Lilongwe City",
    "centroid": {
      "type": "Point",
      "coordinates": [33.7799, -13.9888]
    },
    "created_at": "2025-11-24T10:30:00Z",
    "updated_at": "2025-11-24T10:30:00Z"
  }
}
```

#### List Villages in District

```http
GET /api/locations/districts/{id}/villages/
```

Returns all villages within a specific district.

**Parameters:**

- `id` (path): District UUID

**Response:** `200 OK`

```json
[
  {
    "id": "8f1ad073-4ac7-450d-b569-5454e934dc56",
    "name": "Area 1",
    "name_chichewa": "Area 1",
    "district": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "district_name": "Lilongwe City",
    "latitude": -14.002967594085035,
    "longitude": 33.78105170654241,
    "elevation": 1100.5
  },
  {
    "id": "aa8b761a-a7ef-49a0-860d-b9a1defaf56c",
    "name": "Area 2",
    "name_chichewa": "Area 2",
    "district": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "district_name": "Lilongwe City",
    "latitude": -13.9874228747885,
    "longitude": 33.77869977803419,
    "elevation": 1095.2
  },
  {
    "id": "c3d4e5f6-a7b8-49c0-960d-c9b2aefbf57d",
    "name": "Area 3",
    "name_chichewa": "Area 3",
    "district": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "district_name": "Lilongwe City",
    "latitude": -13.9950123456789,
    "longitude": 33.78234567890123,
    "elevation": null
  }
]
```

**Note:** `elevation` may be `null` if elevation data hasn't been imported for that village.

#### List All Villages

```http
GET /api/locations/villages/
GET /api/locations/villages/?district={district_id}
```

Returns a list of all villages (433 total). Can be filtered by district.

**Query Parameters:**

- `district` (optional): UUID of district to filter by

**Response:** `200 OK`

```json
[
  {
    "id": "8f1ad073-4ac7-450d-b569-5454e934dc56",
    "name": "Area 1",
    "name_chichewa": "Area 1",
    "district": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "district_name": "Lilongwe City",
    "latitude": -14.002967594085035,
    "longitude": 33.78105170654241,
    "elevation": 1100.5
  },
  {
    "id": "aa8b761a-a7ef-49a0-860d-b9a1defaf56c",
    "name": "Area 2",
    "name_chichewa": "Area 2",
    "district": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "district_name": "Lilongwe City",
    "latitude": -13.9874228747885,
    "longitude": 33.77869977803419,
    "elevation": 1095.2
  }
]
```

**Note:** `elevation` may be `null` if elevation data hasn't been imported for that village.

#### Get Village Details

```http
GET /api/locations/villages/{id}/
```

Returns detailed information about a specific village including GeoJSON location.

**Parameters:**

- `id` (path): Village UUID

**Response:** `200 OK`

```json
{
  "id": "8f1ad073-4ac7-450d-b569-5454e934dc56",
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [33.78105170654241, -14.002967594085035]
  },
  "properties": {
    "name": "Area 1",
    "name_chichewa": "Area 1",
    "district": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "district_name": "Lilongwe City",
    "district_name_chichewa": "Lilongwe City",
    "latitude": -14.002967594085035,
    "longitude": 33.78105170654241,
    "elevation": 1100.5,
    "created_at": "2025-11-24T10:30:00Z",
    "updated_at": "2025-11-24T10:30:00Z"
  }
}
```

#### Reverse Geocode

```http
GET /api/locations/reverse/?lat={lat}&lon={lon}
```

Finds the district and village for given coordinates.

**Query Parameters:**

- `lat` (required): Latitude (-90 to 90)
- `lon` (required): Longitude (-180 to 180)

**Example:** `/api/locations/reverse/?lat=-13.9874&lon=33.7786`

**Response:** `200 OK`

```json
{
  "district": {
    "id": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "name": "Lilongwe City",
    "name_chichewa": "Lilongwe City"
  },
  "village": {
    "id": "aa8b761a-a7ef-49a0-860d-b9a1defaf56c",
    "name": "Area 2",
    "name_chichewa": "Area 2",
    "latitude": -13.9874228747885,
    "longitude": 33.77869977803419,
    "elevation": 1095.2
  }
}
```

**Error Response:** `404 Not Found`

```json
{
  "error": "No district found for the given coordinates"
}
```

### Agricultural Advisory Endpoints

#### List Crops

```http
GET /api/advisory/crops/
```

Returns a list of all crops in the database with their requirements (6 total).

**Response:** `200 OK`

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
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
  },
  {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "name": "Beans",
    "name_chichewa": "Nyemba",
    "scientific_name": "Phaseolus vulgaris",
    "min_ph": 6.0,
    "max_ph": 7.5,
    "min_clay_content": 15.0,
    "max_clay_content": 35.0,
    "min_organic_carbon": 1.5,
    "min_rainfall": 400.0,
    "max_rainfall": 900.0,
    "min_temperature": 15.0,
    "max_temperature": 30.0,
    "min_elevation": 0.0,
    "max_elevation": 2500.0,
    "growing_season_days": 90
  },
  {
    "id": "c3d4e5f6-a7b8-9012-cdef-234567890123",
    "name": "Groundnuts",
    "name_chichewa": "Mtedza",
    "scientific_name": "Arachis hypogaea",
    "min_ph": 5.9,
    "max_ph": 7.0,
    "min_clay_content": 10.0,
    "max_clay_content": 30.0,
    "min_organic_carbon": 1.2,
    "min_rainfall": 500.0,
    "max_rainfall": 1000.0,
    "min_temperature": 20.0,
    "max_temperature": 30.0,
    "min_elevation": 0.0,
    "max_elevation": 1500.0,
    "growing_season_days": 120
  }
]
```

**Available Crops:** Maize (Chimanga), Beans (Nyemba), Groundnuts (Mtedza), Soya Beans (Soya), Pigeon Peas (Nandolo), Sweet Potatoes (Mbatata)

#### Get Crop Details

```http
GET /api/advisory/crops/{id}/
```

Returns detailed information about a specific crop.

**Parameters:**

- `id` (path): Crop UUID

**Response:** `200 OK`

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
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

**Error Response:** `404 Not Found`

```json
{
  "detail": "Not found."
}
```

#### Get Planting Calendar

```http
GET /api/advisory/planting-calendar/?location={village_id}
GET /api/advisory/planting-calendar/?location={village_id}&crop={crop_id}
GET /api/advisory/planting-calendar/?location={village_id}&force_refresh=true
```

Returns optimal planting window based on 10-year rainfall analysis.

**Query Parameters:**

- `location` (required): UUID of village
- `crop` (optional): UUID of crop for crop-specific recommendations
- `force_refresh` (optional): Boolean to force recalculation (default: false)

**Example:** `/api/advisory/planting-calendar/?location=8f1ad073-4ac7-450d-b569-5454e934dc56`

**Response:** `200 OK`

```json
{
  "id": "928ccdfc-105a-4b2e-84bf-fa2419f89687",
  "village": "8f1ad073-4ac7-450d-b569-5454e934dc56",
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

**With Crop Parameter:**

```json
{
  "id": "a28dcdfc-205b-5c3f-95cg-gb3520g90798",
  "village": "8f1ad073-4ac7-450d-b569-5454e934dc56",
  "village_name": "Area 1",
  "village_name_chichewa": "Area 1",
  "crop": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "crop_name": "Maize",
  "crop_name_chichewa": "Chimanga",
  "start_date": "2025-01-15",
  "end_date": "2025-02-14",
  "confidence_level": 0.92,
  "calculated_at": "2025-11-25T01:00:08.978912+02:00"
}
```

**Field Descriptions:**

- `start_date`: Recommended planting start date (ISO 8601 format: YYYY-MM-DD)
- `end_date`: Recommended planting end date (ISO 8601 format: YYYY-MM-DD)
- `confidence_level`: Statistical confidence (0.0 to 1.0) based on 10-year rainfall data
- `calculated_at`: Timestamp when calculation was performed (ISO 8601 with timezone)

**Error Response:** `400 Bad Request`

```json
{
  "error": "location parameter is required"
}
```

#### Get Crop Suitability

```http
GET /api/advisory/crop-suitability/?location={village_id}
```

Returns ranked list of crops by suitability score for a location based on soil, elevation, and climate data.

**Query Parameters:**

- `location` (required): UUID of village

**Example:** `/api/advisory/crop-suitability/?location=8f1ad073-4ac7-450d-b569-5454e934dc56`

**Response:** `200 OK`

```json
[
  {
    "crop_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Maize",
    "name_chichewa": "Chimanga",
    "scientific_name": "Zea mays",
    "suitability_score": 92.5,
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
  },
  {
    "crop_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "name": "Beans",
    "name_chichewa": "Nyemba",
    "scientific_name": "Phaseolus vulgaris",
    "suitability_score": 87.3,
    "soil_requirements": {
      "min_ph": 6.0,
      "max_ph": 7.5,
      "min_clay_content": 15.0,
      "max_clay_content": 35.0,
      "min_organic_carbon": 1.5
    },
    "elevation_requirements": {
      "min_elevation": 0.0,
      "max_elevation": 2500.0
    }
  },
  {
    "crop_id": "c3d4e5f6-a7b8-9012-cdef-234567890123",
    "name": "Groundnuts",
    "name_chichewa": "Mtedza",
    "scientific_name": "Arachis hypogaea",
    "suitability_score": 78.9,
    "soil_requirements": {
      "min_ph": 5.9,
      "max_ph": 7.0,
      "min_clay_content": 10.0,
      "max_clay_content": 30.0,
      "min_organic_carbon": 1.2
    },
    "elevation_requirements": {
      "min_elevation": 0.0,
      "max_elevation": 1500.0
    }
  }
]
```

**Note:** Results are sorted by `suitability_score` in descending order (highest suitability first).

**Error Response:** `400 Bad Request`

```json
{
  "error": "location parameter is required"
}
```

**Error Response:** `503 Service Unavailable`

```json
{
  "error": "External API unavailable and no cached data available"
}
```

#### Get Crop Suitability Map Data

```http
GET /api/advisory/crop-suitability-map/?crop={crop_id}&bounds={bbox}
GET /api/advisory/crop-suitability-map/?crop={crop_id}&bounds={bbox}&resolution=0.05
```

Returns grid of suitability scores for map visualization.

**Query Parameters:**

- `crop` (required): UUID of crop
- `bounds` (required): Bounding box as "min_lat,min_lon,max_lat,max_lon"
- `resolution` (optional): Grid resolution in degrees (default: 0.01)

**Example:** `/api/advisory/crop-suitability-map/?crop=a1b2c3d4-e5f6-7890-abcd-ef1234567890&bounds=-14.0,33.0,-13.0,34.0`

**Response:** `200 OK`

```json
{
  "crop_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
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
      "suitability_score": 92.5
    },
    {
      "lat": -14.0,
      "lon": 33.01,
      "suitability_score": 91.8
    },
    {
      "lat": -14.0,
      "lon": 33.02,
      "suitability_score": 90.3
    },
    {
      "lat": -13.99,
      "lon": 33.0,
      "suitability_score": 88.7
    }
  ]
}
```

**Note:** The `data` array contains grid points with suitability scores. Use this for heatmap visualization.

**Error Response:** `400 Bad Request`

```json
{
  "error": "crop and bounds parameters are required"
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
