"""
Tests for location models and import functionality.
"""
import json
import tempfile
from pathlib import Path

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.gis.geos import Point, Polygon, MultiPolygon

from .models import District, Village


class ImportBoundariesCommandTest(TestCase):
    """
    Test the import_boundaries management command.
    Validates: Requirements 5.1, 5.2, 5.4
    """

    def setUp(self):
        """Set up test data."""
        self.temp_dir = tempfile.mkdtemp()

    def create_geojson_file(self, filename, data):
        """Helper to create a temporary GeoJSON file."""
        filepath = Path(self.temp_dir) / filename
        with open(filepath, 'w') as f:
            json.dump(data, f)
        return str(filepath)

    def test_import_districts_with_valid_geojson(self):
        """Test importing districts from valid GeoJSON file."""
        geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Test District", "name_chichewa": "Test District"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[33.0, -14.0], [34.0, -14.0], [34.0, -13.0], [33.0, -13.0], [33.0, -14.0]]]
                    }
                }
            ]
        }
        
        filepath = self.create_geojson_file('districts.geojson', geojson)
        call_command('import_boundaries', districts=filepath)
        
        self.assertEqual(District.objects.count(), 1)
        district = District.objects.first()
        self.assertEqual(district.name, "Test District")
        self.assertIsNotNone(district.boundary)
        self.assertIsNotNone(district.centroid)

    def test_import_villages_with_valid_geojson(self):
        """Test importing villages from valid GeoJSON file."""
        # First create a district
        district = District.objects.create(
            name="Test District",
            name_chichewa="Test District",
            boundary=MultiPolygon(Polygon(((33.0, -14.0), (34.0, -14.0), (34.0, -13.0), (33.0, -13.0), (33.0, -14.0))), srid=4326),
            centroid=Point(33.5, -13.5, srid=4326)
        )
        
        geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Test Village",
                        "name_chichewa": "Test Village",
                        "district": "Test District"
                    },
                    "geometry": {"type": "Point", "coordinates": [33.5, -13.5]}
                }
            ]
        }
        
        filepath = self.create_geojson_file('villages.geojson', geojson)
        call_command('import_boundaries', villages=filepath)
        
        self.assertEqual(Village.objects.count(), 1)
        village = Village.objects.first()
        self.assertEqual(village.name, "Test Village")
        self.assertEqual(village.district, district)
        self.assertIsNotNone(village.location)

    def test_crs_validation_rejects_invalid_crs(self):
        """Test that invalid CRS is rejected. Validates: Requirements 5.4"""
        geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:3857"}},
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Test"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                    }
                }
            ]
        }
        
        filepath = self.create_geojson_file('invalid_crs.geojson', geojson)
        
        with self.assertRaises(CommandError) as context:
            call_command('import_boundaries', districts=filepath)
        
        self.assertIn('Invalid CRS', str(context.exception))
        self.assertIn('EPSG:4326', str(context.exception))

    def test_crs_validation_accepts_wgs84(self):
        """Test that WGS84 CRS is accepted. Validates: Requirements 5.4"""
        geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Test", "name_chichewa": "Test"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[33.0, -14.0], [34.0, -14.0], [34.0, -13.0], [33.0, -13.0], [33.0, -14.0]]]
                    }
                }
            ]
        }
        
        filepath = self.create_geojson_file('valid_crs.geojson', geojson)
        call_command('import_boundaries', districts=filepath)
        
        self.assertEqual(District.objects.count(), 1)

    def test_no_crs_defaults_to_wgs84(self):
        """Test that missing CRS defaults to WGS84. Validates: Requirements 5.4"""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Test", "name_chichewa": "Test"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[33.0, -14.0], [34.0, -14.0], [34.0, -13.0], [33.0, -13.0], [33.0, -14.0]]]
                    }
                }
            ]
        }
        
        filepath = self.create_geojson_file('no_crs.geojson', geojson)
        call_command('import_boundaries', districts=filepath)
        
        self.assertEqual(District.objects.count(), 1)
        district = District.objects.first()
        self.assertEqual(district.boundary.srid, 4326)

    def test_import_preserves_geometry_and_attributes(self):
        """Test that import preserves geometry and attributes. Validates: Requirements 5.1, 5.2"""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Lilongwe",
                        "name_chichewa": "Lilongwe"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[33.5, -14.2], [34.2, -14.2], [34.2, -13.5], [33.5, -13.5], [33.5, -14.2]]]
                    }
                }
            ]
        }
        
        filepath = self.create_geojson_file('preserve_test.geojson', geojson)
        call_command('import_boundaries', districts=filepath)
        
        district = District.objects.get(name="Lilongwe")
        self.assertEqual(district.name, "Lilongwe")
        self.assertEqual(district.name_chichewa, "Lilongwe")
        
        # Verify geometry is preserved
        self.assertTrue(district.boundary.valid)
        self.assertEqual(district.boundary.srid, 4326)
        
        # Verify centroid is calculated
        self.assertIsNotNone(district.centroid)
        self.assertTrue(-14.2 < district.centroid.y < -13.5)
        self.assertTrue(33.5 < district.centroid.x < 34.2)

    def test_clear_flag_removes_existing_data(self):
        """Test that --clear flag removes existing data."""
        # Create initial data
        District.objects.create(
            name="Old District",
            name_chichewa="Old District",
            boundary=MultiPolygon(Polygon(((33.0, -14.0), (34.0, -14.0), (34.0, -13.0), (33.0, -13.0), (33.0, -14.0))), srid=4326),
            centroid=Point(33.5, -13.5, srid=4326)
        )
        
        self.assertEqual(District.objects.count(), 1)
        
        # Import with clear flag
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "New District", "name_chichewa": "New District"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[33.0, -14.0], [34.0, -14.0], [34.0, -13.0], [33.0, -13.0], [33.0, -14.0]]]
                    }
                }
            ]
        }
        
        filepath = self.create_geojson_file('new.geojson', geojson)
        call_command('import_boundaries', districts=filepath, clear=True)
        
        self.assertEqual(District.objects.count(), 1)
        self.assertEqual(District.objects.first().name, "New District")
        self.assertFalse(District.objects.filter(name="Old District").exists())


