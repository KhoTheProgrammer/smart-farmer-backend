"""
Location services for querying districts and villages.
Provides methods for location lookups and spatial queries.
"""
from typing import List, Optional, Tuple
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import District, Village


class LocationService:
    """
    Service class for handling location-related queries.
    Provides methods for district/village lookups and reverse geocoding.
    """

    @staticmethod
    def get_districts() -> List[District]:
        """
        Retrieve all districts with their boundaries.
        
        Returns:
            List of all District objects ordered by name
        
        Validates: Requirements 1.1
        """
        return list(District.objects.all())

    @staticmethod
    def get_villages(district_id: str) -> List[Village]:
        """
        Retrieve all villages within a specific district.
        
        Args:
            district_id: UUID of the district
            
        Returns:
            List of Village objects belonging to the district
            
        Validates: Requirements 1.2
        """
        return list(Village.objects.filter(district_id=district_id).select_related('district'))

    @staticmethod
    def get_coordinates(village_id: str) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude coordinates for a village.
        
        Args:
            village_id: UUID of the village
            
        Returns:
            Tuple of (latitude, longitude) or None if village not found
            
        Validates: Requirements 1.3, 1.4
        """
        try:
            village = Village.objects.get(id=village_id)
            # PostGIS Point stores as (longitude, latitude) but we return (lat, lon)
            return (village.location.y, village.location.x)
        except Village.DoesNotExist:
            return None

    @staticmethod
    def get_village_by_id(village_id: str) -> Optional[Village]:
        """
        Retrieve a village by its ID.
        
        Args:
            village_id: UUID of the village
            
        Returns:
            Village object or None if not found
        """
        try:
            return Village.objects.select_related('district').get(id=village_id)
        except Village.DoesNotExist:
            return None

    @staticmethod
    def get_district_by_id(district_id: str) -> Optional[District]:
        """
        Retrieve a district by its ID.
        
        Args:
            district_id: UUID of the district
            
        Returns:
            District object or None if not found
        """
        try:
            return District.objects.get(id=district_id)
        except District.DoesNotExist:
            return None

    @staticmethod
    def get_location_by_point(lat: float, lon: float) -> Optional[dict]:
        """
        Reverse geocoding: find district and village containing a point.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            
        Returns:
            Dictionary with district and village info, or None if not found
            
        Validates: Requirements 1.4, 1.5
        """
        # Validate coordinate ranges
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return None
            
        point = Point(lon, lat, srid=4326)
        
        # Find district containing the point
        district = District.objects.filter(boundary__contains=point).first()
        
        if not district:
            return None
        
        # Find nearest village in the district
        village = (
            Village.objects
            .filter(district=district)
            .annotate(distance=Distance('location', point))
            .order_by('distance')
            .first()
        )
        
        result = {
            'district': {
                'id': str(district.id),
                'name': district.name,
                'name_chichewa': district.name_chichewa,
            }
        }
        
        if village:
            result['village'] = {
                'id': str(village.id),
                'name': village.name,
                'name_chichewa': village.name_chichewa,
                'latitude': village.location.y,
                'longitude': village.location.x,
                'elevation': village.elevation,
            }
        else:
            # Fallback to district centroid if no village found
            result['village'] = {
                'id': None,
                'name': f"{district.name} (District Center)",
                'name_chichewa': f"{district.name_chichewa} (District Center)",
                'latitude': district.centroid.y,
                'longitude': district.centroid.x,
                'elevation': None,
            }
        
        return result

    @staticmethod
    def get_villages_near_point(lat: float, lon: float, radius_km: float = 50) -> List[Village]:
        """
        Find villages within a specified radius of a point.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            radius_km: Search radius in kilometers (default: 50)
            
        Returns:
            List of Village objects within the radius, ordered by distance
        """
        point = Point(lon, lat, srid=4326)
        
        # Convert km to meters for ST_DWithin
        radius_m = radius_km * 1000
        
        villages = (
            Village.objects
            .filter(location__dwithin=(point, radius_m))
            .annotate(distance=Distance('location', point))
            .order_by('distance')
            .select_related('district')
        )
        
        return list(villages)
