"""
API views for location endpoints.
Provides REST API for districts, villages, and reverse geocoding.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import District, Village
from .serializers import (
    DistrictSerializer,
    DistrictListSerializer,
    VillageSerializer,
    VillageListSerializer,
    ReverseGeocodeSerializer
)
from .services import LocationService
import logging

logger = logging.getLogger(__name__)


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for District model.
    Provides list and retrieve endpoints for districts.
    
    Validates: Requirements 1.1
    """
    queryset = District.objects.all()
    
    def get_serializer_class(self):
        """Use simplified serializer for list view."""
        if self.action == 'list':
            return DistrictListSerializer
        return DistrictSerializer
    
    @action(detail=True, methods=['get'])
    def villages(self, request, pk=None):
        """
        Get all villages within a district.
        
        Endpoint: GET /api/locations/districts/{id}/villages/
        
        Validates: Requirements 1.2
        """
        district = self.get_object()
        villages = LocationService.get_villages(str(district.id))
        serializer = VillageListSerializer(villages, many=True)
        return Response(serializer.data)


class VillageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Village model.
    Provides list and retrieve endpoints for villages.
    
    Validates: Requirements 1.2, 1.3, 1.4
    """
    queryset = Village.objects.select_related('district').all()
    
    def get_serializer_class(self):
        """Use simplified serializer for list view."""
        if self.action == 'list':
            return VillageListSerializer
        return VillageSerializer
    
    def get_queryset(self):
        """
        Optionally filter villages by district.
        
        Query params:
            district: UUID of district to filter by
        """
        queryset = super().get_queryset()
        district_id = self.request.query_params.get('district', None)
        
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        
        return queryset


class ReverseGeocodeView(APIView):
    """
    API view for reverse geocoding.
    Finds district and village for given coordinates.
    
    Validates: Requirements 1.4, 1.5
    """
    
    def get(self, request):
        """
        Reverse geocode coordinates to find location.
        
        Endpoint: GET /api/locations/reverse/?lat={lat}&lon={lon}
        
        Query params:
            lat: Latitude coordinate (required)
            lon: Longitude coordinate (required)
        
        Returns:
            District and village information for the location
        """
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        
        # Validate parameters
        if not lat or not lon:
            return Response(
                {'error': 'Both lat and lon parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return Response(
                {'error': 'Invalid coordinate values. Must be numbers.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate coordinate ranges
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return Response(
                {'error': 'Coordinates out of range. Latitude must be -90 to 90, longitude -180 to 180.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform reverse geocoding
        try:
            result = LocationService.get_location_by_point(lat, lon)
            
            if result is None:
                return Response(
                    {'error': 'No location found for the given coordinates'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ReverseGeocodeSerializer(result)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Reverse geocoding failed: {e}")
            return Response(
                {'error': 'Failed to perform reverse geocoding'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
