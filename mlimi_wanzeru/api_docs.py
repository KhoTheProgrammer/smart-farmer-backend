"""
API Documentation view for Mlimi Wanzeru platform.
Provides a simple HTML page documenting all available endpoints.
"""
from django.http import HttpResponse


def api_documentation(request):
    """
    Simple API documentation page.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mlimi Wanzeru API Documentation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 { color: #2c5f2d; }
            h2 { color: #4a7c59; margin-top: 30px; }
            h3 { color: #6b8e23; }
            .endpoint {
                background: #f5f5f5;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #2c5f2d;
            }
            .method {
                display: inline-block;
                padding: 3px 8px;
                background: #2c5f2d;
                color: white;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
            }
            .path {
                font-family: monospace;
                color: #333;
            }
            .params {
                margin-top: 10px;
                padding-left: 20px;
            }
            .param {
                margin: 5px 0;
            }
            .param-name {
                font-weight: bold;
                color: #2c5f2d;
            }
            .response-example {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                margin-top: 10px;
                overflow-x: auto;
            }
            .response-example pre {
                margin: 0;
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }
            .response-label {
                font-weight: bold;
                margin-top: 10px;
                color: #2c5f2d;
            }
        </style>
    </head>
    <body>
        <h1>Mlimi Wanzeru API Documentation</h1>
        <p>RESTful API for the Smart Farmer platform providing location-based agricultural advisory services.</p>
        
        <h2>Location Endpoints</h2>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/districts/</span></h3>
            <p>List all districts in Malawi (32 total).</p>
            <p class="response-label">Response Example:</p>
            <div class="response-example">
                <pre>[
  {
    "id": "e00de446-86ac-497f-84cb-92ce85c4fd70",
    "name": "Balaka",
    "name_chichewa": "Balaka"
  },
  {
    "id": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "name": "Lilongwe City",
    "name_chichewa": "Lilongwe City"
  }
]</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/districts/{id}/</span></h3>
            <p>Get detailed information about a specific district including boundary geometry.</p>
            <p class="response-label">Response Example:</p>
            <div class="response-example">
                <pre>{
  "id": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [[[...]]]
  },
  "properties": {
    "name": "Lilongwe City",
    "name_chichewa": "Lilongwe City",
    "centroid": {
      "type": "Point",
      "coordinates": [33.7799, -13.9888]
    }
  }
}</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/districts/{id}/villages/</span></h3>
            <p>Get all villages within a specific district.</p>
            <p><strong>Returns:</strong> Array of village objects</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/villages/</span></h3>
            <p>List all villages (433 total). Can be filtered by district.</p>
            <div class="params">
                <div class="param">
                    <span class="param-name">district</span> (optional): UUID of district to filter by
                </div>
            </div>
            <p class="response-label">Response Example:</p>
            <div class="response-example">
                <pre>[
  {
    "id": "8f1ad073-4ac7-450d-b569-5454e934dc56",
    "name": "Area 1",
    "name_chichewa": "Area 1",
    "district": "3ac7e9b5-21af-4b46-86cf-9b3faa308217",
    "district_name": "Lilongwe City",
    "latitude": -14.002967594085035,
    "longitude": 33.78105170654241,
    "elevation": 1100.5
  }
]</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/villages/{id}/</span></h3>
            <p>Get detailed information about a specific village including coordinates and elevation.</p>
            <p><strong>Returns:</strong> Village object with GeoJSON location</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/reverse/</span></h3>
            <p>Reverse geocode coordinates to find district and village.</p>
            <div class="params">
                <div class="param">
                    <span class="param-name">lat</span> (required): Latitude coordinate (-90 to 90)
                </div>
                <div class="param">
                    <span class="param-name">lon</span> (required): Longitude coordinate (-180 to 180)
                </div>
            </div>
            <p class="response-label">Response Example:</p>
            <div class="response-example">
                <pre>{
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
}</pre>
            </div>
        </div>
        
        <h2>Agricultural Advisory Endpoints</h2>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/advisory/crops/</span></h3>
            <p>List all crops in the database with their requirements (6 total).</p>
            <p class="response-label">Response Example:</p>
            <div class="response-example">
                <pre>[
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
]</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/advisory/crops/{id}/</span></h3>
            <p>Get detailed information about a specific crop.</p>
            <p><strong>Returns:</strong> Crop object with soil, climate, and elevation requirements</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/advisory/planting-calendar/</span></h3>
            <p>Get optimal planting window for a location based on 10-year rainfall analysis.</p>
            <div class="params">
                <div class="param">
                    <span class="param-name">location</span> (required): UUID of village
                </div>
                <div class="param">
                    <span class="param-name">crop</span> (optional): UUID of crop
                </div>
                <div class="param">
                    <span class="param-name">force_refresh</span> (optional): Boolean to force recalculation (default: false)
                </div>
            </div>
            <p class="response-label">Response Example:</p>
            <div class="response-example">
                <pre>{
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
}</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/advisory/crop-suitability/</span></h3>
            <p>Get ranked list of crops by suitability score for a location based on soil, elevation, and climate data.</p>
            <div class="params">
                <div class="param">
                    <span class="param-name">location</span> (required): UUID of village
                </div>
            </div>
            <p class="response-label">Response Example:</p>
            <div class="response-example">
                <pre>[
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
  }
]</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/advisory/crop-suitability-map/</span></h3>
            <p>Get grid of suitability scores for map visualization.</p>
            <div class="params">
                <div class="param">
                    <span class="param-name">crop</span> (required): UUID of crop
                </div>
                <div class="param">
                    <span class="param-name">bounds</span> (required): Bounding box as "min_lat,min_lon,max_lat,max_lon"
                </div>
                <div class="param">
                    <span class="param-name">resolution</span> (optional): Grid resolution in degrees (default: 0.01)
                </div>
            </div>
            <p><strong>Returns:</strong> Array of grid points with lat, lon, and suitability_score</p>
        </div>
        
        <h2>Response Format</h2>
        <p>All endpoints return JSON. Successful responses have HTTP status 200. Errors return appropriate status codes:</p>
        <ul>
            <li><strong>400 Bad Request:</strong> Invalid parameters</li>
            <li><strong>404 Not Found:</strong> Resource not found</li>
            <li><strong>500 Internal Server Error:</strong> Server error</li>
            <li><strong>503 Service Unavailable:</strong> External API unavailable</li>
        </ul>
        
        <h2>Rate Limiting</h2>
        <p>API requests are limited to 100 requests per minute per IP address.</p>
    </body>
    </html>
    """
    return HttpResponse(html)
