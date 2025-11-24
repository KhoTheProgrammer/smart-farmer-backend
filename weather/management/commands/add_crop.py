"""
Management command to add a new crop to the database.
Usage: python manage.py add_crop --name "Rice" --chichewa "Mpunga" ...
"""
import uuid
from django.core.management.base import BaseCommand, CommandError
from weather.models import Crop


class Command(BaseCommand):
    help = 'Add a new crop to the database'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Crop name in English')
        parser.add_argument('--chichewa', type=str, required=True, help='Crop name in Chichewa')
        parser.add_argument('--scientific', type=str, required=True, help='Scientific name')
        
        # Soil requirements
        parser.add_argument('--min-ph', type=float, required=True)
        parser.add_argument('--max-ph', type=float, required=True)
        parser.add_argument('--min-clay', type=float, required=True)
        parser.add_argument('--max-clay', type=float, required=True)
        parser.add_argument('--min-organic-carbon', type=float, required=True)
        
        # Climate requirements
        parser.add_argument('--min-rainfall', type=float, required=True)
        parser.add_argument('--max-rainfall', type=float, required=True)
        parser.add_argument('--min-temp', type=float, required=True)
        parser.add_argument('--max-temp', type=float, required=True)
        
        # Elevation requirements
        parser.add_argument('--min-elevation', type=float, required=True)
        parser.add_argument('--max-elevation', type=float, required=True)
        
        parser.add_argument('--growing-days', type=int, required=True)

    def handle(self, *args, **options):
        # Check if crop already exists
        if Crop.objects.filter(name=options['name']).exists():
            raise CommandError(f"Crop '{options['name']}' already exists")
        
        # Validate ranges
        if options['min_ph'] >= options['max_ph']:
            raise CommandError("min-ph must be less than max-ph")
        if options['min_clay'] >= options['max_clay']:
            raise CommandError("min-clay must be less than max-clay")
        if options['min_rainfall'] >= options['max_rainfall']:
            raise CommandError("min-rainfall must be less than max-rainfall")
        if options['min_temp'] >= options['max_temp']:
            raise CommandError("min-temp must be less than max-temp")
        if options['min_elevation'] >= options['max_elevation']:
            raise CommandError("min-elevation must be less than max-elevation")
        
        # Create the crop
        crop = Crop.objects.create(
            id=uuid.uuid4(),
            name=options['name'],
            name_chichewa=options['chichewa'],
            scientific_name=options['scientific'],
            min_ph=options['min_ph'],
            max_ph=options['max_ph'],
            min_clay_content=options['min_clay'],
            max_clay_content=options['max_clay'],
            min_organic_carbon=options['min_organic_carbon'],
            min_rainfall=options['min_rainfall'],
            max_rainfall=options['max_rainfall'],
            min_temperature=options['min_temp'],
            max_temperature=options['max_temp'],
            min_elevation=options['min_elevation'],
            max_elevation=options['max_elevation'],
            growing_season_days=options['growing_days']
        )
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully added crop: {crop.name} ({crop.name_chichewa})")
        )
