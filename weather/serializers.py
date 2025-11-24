"""
Serializers for weather and crop models.
Converts model instances to JSON and validates input data.
"""
from rest_framework import serializers
from .models import Crop, PlantingWindow, WeatherCache, SoilCache


class CropSerializer(serializers.ModelSerializer):
    """
    Serializer for Crop model.
    
    Validates: Requirements 3.4, 3.5, 3.6
    """
    class Meta:
        model = Crop
        fields = [
            'id', 'name', 'name_chichewa', 'scientific_name',
            'min_ph', 'max_ph', 'min_clay_content', 'max_clay_content',
            'min_organic_carbon', 'min_rainfall', 'max_rainfall',
            'min_temperature', 'max_temperature', 'min_elevation',
            'max_elevation', 'growing_season_days'
        ]
        read_only_fields = ['id']


class PlantingWindowSerializer(serializers.ModelSerializer):
    """
    Serializer for PlantingWindow model.
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
    """
    village_name = serializers.CharField(source='village.name', read_only=True)
    village_name_chichewa = serializers.CharField(source='village.name_chichewa', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True, allow_null=True)
    crop_name_chichewa = serializers.CharField(source='crop.name_chichewa', read_only=True, allow_null=True)
    
    class Meta:
        model = PlantingWindow
        fields = [
            'id', 'village', 'village_name', 'village_name_chichewa',
            'crop', 'crop_name', 'crop_name_chichewa',
            'start_date', 'end_date', 'confidence_level', 'calculated_at'
        ]
        read_only_fields = ['id', 'calculated_at']


class CropSuitabilitySerializer(serializers.Serializer):
    """
    Serializer for crop suitability results.
    
    Validates: Requirements 3.4, 3.5, 3.6
    """
    crop_id = serializers.UUIDField()
    name = serializers.CharField()
    name_chichewa = serializers.CharField()
    scientific_name = serializers.CharField()
    suitability_score = serializers.FloatField()
    soil_requirements = serializers.DictField()
    elevation_requirements = serializers.DictField()


class SuitabilityMapDataSerializer(serializers.Serializer):
    """
    Serializer for crop suitability map data points.
    
    Validates: Requirements 4.1, 4.2, 4.3, 4.4
    """
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    suitability_score = serializers.FloatField()


class WeatherCacheSerializer(serializers.ModelSerializer):
    """
    Serializer for WeatherCache model (admin use).
    """
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = WeatherCache
        fields = [
            'id', 'location_key', 'latitude', 'longitude',
            'data', 'cached_at', 'expires_at', 'is_expired'
        ]
        read_only_fields = ['id', 'cached_at']
    
    def get_is_expired(self, obj):
        """Check if cache is expired."""
        return obj.is_expired()


class SoilCacheSerializer(serializers.ModelSerializer):
    """
    Serializer for SoilCache model (admin use).
    """
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = SoilCache
        fields = [
            'id', 'location_key', 'latitude', 'longitude',
            'data', 'cached_at', 'expires_at', 'is_expired'
        ]
        read_only_fields = ['id', 'cached_at']
    
    def get_is_expired(self, obj):
        """Check if cache is expired."""
        return obj.is_expired()
