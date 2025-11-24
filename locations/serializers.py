"""
Serializers for location models.
Converts model instances to JSON and validates input data.
"""
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import District, Village


class DistrictSerializer(GeoFeatureModelSerializer):
    """
    Serializer for District model with GeoJSON support.
    
    Validates: Requirements 1.1
    """
    class Meta:
        model = District
        geo_field = 'boundary'
        fields = ['id', 'name', 'name_chichewa', 'centroid', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DistrictListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing districts without geometry.
    
    Validates: Requirements 1.1
    """
    class Meta:
        model = District
        fields = ['id', 'name', 'name_chichewa']
        read_only_fields = ['id']


class VillageSerializer(GeoFeatureModelSerializer):
    """
    Serializer for Village model with GeoJSON support.
    
    Validates: Requirements 1.2, 1.3, 1.4
    """
    district_name = serializers.CharField(source='district.name', read_only=True)
    district_name_chichewa = serializers.CharField(source='district.name_chichewa', read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Village
        geo_field = 'location'
        fields = [
            'id', 'name', 'name_chichewa', 'district', 'district_name',
            'district_name_chichewa', 'latitude', 'longitude', 'elevation',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latitude(self, obj):
        """Extract latitude from Point geometry."""
        return obj.location.y if obj.location else None
    
    def get_longitude(self, obj):
        """Extract longitude from Point geometry."""
        return obj.location.x if obj.location else None


class VillageListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing villages without full geometry.
    
    Validates: Requirements 1.2
    """
    district_name = serializers.CharField(source='district.name', read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Village
        fields = [
            'id', 'name', 'name_chichewa', 'district', 'district_name',
            'latitude', 'longitude', 'elevation'
        ]
        read_only_fields = ['id']
    
    def get_latitude(self, obj):
        """Extract latitude from Point geometry."""
        return obj.location.y if obj.location else None
    
    def get_longitude(self, obj):
        """Extract longitude from Point geometry."""
        return obj.location.x if obj.location else None


class ReverseGeocodeSerializer(serializers.Serializer):
    """
    Serializer for reverse geocoding results.
    
    Validates: Requirements 1.4, 1.5
    """
    district = serializers.DictField()
    village = serializers.DictField()