class DistrictModelTest(TestCase):
    """Test District model functionality."""

    def test_district_creation(self):
        """Test creating a district with spatial data."""
        boundary = MultiPolygon(
            Polygon(((33.0, -14.0), (34.0, -14.0), (34.0, -13.0), (33.0, -13.0), (33.0, -14.0))),
            srid=4326
        )
        centroid = Point(33.5, -13.5, srid=4326)
        
        district = District.objects.create(
            name="Test District",
            name_chichewa="Test District",
            boundary=boundary,
            centroid=centroid
        )
        
        self.assertEqual(district.name, "Test District")
        self.assertTrue(district.boundary.valid)
        self.assertEqual(district.boundary.srid, 4326)

    def test_district_string_representation(self):
        """Test district __str__ method."""
        district = District.objects.create(
            name="Lilongwe",
            name_chichewa="Lilongwe",
            boundary=MultiPolygon(Polygon(((33.0, -14.0), (34.0, -14.0), (34.0, -13.0), (33.0, -13.0), (33.0, -14.0))), srid=4326),
            centroid=Point(33.5, -13.5, srid=4326)
        )
        
        self.assertEqual(str(district), "Lilongwe")


class VillageModelTest(TestCase):
    """Test Village model functionality."""

    def setUp(self):
        """Create a test district."""
        self.district = District.objects.create(
            name="Test District",
            name_chichewa="Test District",
            boundary=MultiPolygon(Polygon(((33.0, -14.0), (34.0, -14.0), (34.0, -13.0), (33.0, -13.0), (33.0, -14.0))), srid=4326),
            centroid=Point(33.5, -13.5, srid=4326)
        )

    def test_village_creation(self):
        """Test creating a village with spatial data."""
        location = Point(33.5, -13.5, srid=4326)
        
        village = Village.objects.create(
            name="Test Village",
            name_chichewa="Test Village",
            district=self.district,
            location=location,
            elevation=1200.0
        )
        
        self.assertEqual(village.name, "Test Village")
        self.assertEqual(village.district, self.district)
        self.assertTrue(village.location.valid)
        self.assertEqual(village.location.srid, 4326)
        self.assertEqual(village.elevation, 1200.0)

    def test_village_string_representation(self):
        """Test village __str__ method."""
        village = Village.objects.create(
            name="Kauma",
            name_chichewa="Kauma",
            district=self.district,
            location=Point(33.5, -13.5, srid=4326)
        )
        
        self.assertEqual(str(village), "Kauma (Test District)")

    def test_village_elevation_nullable(self):
        """Test that village elevation can be null."""
        village = Village.objects.create(
            name="Test Village",
            name_chichewa="Test Village",
            district=self.district,
            location=Point(33.5, -13.5, srid=4326),
            elevation=None
        )
        
        self.assertIsNone(village.elevation)
        
        # Update elevation
        village.elevation = 1500.0
        village.save()
        
        village.refresh_from_db()
        self.assertEqual(village.elevation, 1500.0)


