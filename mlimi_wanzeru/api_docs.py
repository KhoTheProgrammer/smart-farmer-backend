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
        </style>
    </head>
    <body>
        <h1>Mlimi Wanzeru API Documentation</h1>
        <p>RESTful API for the Smart Farmer platform providing location-based agricultural advisory services.</p>
        
        <h2>Location Endpoints</h2>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/districts/</span></h3>
            <p>List all districts in Malawi.</p>
            <p><strong>Returns:</strong> Array of district objects with id, name, and name_chichewa</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/districts/{id}/</span></h3>
            <p>Get detailed information about a specific district including boundary geometry.</p>
            <p><strong>Returns:</strong> District object with GeoJSON boundary</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/districts/{id}/villages/</span></h3>
            <p>Get all villages within a specific district.</p>
            <p><strong>Returns:</strong> Array of village objects</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/locations/villages/</span></h3>
            <p>List all villages. Can be filtered by district.</p>
            <div class="params">
                <div class="param">
                    <span class="param-name">district</span> (optional): UUID of district to filter by
                </div>
            </div>
            <p><strong>Returns:</strong> Array of village objects</p>
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
            <p><strong>Returns:</strong> District and village information for the location</p>
        </div>
        
        <h2>Agricultural Advisory Endpoints</h2>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/advisory/crops/</span></h3>
            <p>List all crops in the database with their requirements.</p>
            <p><strong>Returns:</strong> Array of crop objects</p>
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
            <p><strong>Returns:</strong> Planting window with start_date, end_date, and confidence_level</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/advisory/crop-suitability/</span></h3>
            <p>Get ranked list of crops by suitability score for a location.</p>
            <div class="params">
                <div class="param">
                    <span class="param-name">location</span> (required): UUID of village
                </div>
            </div>
            <p><strong>Returns:</strong> Array of crops ranked by suitability score (0-100)</p>
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
