"""
API views for agricultural advisory endpoints.
Provides REST API for planting calendar and crop suitability.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from locations.models import Village, District
from .models import Crop, PlantingWindow
from .serializers import (
    CropSerializer,
    PlantingWindowSerializer,
    CropSuitabilitySerializer,
    SuitabilityMapDataSerializer
)
from .services import (
    PlantingCalendarService,
    CropSuitabilityService,
    WeatherServiceError,
    CropSuitabilityServiceError
)
import logging

logger = logging.getLogger(__name__)


class CropViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Crop model.
    Provides list and retrieve endpoints for crops.
    
    Validates: Requirements 3.4, 3.5, 3.6
    """
    queryset = Crop.objects.all()
    serializer_class = CropSerializer


class PlantingCalendarView(APIView):
    """
    API view for planting calendar information.
    Returns optimal planting windows based on rainfall analysis.
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
    """
    
    def get(self, request):
        """
        Get planting calendar for a location.
        
        Endpoint: GET /api/advisory/planting-calendar/?location={village_id}&crop={crop_id}
        
        Query params:
            location: UUID of village (required)
            crop: UUID of crop (optional)
            force_refresh: Boolean to force recalculation (optional, default: false)
        
        Returns:
            Planting window with start date, end date, and confidence level
        """
        village_id = request.query_params.get('location')
        crop_id = request.query_params.get('crop')
        force_refresh = request.query_params.get('force_refresh', 'false').lower() == 'true'
        
        # Validate required parameters
        if not village_id:
            return Response(
                {'error': 'location parameter (village ID) is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get village
        village = get_object_or_404(Village, id=village_id)
        
        # Get crop if specified
        crop = None
        if crop_id:
            crop = get_object_or_404(Crop, id=crop_id)
        
        # Calculate or retrieve planting window
        try:
            planting_window = PlantingCalendarService.get_planting_window_for_village(
                village,
                crop,
                force_refresh
            )
            
            serializer = PlantingWindowSerializer(planting_window)
            return Response(serializer.data)
            
        except WeatherServiceError as e:
            logger.error(f"Weather service error: {e}")
            return Response(
                {'error': f'Failed to fetch weather data: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Failed to calculate planting window: {e}")
            return Response(
                {'error': 'Failed to calculate planting window'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CropSuitabilityView(APIView):
    """
    API view for crop suitability analysis.
    Returns ranked list of crops by suitability score.
    
    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
    """
    
    def get(self, request):
        """
        Get crop suitability rankings for a location.
        
        Endpoint: GET /api/advisory/crop-suitability/?location={village_id}
        
        Query params:
            location: UUID of village (required)
        
        Returns:
            List of crops ranked by suitability score
        """
        village_id = request.query_params.get('location')
        
        # Validate required parameters
        if not village_id:
            return Response(
                {'error': 'location parameter (village ID) is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get village
        village = get_object_or_404(Village, id=village_id)
        
        # Calculate crop suitability
        try:
            ranked_crops = CropSuitabilityService.rank_crops(village)
            
            serializer = CropSuitabilitySerializer(ranked_crops, many=True)
            return Response(serializer.data)
            
        except CropSuitabilityServiceError as e:
            logger.error(f"Crop suitability service error: {e}")
            return Response(
                {'error': f'Failed to calculate crop suitability: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Failed to calculate crop suitability: {e}")
            return Response(
                {'error': 'Failed to calculate crop suitability'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CropSuitabilityMapView(APIView):
    """
    API view for crop suitability map data.
    Returns grid of suitability scores for map visualization.
    
    Validates: Requirements 4.1, 4.2, 4.3, 4.4
    """
    
    def get(self, request):
        """
        Get crop suitability map data for visualization.
        
        Endpoint: GET /api/advisory/crop-suitability-map/?crop={crop_id}&bounds={bbox}
        
        Query params:
            crop: UUID of crop (required)
            bounds: Bounding box as "min_lat,min_lon,max_lat,max_lon" (required)
            resolution: Grid resolution in degrees (optional, default: 0.01)
        
        Returns:
            List of grid points with suitability scores
        """
        crop_id = request.query_params.get('crop')
        bounds_str = request.query_params.get('bounds')
        resolution = request.query_params.get('resolution', '0.01')
        
        # Validate required parameters
        if not crop_id:
            return Response(
                {'error': 'crop parameter (crop ID) is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not bounds_str:
            return Response(
                {'error': 'bounds parameter is required (format: min_lat,min_lon,max_lat,max_lon)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse bounds
        try:
            bounds_parts = bounds_str.split(',')
            if len(bounds_parts) != 4:
                raise ValueError("Bounds must have 4 values")
            
            bounds = {
                'min_lat': float(bounds_parts[0]),
                'min_lon': float(bounds_parts[1]),
                'max_lat': float(bounds_parts[2]),
                'max_lon': float(bounds_parts[3])
            }
            
            resolution = float(resolution)
            
        except (ValueError, IndexError) as e:
            return Response(
                {'error': f'Invalid bounds or resolution format: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get crop
        crop = get_object_or_404(Crop, id=crop_id)
        
        # Generate suitability raster
        try:
            # Note: This is a simplified implementation for the 2-week project
            # In production, this would be pre-computed and cached
            raster_data = CropSuitabilityService.generate_suitability_raster(
                crop,
                bounds,
                resolution
            )
            
            serializer = SuitabilityMapDataSerializer(raster_data, many=True)
            return Response({
                'crop_id': str(crop.id),
                'crop_name': crop.name,
                'bounds': bounds,
                'resolution': resolution,
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Failed to generate suitability map: {e}")
            return Response(
                {'error': 'Failed to generate suitability map'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