class ImportElevationCommandTest(TestCase):
    """
    Test the import_elevation management command.
    Validates: Requirements 3.3, 5.3
    """

    def setUp(self):
        """Set up test data."""
        # Create a test district
        self.district = District.objects.create(
            name="Test District",
            name_chichewa="Test District",
            boundary=MultiPolygon(
                Polygon(((33.0, -14.0), (34.0, -14.0), (34.0, -13.0), (33.0, -13.0), (33.0, -14.0))),
                srid=4326
            ),
            centroid=Point(33.5, -13.5, srid=4326)
        )
        
        # Create test villages without elevation
        self.village1 = Village.objects.create(
            name="Village 1",
            name_chichewa="Village 1",
            district=self.district,
            location=Point(33.5, -13.5, srid=4326),
            elevation=None
        )
        
        self.village2 = Village.objects.create(
            name="Village 2",
            name_chichewa="Village 2",
            district=self.district,
            location=Point(33.7, -13.7, srid=4326),
            elevation=None
        )

    def test_command_requires_raster_argument(self):
        """Test that command requires --raster argument."""
        with self.assertRaises(CommandError):
            call_command('import_elevation')

    def test_command_rejects_nonexistent_file(self):
        """Test that command rejects non-existent raster file."""
        with self.assertRaises(CommandError) as context:
            call_command('import_elevation', raster='/nonexistent/file.tif')
        
        self.assertIn('not found', str(context.exception).lower())

    def test_elevation_field_stores_float_values(self):
        """Test that elevation field can store float values. Validates: Requirements 3.3"""
        self.village1.elevation = 1234.56
        self.village1.save()
        
        self.village1.refresh_from_db()
        self.assertEqual(self.village1.elevation, 1234.56)

    def test_villages_can_be_queried_by_elevation(self):
        """Test querying villages by elevation. Validates: Requirements 3.3"""
        # Set elevations
        self.village1.elevation = 1000.0
        self.village1.save()
        
        self.village2.elevation = 1500.0
        self.village2.save()
        
        # Query villages with elevation
        villages_with_elevation = Village.objects.filter(elevation__isnull=False)
        self.assertEqual(villages_with_elevation.count(), 2)
        
        # Query villages without elevation
        Village.objects.create(
            name="Village 3",
            name_chichewa="Village 3",
            district=self.district,
            location=Point(33.8, -13.8, srid=4326),
            elevation=None
        )
        
        villages_without_elevation = Village.objects.filter(elevation__isnull=True)
        self.assertEqual(villages_without_elevation.count(), 1)

    def test_elevation_range_validation(self):
        """Test that elevation values are within reasonable range for Malawi."""
        # Malawi elevation range: approximately 0-3000m
        # Test valid elevations
        valid_elevations = [0, 500, 1000, 1500, 2000, 2500, 3000]
        
        for elev in valid_elevations:
            self.village1.elevation = elev
            self.village1.save()
            self.village1.refresh_from_db()
            self.assertEqual(self.village1.elevation, elev)
