"""
Admin configuration for location models.
"""
from django.contrib.gis import admin
from .models import District, Village


@admin.register(District)
class DistrictAdmin(admin.GISModelAdmin):
    """Admin interface for District model."""
    list_display = ['name', 'name_chichewa', 'created_at']
    search_fields = ['name', 'name_chichewa']
    readonly_fields = ['id', 'created_at', 'updated_at']
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 6,
            'default_lon': 34.0,
            'default_lat': -13.5,
        },
    }


@admin.register(Village)
class VillageAdmin(admin.GISModelAdmin):
    """Admin interface for Village model."""
    list_display = ['name', 'name_chichewa', 'district', 'elevation', 'created_at']
    list_filter = ['district']
    search_fields = ['name', 'name_chichewa', 'district__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['district']
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 8,
            'default_lon': 34.0,
            'default_lat': -13.5,
        },
    }
