"""
Django management command to import elevation data from SRTM raster files.
Extracts elevation values for village locations and stores them in the Village model.

Usage:
    python manage.py import_elevation --raster <path_to_srtm.tif>
    python manage.py import_elevation --raster <path_to_srtm.tif> --update-all

Validates: Requirements 3.3, 5.3
"""

from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.gdal import GDALRaster
from django.db import transaction

from locations.models import Village


class Command(BaseCommand):
    help = 'Import elevation data from SRTM raster files and update village elevations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--raster',
            type=str,
            required=True,
            help='Path to SRTM raster file (GeoTIFF format)',
        )
        parser.add_argument(
            '--update-all',
            action='store_true',
            help='Update all villages, even those with existing elevation data',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of villages to update in each batch (default: 100)',
        )

    def handle(self, *args, **options):
        raster_path = options['raster']
        update_all = options['update_all']
        batch_size = options['batch_size']

        # Validate raster file exists
        path = Path(raster_path)
        if not path.exists():
            raise CommandError(f'Raster file not found: {raster_path}')

        self.stdout.write(f'Loading raster file: {raster_path}')
        
        try:
            # Load raster using GDAL
            raster = GDALRaster(str(path), write=False)
            
            # Display raster information
            self.stdout.write(f'Raster info:')
            self.stdout.write(f'  Size: {raster.width} x {raster.height}')
            self.stdout.write(f'  Bands: {len(raster.bands)}')
            self.stdout.write(f'  SRID: {raster.srid}')
            
            # Validate raster has at least one band
            if len(raster.bands) == 0:
                raise CommandError('Raster file has no bands')
            
            # Get the first band (elevation data)
            band = raster.bands[0]
            self.stdout.write(f'  NoData value: {band.nodata_value}')
            
        except Exception as e:
            raise CommandError(f'Error loading raster file: {e}')

        # Get villages to update
        if update_all:
            villages = Village.objects.all()
            self.stdout.write(f'Updating elevation for all {villages.count()} villages')
        else:
            villages = Village.objects.filter(elevation__isnull=True)
            self.stdout.write(
                f'Updating elevation for {villages.count()} villages without elevation data'
            )

        if villages.count() == 0:
            self.stdout.write(self.style.SUCCESS('No villages to update'))
            return

        # Process villages in batches
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        villages_to_update = []
        
        for village in villages.iterator(chunk_size=batch_size):
            try:
                # Extract elevation at village location
                elevation = self.extract_elevation(raster, village)
                
                if elevation is not None:
                    village.elevation = elevation
                    villages_to_update.append(village)
                    updated_count += 1
                    
                    # Batch update when we reach batch_size
                    if len(villages_to_update) >= batch_size:
                        self.bulk_update_villages(villages_to_update)
                        villages_to_update = []
                else:
                    skipped_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Error processing {village.name}: {e}'
                    )
                )
                error_count += 1
                continue

        # Update remaining villages
        if villages_to_update:
            self.bulk_update_villages(villages_to_update)

        # Display summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nElevation import complete:\n'
                f'  Updated: {updated_count}\n'
                f'  Skipped (no data): {skipped_count}\n'
                f'  Errors: {error_count}'
            )
        )

    def extract_elevation(
        self,
        raster: GDALRaster,
        village: Village
    ) -> Optional[float]:
        """
        Extract elevation value from raster at village location.
        
        Args:
            raster: GDAL raster object
            village: Village model instance
            
        Returns:
            Elevation in meters, or None if no data available
        """
        try:
            # Get village coordinates
            lon = village.location.x
            lat = village.location.y
            
            # Transform coordinates to raster's coordinate system if needed
            # SRTM data is typically in WGS84 (EPSG:4326), same as our data
            
            # Get pixel coordinates
            # GDAL uses (x, y) which corresponds to (lon, lat)
            pixel_x, pixel_y = raster.transform.inverse_transform(lon, lat)
            
            # Check if coordinates are within raster bounds
            if (pixel_x < 0 or pixel_x >= raster.width or
                pixel_y < 0 or pixel_y >= raster.height):
                self.stdout.write(
                    self.style.WARNING(
                        f'{village.name} is outside raster bounds '
                        f'(lon={lon:.4f}, lat={lat:.4f})'
                    )
                )
                return None
            
            # Get elevation value from first band
            band = raster.bands[0]
            
            # Read the pixel value
            # Note: pixel coordinates need to be integers
            pixel_x_int = int(pixel_x)
            pixel_y_int = int(pixel_y)
            
            # Get the elevation value
            elevation = band.data(offset=(pixel_x_int, pixel_y_int), size=(1, 1))[0, 0]
            
            # Check for NoData value
            if band.nodata_value is not None and elevation == band.nodata_value:
                self.stdout.write(
                    self.style.WARNING(
                        f'{village.name} has NoData value at location '
                        f'(lon={lon:.4f}, lat={lat:.4f})'
                    )
                )
                return None
            
            # Validate elevation is reasonable (Malawi elevation range: 0-3000m)
            if elevation < -100 or elevation > 4000:
                self.stdout.write(
                    self.style.WARNING(
                        f'{village.name} has unrealistic elevation: {elevation}m'
                    )
                )
                return None
            
            return float(elevation)
            
        except Exception as e:
            raise Exception(f'Error extracting elevation: {e}')

    @transaction.atomic
    def bulk_update_villages(self, villages: list) -> None:
        """
        Bulk update village elevations in database.
        
        Args:
            villages: List of Village instances to update
        """
        if villages:
            Village.objects.bulk_update(villages, ['elevation'])
            self.stdout.write(f'  Updated batch of {len(villages)} villages')
