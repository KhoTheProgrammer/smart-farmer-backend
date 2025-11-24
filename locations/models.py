"""
Location models for Mlimi Wanzeru platform.
Includes District and Village models with spatial fields.
"""
import uuid
from django.contrib.gis.db import models


class District(models.Model):
    """
    Represents an administrative district in Malawi.
    Contains spatial boundary data and centroid for location queries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    name_chichewa = models.CharField(max_length=100)
    boundary = models.MultiPolygonField(srid=4326)
    centroid = models.PointField(srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'districts'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Village(models.Model):
    """
    Represents a village within a district in Malawi.
    Contains point location data and elevation information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    name_chichewa = models.CharField(max_length=100)
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='villages'
    )
    location = models.PointField(srid=4326)
    elevation = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'villages'
        ordering = ['name']
        unique_together = [['name', 'district']]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['district']),
        ]

    def __str__(self):
        return f"{self.name} ({self.district.name})"
