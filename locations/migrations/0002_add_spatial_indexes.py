"""
Add spatial indexes for performance optimization.
PostGIS spatial indexes (GIST) for boundary and location fields.
"""
from django.contrib.postgres.indexes import GistIndex
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='district',
            index=GistIndex(fields=['boundary'], name='districts_boundary_gist_idx'),
        ),
        migrations.AddIndex(
            model_name='district',
            index=GistIndex(fields=['centroid'], name='districts_centroid_gist_idx'),
        ),
        migrations.AddIndex(
            model_name='village',
            index=GistIndex(fields=['location'], name='villages_location_gist_idx'),
        ),
    ]
