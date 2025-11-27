# Generated migration for sample locations

from django.db import migrations
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
import uuid


def add_sample_locations(apps, schema_editor):
    """
    Add sample districts and villages for testing and demo purposes.
    Includes major cities and regions in Malawi.
    """
    District = apps.get_model('locations', 'District')
    Village = apps.get_model('locations', 'Village')
    
    # Sample districts with approximate boundaries and centroids
    districts_data = [
        {
            'name': 'Lilongwe',
            'name_chichewa': 'Lilongwe',
            'centroid': Point(33.7833, -13.9833),  # lon, lat
            'boundary': MultiPolygon(Polygon((
                (33.5, -14.2), (34.0, -14.2), (34.0, -13.7), (33.5, -13.7), (33.5, -14.2)
            )))
        },
        {
            'name': 'Blantyre',
            'name_chichewa': 'Blantyre',
            'centroid': Point(35.0, -15.7833),
            'boundary': MultiPolygon(Polygon((
                (34.8, -16.0), (35.2, -16.0), (35.2, -15.5), (34.8, -15.5), (34.8, -16.0)
            )))
        },
        {
            'name': 'Mzuzu',
            'name_chichewa': 'Mzuzu',
            'centroid': Point(34.0167, -11.45),
            'boundary': MultiPolygon(Polygon((
                (33.8, -11.7), (34.2, -11.7), (34.2, -11.2), (33.8, -11.2), (33.8, -11.7)
            )))
        },
        {
            'name': 'Zomba',
            'name_chichewa': 'Zomba',
            'centroid': Point(35.3167, -15.3833),
            'boundary': MultiPolygon(Polygon((
                (35.1, -15.6), (35.5, -15.6), (35.5, -15.1), (35.1, -15.1), (35.1, -15.6)
            )))
        },
        {
            'name': 'Kasungu',
            'name_chichewa': 'Kasungu',
            'centroid': Point(33.4833, -13.0333),
            'boundary': MultiPolygon(Polygon((
                (33.2, -13.3), (33.7, -13.3), (33.7, -12.7), (33.2, -12.7), (33.2, -13.3)
            )))
        },
    ]
    
    # Create districts and store references
    districts = {}
    for district_data in districts_data:
        district = District.objects.create(
            id=uuid.uuid4(),
            **district_data
        )
        districts[district.name] = district
    
    # Sample villages with locations and elevations
    villages_data = [
        # Lilongwe District
        {'name': 'Area 25', 'name_chichewa': 'Area 25', 'district': 'Lilongwe', 
         'location': Point(33.7833, -13.9833), 'elevation': 1050.0},
        {'name': 'Kauma', 'name_chichewa': 'Kauma', 'district': 'Lilongwe',
         'location': Point(33.8, -14.0), 'elevation': 1070.0},
        {'name': 'Mitundu', 'name_chichewa': 'Mitundu', 'district': 'Lilongwe',
         'location': Point(33.7, -13.95), 'elevation': 1040.0},
        
        # Blantyre District
        {'name': 'Ndirande', 'name_chichewa': 'Ndirande', 'district': 'Blantyre',
         'location': Point(35.0, -15.8), 'elevation': 1100.0},
        {'name': 'Chilomoni', 'name_chichewa': 'Chilomoni', 'district': 'Blantyre',
         'location': Point(35.02, -15.82), 'elevation': 1120.0},
        {'name': 'Bangwe', 'name_chichewa': 'Bangwe', 'district': 'Blantyre',
         'location': Point(34.98, -15.78), 'elevation': 1090.0},
        
        # Mzuzu District
        {'name': 'Chibavi', 'name_chichewa': 'Chibavi', 'district': 'Mzuzu',
         'location': Point(34.02, -11.45), 'elevation': 1280.0},
        {'name': 'Katoto', 'name_chichewa': 'Katoto', 'district': 'Mzuzu',
         'location': Point(34.0, -11.47), 'elevation': 1260.0},
        
        # Zomba District
        {'name': 'Chinamwali', 'name_chichewa': 'Chinamwali', 'district': 'Zomba',
         'location': Point(35.32, -15.38), 'elevation': 900.0},
        {'name': 'Matawale', 'name_chichewa': 'Matawale', 'district': 'Zomba',
         'location': Point(35.3, -15.4), 'elevation': 920.0},
        
        # Kasungu District
        {'name': 'Chulu', 'name_chichewa': 'Chulu', 'district': 'Kasungu',
         'location': Point(33.48, -13.03), 'elevation': 1100.0},
        {'name': 'Santhe', 'name_chichewa': 'Santhe', 'district': 'Kasungu',
         'location': Point(33.5, -13.05), 'elevation': 1110.0},
    ]
    
    # Create villages
    for village_data in villages_data:
        district_name = village_data.pop('district')
        Village.objects.create(
            id=uuid.uuid4(),
            district=districts[district_name],
            **village_data
        )


def remove_sample_locations(apps, schema_editor):
    """
    Remove sample locations added by this migration.
    """
    District = apps.get_model('locations', 'District')
    district_names = ['Lilongwe', 'Blantyre', 'Mzuzu', 'Zomba', 'Kasungu']
    District.objects.filter(name__in=district_names).delete()
    # Villages will be deleted automatically due to CASCADE


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0004_add_malawian_crops'),
        ('locations', '0001_initial'),  # Ensure locations app is ready
    ]

    operations = [
        migrations.RunPython(add_sample_locations, remove_sample_locations),
    ]

