"""
Admin interface for weather models.
"""
from django.contrib import admin
from .models import WeatherCache, SoilCache, PlantingWindow, Crop


@admin.register(WeatherCache)
class WeatherCacheAdmin(admin.ModelAdmin):
    """
    Admin interface for WeatherCache model.
    """
    list_display = ['location_key', 'latitude', 'longitude', 'cached_at', 'expires_at', 'is_expired']
    list_filter = ['cached_at', 'expires_at']
    search_fields = ['location_key']
    readonly_fields = ['id', 'cached_at', 'created_at']
    
    def is_expired(self, obj):
        """Display whether cache is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(SoilCache)
class SoilCacheAdmin(admin.ModelAdmin):
    """
    Admin interface for SoilCache model.
    """
    list_display = ['location_key', 'latitude', 'longitude', 'cached_at', 'expires_at', 'is_expired']
    list_filter = ['cached_at', 'expires_at']
    search_fields = ['location_key']
    readonly_fields = ['id', 'cached_at', 'created_at']
    
    def is_expired(self, obj):
        """Display whether cache is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(PlantingWindow)
class PlantingWindowAdmin(admin.ModelAdmin):
    """
    Admin interface for PlantingWindow model.
    """
    list_display = ['village', 'crop', 'start_date', 'end_date', 'confidence_level', 'calculated_at']
    list_filter = ['calculated_at', 'crop']
    search_fields = ['village__name', 'crop__name']
    readonly_fields = ['id', 'calculated_at', 'created_at']
    autocomplete_fields = ['village', 'crop']


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    """
    Admin interface for Crop model.
    """
    list_display = ['name', 'name_chichewa', 'scientific_name', 'growing_season_days']
    search_fields = ['name', 'name_chichewa', 'scientific_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'name_chichewa', 'scientific_name', 'growing_season_days')
        }),
        ('Soil Requirements', {
            'fields': ('min_ph', 'max_ph', 'min_clay_content', 'max_clay_content', 'min_organic_carbon')
        }),
        ('Climate Requirements', {
            'fields': ('min_rainfall', 'max_rainfall', 'min_temperature', 'max_temperature')
        }),
        ('Elevation Requirements', {
            'fields': ('min_elevation', 'max_elevation')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
