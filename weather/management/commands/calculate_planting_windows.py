"""
Management command to calculate planting windows for villages.
"""
from django.core.management.base import BaseCommand
from locations.models import Village, District
from weather.services import PlantingCalendarService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Calculate planting windows for villages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--district',
            type=str,
            help='Calculate for specific district (by name)',
        )
        parser.add_argument(
            '--village',
            type=str,
            help='Calculate for specific village (by name)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recalculation even if recent data exists',
        )

    def handle(self, *args, **options):
        district_name = options.get('district')
        village_name = options.get('village')
        force_refresh = options.get('force', False)

        if village_name:
            # Calculate for specific village
            try:
                village = Village.objects.get(name=village_name)
                self.stdout.write(f"Calculating planting window for {village.name}...")
                window = PlantingCalendarService.get_planting_window_for_village(
                    village, force_refresh=force_refresh
                )
                self.stdout.write(self.style.SUCCESS(
                    f"✓ {village.name}: {window.start_date} to {window.end_date} "
                    f"(confidence: {window.confidence_level:.2f})"
                ))
            except Village.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Village '{village_name}' not found"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

        elif district_name:
            # Calculate for all villages in district
            try:
                district = District.objects.get(name=district_name)
                self.stdout.write(f"Calculating planting windows for {district.name}...")
                windows = PlantingCalendarService.get_planting_windows_for_district(district)
                self.stdout.write(self.style.SUCCESS(
                    f"✓ Calculated {len(windows)} planting windows"
                ))
            except District.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"District '{district_name}' not found"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

        else:
            # Calculate for all villages
            self.stdout.write("Calculating planting windows for all villages...")
            villages = Village.objects.all()
            total = villages.count()
            success = 0
            failed = 0

            for i, village in enumerate(villages, 1):
                try:
                    self.stdout.write(f"[{i}/{total}] Processing {village.name}...")
                    window = PlantingCalendarService.get_planting_window_for_village(
                        village, force_refresh=force_refresh
                    )
                    success += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Failed: {str(e)}"))
                    failed += 1

            self.stdout.write(self.style.SUCCESS(
                f"\n✓ Complete: {success} successful, {failed} failed"
            ))
