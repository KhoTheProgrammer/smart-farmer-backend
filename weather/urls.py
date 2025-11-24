"""
URL configuration for weather/advisory app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CropViewSet,
    PlantingCalendarView,
    CropSuitabilityView,
    CropSuitabilityMapView
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'crops', CropViewSet, basename='crop')

urlpatterns = [
    path('', include(router.urls)),
    path('planting-calendar/', PlantingCalendarView.as_view(), name='planting-calendar'),
    path('crop-suitability/', CropSuitabilityView.as_view(), name='crop-suitability'),
    path('crop-suitability-map/', CropSuitabilityMapView.as_view(), name='crop-suitability-map'),
]
