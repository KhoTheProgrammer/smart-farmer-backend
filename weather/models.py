"""
Weather models for Mlimi Wanzeru platform.
Includes WeatherCache model for caching NASA POWER API responses.
Includes PlantingWindow model for storing calculated planting dates.
"""
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta


class WeatherCache(models.Model):
    """
    Cache model for storing weather data from NASA POWER API.
    Implements 24-hour TTL for cached data.
    
    Validates: Requirements 9.3, 9.4
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location_key = models.CharField(max_length=100, unique=True, db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    data = models.JSONField()
    cached_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weather_cache'
        ordering = ['-cached_at']
        indexes = [
            models.Index(fields=['location_key']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Weather cache for {self.location_key}"

    def save(self, *args, **kwargs):
        """
        Override save to automatically set expiration time to 24 hours from now.
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        """
        Check if the cached data has expired.
        
        Returns:
            True if expired, False otherwise
        """
        return timezone.now() > self.expires_at

    @classmethod
    def get_cached_data(cls, location_key: str):
        """
        Retrieve cached weather data if it exists and is not expired.
        
        Args:
            location_key: Unique key for the location (e.g., "lat_lon")
            
        Returns:
            WeatherCache object if valid cache exists, None otherwise
        """
        try:
            cache = cls.objects.get(location_key=location_key)
            if not cache.is_expired():
                return cache
            # Delete expired cache
            cache.delete()
            return None
        except cls.DoesNotExist:
            return None

    @classmethod
    def create_location_key(cls, lat: float, lon: float) -> str:
        """
        Create a standardized location key from coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Location key string
        """
        # Round to 2 decimal places for cache key consistency
        return f"{lat:.2f}_{lon:.2f}"


class PlantingWindow(models.Model):
    """
    Model for storing calculated optimal planting windows.
    Based on rainfall pattern analysis and rainy season onset.
    
    Validates: Requirements 2.2, 2.3, 2.4, 2.5
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    village = models.ForeignKey(
        'locations.Village',
        on_delete=models.CASCADE,
        related_name='planting_windows'
    )
    crop = models.ForeignKey(
        'weather.Crop',
        on_delete=models.CASCADE,
        related_name='planting_windows',
        null=True,
        blank=True
    )
    start_date = models.DateField()
    end_date = models.DateField()
    confidence_level = models.FloatField()  # 0-1 range
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'planting_windows'
        ordering = ['-calculated_at']
        indexes = [
            models.Index(fields=['village']),
            models.Index(fields=['crop']),
            models.Index(fields=['calculated_at']),
        ]

    def __str__(self):
        crop_name = self.crop.name if self.crop else "General"
        return f"Planting window for {self.village.name} - {crop_name}"

    def clean(self):
        """Validate that start_date is before end_date."""
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date")
        if self.confidence_level < 0 or self.confidence_level > 1:
            raise ValidationError("Confidence level must be between 0 and 1")


class SoilCache(models.Model):
    """
    Cache model for storing soil data from SoilGrids API.
    Implements 24-hour TTL for cached data.
    
    Validates: Requirements 3.1, 3.2
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location_key = models.CharField(max_length=100, unique=True, db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    data = models.JSONField()
    cached_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'soil_cache'
        ordering = ['-cached_at']
        indexes = [
            models.Index(fields=['location_key']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Soil cache for {self.location_key}"

    def save(self, *args, **kwargs):
        """
        Override save to automatically set expiration time to 24 hours from now.
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        """
        Check if the cached data has expired.
        
        Returns:
            True if expired, False otherwise
        """
        return timezone.now() > self.expires_at

    @classmethod
    def get_cached_data(cls, location_key: str):
        """
        Retrieve cached soil data if it exists and is not expired.
        
        Args:
            location_key: Unique key for the location (e.g., "lat_lon")
            
        Returns:
            SoilCache object if valid cache exists, None otherwise
        """
        try:
            cache = cls.objects.get(location_key=location_key)
            if not cache.is_expired():
                return cache
            # Delete expired cache
            cache.delete()
            return None
        except cls.DoesNotExist:
            return None

    @classmethod
    def create_location_key(cls, lat: float, lon: float) -> str:
        """
        Create a standardized location key from coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Location key string
        """
        # Round to 2 decimal places for cache key consistency
        return f"{lat:.2f}_{lon:.2f}"


class Crop(models.Model):
    """
    Model for storing crop information and requirements.
    Used for crop suitability analysis and planting recommendations.
    
    Validates: Requirements 3.4, 3.5, 3.6
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    name_chichewa = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=200)

    # Soil requirements
    min_ph = models.FloatField()
    max_ph = models.FloatField()
    min_clay_content = models.FloatField()  # percentage
    max_clay_content = models.FloatField()
    min_organic_carbon = models.FloatField()

    # Climate requirements
    min_rainfall = models.FloatField()  # mm per season
    max_rainfall = models.FloatField()
    min_temperature = models.FloatField()  # celsius
    max_temperature = models.FloatField()

    # Elevation requirements
    min_elevation = models.FloatField()  # meters
    max_elevation = models.FloatField()

    growing_season_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crops'
        ordering = ['name']

    def __str__(self):
        return self.name
