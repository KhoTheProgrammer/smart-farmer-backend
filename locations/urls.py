"""
URL configuration for locations app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DistrictViewSet, VillageViewSet, ReverseGeocodeView

# Create router for viewsets
router = DefaultRouter()
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'villages', VillageViewSet, basename='village')

urlpatterns = [
    path('', include(router.urls)),
    path('reverse/', ReverseGeocodeView.as_view(), name='reverse-geocode'),
]
