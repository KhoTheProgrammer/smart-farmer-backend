"""
Django management command to import administrative boundaries from GeoJSON.
Validates CRS and stores district polygons and village points in PostGIS.

Usage:
    python manage.py import_boundaries --districts <path_to_districts.geojson>
    python manage.py import_boundaries --villages <path_to_villages.geojson>
    python manage.py import_boundaries --districts <districts.geojson> --villages <villages.geojson>

Validates: Requirements 5.1, 5.2, 5.4
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point
from django.db import transaction

from locations.models import District, Village


class Command(BaseCommand):
    help = 'Import administrative boundaries from GeoJSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--districts',
            type=str,
            help='Path to GeoJSON file containing district boundaries',
        )
        parser.add_argument(
            '--villages',
            type=str,
            help='Path to GeoJSON file containing village points',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import',
        )

    def handle(self, *args, **options):
        districts_path = options.get('districts')
        villages_path = options.get('villages')
        clear_data = options.get('clear', False)

        if not districts_path and not villages_path:
            raise CommandError(
                'Please provide at least one of --districts or --villages'
            )

        # Clear existing data if requested
        if clear_data:
            self.stdout.write('Clearing existing data...')
            Village.objects.all().delete()
            District.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        # Import districts
        if districts_path:
            self.stdout.write(f'Importing districts from {districts_path}...')
            districts_imported = self.import_districts(districts_path)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {districts_imported} districts')
            )

        # Import villages
        if villages_path:
            self.stdout.write(f'Importing villages from {villages_path}...')
            villages_imported = self.import_villages(villages_path)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {villages_imported} villages')
            )

    def load_geojson(self, file_path: str) -> Dict[str, Any]:
        """
        Load and parse GeoJSON file.
        
        Args:
            file_path: Path to GeoJSON file
            
        Returns:
            Parsed GeoJSON dictionary
            
        Raises:
            CommandError: If file cannot be read or parsed
        """
        path = Path(file_path)
        
        if not path.exists():
            raise CommandError(f'File not found: {file_path}')
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON in {file_path}: {e}')
        except Exception as e:
            raise CommandError(f'Error reading {file_path}: {e}')
        
        # Validate GeoJSON structure
        if not isinstance(data, dict):
            raise CommandError(f'Invalid GeoJSON: root must be an object')
        
        if data.get('type') not in ['FeatureCollection', 'Feature']:
            raise CommandError(
                f'Invalid GeoJSON: type must be FeatureCollection or Feature, '
                f'got {data.get("type")}'
            )
        
        return data

    def validate_crs(self, geojson: Dict[str, Any], file_path: str) -> None:
        """
        Validate that the CRS is WGS84 (EPSG:4326).
        
        Args:
            geojson: Parsed GeoJSON dictionary
            file_path: Path to file (for error messages)
            
        Raises:
            CommandError: If CRS is not WGS84
            
        Validates: Requirements 5.4
        """
        # Check for explicit CRS definition
        crs = geojson.get('crs')
        
        if crs:
            # CRS is explicitly defined
            crs_type = crs.get('type')
            properties = crs.get('properties', {})
            
            if crs_type == 'name':
                name = properties.get('name', '').upper()
                # Accept various forms of WGS84/EPSG:4326
                valid_names = [
                    'EPSG:4326',
                    'URN:OGC:DEF:CRS:EPSG::4326',
                    'URN:OGC:DEF:CRS:OGC:1.3:CRS84',
                    'WGS84',
                ]
                if not any(valid in name for valid in valid_names):
                    raise CommandError(
                        f'Invalid CRS in {file_path}: {name}. '
                        f'Only WGS84 (EPSG:4326) is supported.'
                    )
            elif crs_type == 'link':
                # For linked CRS, we'll assume it's correct and let GEOS validate
                self.stdout.write(
                    self.style.WARNING(
                        f'CRS is defined as a link in {file_path}. '
                        f'Assuming WGS84 (EPSG:4326).'
                    )
                )
        else:
            # No explicit CRS - GeoJSON spec says this means WGS84
            self.stdout.write(
                f'No explicit CRS in {file_path}, assuming WGS84 (EPSG:4326) '
                f'per GeoJSON specification'
            )

    def get_feature_property(
        self,
        properties: Dict[str, Any],
        possible_keys: list,
        default: Optional[str] = None
    ) -> Optional[str]:
        """
        Get a property value from a feature, trying multiple possible keys.
        
        Args:
            properties: Feature properties dictionary
            possible_keys: List of possible property keys to try
            default: Default value if no key is found
            
        Returns:
            Property value or default
        """
        for key in possible_keys:
            if key in properties:
                value = properties[key]
                if value:
                    return str(value).strip()
        return default

    @transaction.atomic
    def import_districts(self, file_path: str) -> int:
        """
        Import district boundaries from GeoJSON file.
        
        Args:
            file_path: Path to GeoJSON file
            
        Returns:
            Number of districts imported
            
        Validates: Requirements 5.1, 5.2, 5.4
        """
        geojson = self.load_geojson(file_path)
        self.validate_crs(geojson, file_path)
        
        # Get features
        if geojson['type'] == 'FeatureCollection':
            features = geojson.get('features', [])
        else:
            features = [geojson]
        
        if not features:
            raise CommandError(f'No features found in {file_path}')
        
        districts_created = 0
        districts_updated = 0
        
        for feature in features:
            if feature.get('type') != 'Feature':
                self.stdout.write(
                    self.style.WARNING(f'Skipping non-feature: {feature.get("type")}')
                )
                continue
            
            geometry = feature.get('geometry')
            properties = feature.get('properties', {})
            
            if not geometry:
                self.stdout.write(
                    self.style.WARNING('Skipping feature with no geometry')
                )
                continue
            
            # Extract district name (try various common property names)
            name = self.get_feature_property(
                properties,
                ['name', 'NAME', 'district', 'DISTRICT', 'ADM2_EN', 'ADM1_EN', 'NAME_1', 'NAME_2']
            )
            
            if not name:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping feature with no name: {properties}'
                    )
                )
                continue
            
            # Extract Chichewa name (optional)
            name_chichewa = self.get_feature_property(
                properties,
                ['name_chichewa', 'name_local', 'NAME_LOCAL', 'ADM2_NY', 'ADM1_NY'],
                default=name  # Fallback to English name
            )
            
            try:
                # Parse geometry
                geom = GEOSGeometry(json.dumps(geometry), srid=4326)
                
                # Ensure it's a MultiPolygon
                if geom.geom_type == 'Polygon':
                    geom = MultiPolygon(geom, srid=4326)
                elif geom.geom_type != 'MultiPolygon':
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping {name}: geometry type {geom.geom_type} '
                            f'is not Polygon or MultiPolygon'
                        )
                    )
                    continue
                
                # Validate geometry
                if not geom.valid:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Invalid geometry for {name}, attempting to fix...'
                        )
                    )
                    geom = geom.buffer(0)  # Try to fix invalid geometry
                    
                    if not geom.valid:
                        self.stdout.write(
                            self.style.ERROR(f'Could not fix geometry for {name}, skipping')
                        )
                        continue
                
                # Calculate centroid
                centroid = geom.centroid
                
                # Create or update district
                district, created = District.objects.update_or_create(
                    name=name,
                    defaults={
                        'name_chichewa': name_chichewa,
                        'boundary': geom,
                        'centroid': centroid,
                    }
                )
                
                if created:
                    districts_created += 1
                    self.stdout.write(f'  Created district: {name}')
                else:
                    districts_updated += 1
                    self.stdout.write(f'  Updated district: {name}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {name}: {e}')
                )
                continue
        
        if districts_updated > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {districts_created}, updated {districts_updated} districts'
                )
            )
        
        return districts_created + districts_updated

    @transaction.atomic
    def import_villages(self, file_path: str) -> int:
        """
        Import village points from GeoJSON file.
        
        Args:
            file_path: Path to GeoJSON file
            
        Returns:
            Number of villages imported
            
        Validates: Requirements 5.1, 5.2, 5.4
        """
        geojson = self.load_geojson(file_path)
        self.validate_crs(geojson, file_path)
        
        # Get features
        if geojson['type'] == 'FeatureCollection':
            features = geojson.get('features', [])
        else:
            features = [geojson]
        
        if not features:
            raise CommandError(f'No features found in {file_path}')
        
        # Get all districts for lookup
        districts = {d.name.lower(): d for d in District.objects.all()}
        
        if not districts:
            raise CommandError(
                'No districts found in database. Please import districts first.'
            )
        
        villages_created = 0
        villages_updated = 0
        villages_skipped = 0
        
        for feature in features:
            if feature.get('type') != 'Feature':
                continue
            
            geometry = feature.get('geometry')
            properties = feature.get('properties', {})
            
            if not geometry:
                villages_skipped += 1
                continue
            
            # Extract village name
            name = self.get_feature_property(
                properties,
                ['name', 'NAME', 'village', 'VILLAGE', 'ADM3_EN', 'ADM2_EN', 'NAME_2', 'NAME_3']
            )
            
            if not name:
                villages_skipped += 1
                continue
            
            # Extract Chichewa name
            name_chichewa = self.get_feature_property(
                properties,
                ['name_chichewa', 'name_local', 'NAME_LOCAL', 'ADM3_NY', 'ADM2_NY'],
                default=name
            )
            
            # Extract district name
            district_name = self.get_feature_property(
                properties,
                ['district', 'DISTRICT', 'district_name', 'ADM2_EN', 'ADM1_EN', 'NAME_1', 'NAME_2']
            )
            
            if not district_name:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping {name}: no district information'
                    )
                )
                villages_skipped += 1
                continue
            
            # Find matching district
            district = districts.get(district_name.lower())
            
            if not district:
                # Try to find district by checking if point is within any district boundary
                try:
                    geom = GEOSGeometry(json.dumps(geometry), srid=4326)
                    if geom.geom_type == 'Point':
                        district = District.objects.filter(
                            boundary__contains=geom
                        ).first()
                except Exception:
                    pass
                
                if not district:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping {name}: district "{district_name}" not found'
                        )
                    )
                    villages_skipped += 1
                    continue
            
            try:
                # Parse geometry
                geom = GEOSGeometry(json.dumps(geometry), srid=4326)
                
                # Ensure it's a Point
                if geom.geom_type != 'Point':
                    # Try to get centroid if it's a polygon
                    if geom.geom_type in ['Polygon', 'MultiPolygon']:
                        geom = geom.centroid
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Skipping {name}: geometry type {geom.geom_type} '
                                f'cannot be converted to Point'
                            )
                        )
                        villages_skipped += 1
                        continue
                
                # Validate geometry
                if not geom.valid:
                    self.stdout.write(
                        self.style.ERROR(f'Invalid geometry for {name}, skipping')
                    )
                    villages_skipped += 1
                    continue
                
                # Create or update village
                village, created = Village.objects.update_or_create(
                    name=name,
                    district=district,
                    defaults={
                        'name_chichewa': name_chichewa,
                        'location': geom,
                    }
                )
                
                if created:
                    villages_created += 1
                else:
                    villages_updated += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {name}: {e}')
                )
                villages_skipped += 1
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Created {villages_created}, updated {villages_updated}, '
                f'skipped {villages_skipped} villages'
            )
        )
        
        return villages_created + villages_updated

