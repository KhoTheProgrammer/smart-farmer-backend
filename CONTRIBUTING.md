# Contributing to Mlimi Wanzeru Backend

Thank you for your interest in contributing to the Mlimi Wanzeru platform!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Set up development environment (see README.md)
5. Make your changes
6. Write/update tests
7. Commit with clear messages
8. Push to your fork
9. Create a Pull Request

## Development Setup

See [README.md](./README.md) for detailed setup instructions including:

- PostgreSQL/PostGIS installation
- GDAL installation
- Database setup
- Data import

## Code Style

### Python/Django

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused (< 50 lines)
- Use type hints where appropriate

### Example

```python
def calculate_crop_suitability(
    crop: Crop,
    temperature: float,
    rainfall: float,
    soil_ph: float
) -> float:
    """
    Calculate crop suitability score based on environmental factors.

    Args:
        crop: Crop model instance
        temperature: Average temperature in Celsius
        rainfall: Annual rainfall in mm
        soil_ph: Soil pH value

    Returns:
        Suitability score between 0 and 100
    """
    # Implementation here
    pass
```

## Project Structure

- `locations/` - Location models and services (districts, villages, elevation)
- `weather/` - Crop models and advisory services (crops, planting calendar)
- `mlimi_wanzeru/` - Django project settings and configuration

## Database Migrations

When changing models:

```bash
# Create migration
python manage.py makemigrations

# Review migration file
cat locations/migrations/0XXX_*.py

# Apply migration
python manage.py migrate

# Test migration
python manage.py test
```

## Testing

### Run Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test locations
python manage.py test weather

# Specific test
python manage.py test locations.tests.TestDistrictModel
```

### Write Tests

Add tests for:

- New models
- New API endpoints
- Business logic in services
- Data validation

Example:

```python
from django.test import TestCase
from locations.models import District

class TestDistrictModel(TestCase):
    def test_district_creation(self):
        district = District.objects.create(
            name="Lilongwe",
            code="LLW"
        )
        self.assertEqual(district.name, "Lilongwe")
```

## API Development

### Adding New Endpoints

1. Define model in `models.py`
2. Create serializer in `serializers.py`
3. Create view in `views.py`
4. Add URL pattern in `urls.py`
5. Update API documentation
6. Write tests

### API Documentation

Use drf-spectacular decorators:

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter

@extend_schema(
    summary="Get crop suitability",
    description="Calculate crop suitability for a location",
    parameters=[
        OpenApiParameter(
            name='lat',
            type=float,
            description='Latitude',
            required=True
        ),
    ]
)
def get_suitability(self, request, pk=None):
    # Implementation
    pass
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add soil texture analysis endpoint
fix: Resolve elevation calculation bug
docs: Update API documentation
refactor: Simplify weather service logic
test: Add tests for planting calendar
perf: Optimize village boundary queries
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Add migration files if needed
4. Update API_README.md for new endpoints
5. Request review from maintainers
6. Address review feedback
7. Wait for approval and merge

## Code Review Checklist

- [ ] Code follows PEP 8 style guide
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No sensitive data in code
- [ ] Database migrations are included
- [ ] API endpoints are documented

## Common Tasks

### Adding a New Crop

1. Add crop data to migration file
2. Run migration: `python manage.py migrate`
3. Verify: `python verify_crops.py`

### Updating Geospatial Data

1. Download new data files
2. Place in `data/` directory
3. Run import command
4. Verify with test scripts

### Debugging

```bash
# Django shell
python manage.py shell

# Check database
python manage.py dbshell

# View logs
tail -f logs/django.log
```

## Questions?

- Check existing issues
- Review documentation
- Ask in pull request comments
- Contact maintainers

Thank you for contributing! 🌱
