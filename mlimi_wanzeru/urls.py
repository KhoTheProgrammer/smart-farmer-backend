"""
URL configuration for mlimi_wanzeru project.

API Endpoints:
    /api/locations/ - Location endpoints (districts, villages, reverse geocode)
    /api/advisory/ - Agricultural advisory endpoints (planting calendar, crop suitability)
"""
from django.contrib import admin
from django.urls import path, include
from .api_docs import api_documentation

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_documentation, name='api-docs'),
    path('api/locations/', include('locations.urls')),
    path('api/advisory/', include('weather.urls')),
]
