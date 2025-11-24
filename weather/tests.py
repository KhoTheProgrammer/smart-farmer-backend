"""
Tests for weather app.
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
from .models import WeatherCache
from .services import WeatherService, WeatherServiceError


class WeatherCacheModelTest(TestCase):
    """
    Test cases for WeatherCache model.
    """
    
    def test_create_location_key(self):
        """Test location key creation from coordinates."""
        key = WeatherCache.create_location_key(-13.9626, 33.7741)
        self.assertEqual(key, "-13.96_33.77")
    
    def test_cache_expiration(self):
        """Test cache expiration logic."""
        cache = WeatherCache.objects.create(
            location_key="test_key",
            latitude=-13.96,
            longitude=33.77,
            data={"test": "data"},
            expires_at=timezone.now() - timedelta(hours=1)  # Expired
        )
        self.assertTrue(cache.is_expired())
        
        cache.expires_at = timezone.now() + timedelta(hours=1)  # Not expired
        cache.save()
        self.assertFalse(cache.is_expired())
    
    def test_get_cached_data_valid(self):
        """Test retrieving valid cached data."""
        location_key = "test_location"
        test_data = {"precipitation": {"2023-01-01": 10.5}}
        
        WeatherCache.objects.create(
            location_key=location_key,
            latitude=-13.96,
            longitude=33.77,
            data=test_data,
            expires_at=timezone.now() + timedelta(hours=12)
        )
        
        cached = WeatherCache.get_cached_data(location_key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached.data, test_data)
    
    def test_get_cached_data_expired(self):
        """Test that expired cache is deleted and returns None."""
        location_key = "expired_location"
        
        WeatherCache.objects.create(
            location_key=location_key,
            latitude=-13.96,
            longitude=33.77,
            data={"test": "data"},
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        cached = WeatherCache.get_cached_data(location_key)
        self.assertIsNone(cached)
        
        # Verify cache was deleted
        self.assertFalse(WeatherCache.objects.filter(location_key=location_key).exists())
    
    def test_auto_set_expiration(self):
        """Test that expiration is automatically set to 24 hours."""
        cache = WeatherCache.objects.create(
            location_key="auto_expire",
            latitude=-13.96,
            longitude=33.77,
            data={"test": "data"}
        )
        
        # Check that expires_at is set to approximately 24 hours from now
        time_diff = cache.expires_at - timezone.now()
        self.assertAlmostEqual(time_diff.total_seconds(), 24 * 3600, delta=10)


class WeatherServiceTest(TestCase):
    """
    Test cases for WeatherService.
    """
    
    def test_validate_coordinates_valid(self):
        """Test coordinate validation with valid coordinates."""
        self.assertTrue(WeatherService._validate_coordinates(-13.96, 33.77))
        self.assertTrue(WeatherService._validate_coordinates(0, 0))
        self.assertTrue(WeatherService._validate_coordinates(90, 180))
        self.assertTrue(WeatherService._validate_coordinates(-90, -180))
    
    def test_validate_coordinates_invalid(self):
        """Test coordinate validation with invalid coordinates."""
        self.assertFalse(WeatherService._validate_coordinates(91, 0))
        self.assertFalse(WeatherService._validate_coordinates(-91, 0))
        self.assertFalse(WeatherService._validate_coordinates(0, 181))
        self.assertFalse(WeatherService._validate_coordinates(0, -181))
    
    def test_fetch_rainfall_data_invalid_coordinates(self):
        """Test that invalid coordinates raise an error."""
        with self.assertRaises(WeatherServiceError) as context:
            WeatherService.fetch_rainfall_data(100, 200)
        
        self.assertIn("Invalid coordinates", str(context.exception))
    
    @patch('weather.services.requests.get')
    def test_fetch_from_api_success(self, mock_get):
        """Test successful API fetch."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'properties': {
                'parameter': {
                    'PRECTOTCORR': {'2023-01-01': 10.5},
                    'T2M': {'2023-01-01': 25.0},
                    'ALLSKY_SFC_SW_DWN': {'2023-01-01': 200.0}
                }
            },
            'geometry': {
                'coordinates': [33.77, -13.96]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        data = WeatherService._fetch_from_api(-13.96, 33.77, 2020, 2023)
        
        self.assertIn('precipitation', data)
        self.assertIn('temperature', data)
        self.assertIn('solar_radiation', data)
        self.assertIn('metadata', data)
    
    @patch('weather.services.requests.get')
    def test_fetch_rainfall_data_with_cache(self, mock_get):
        """Test that cached data is used when available."""
        location_key = WeatherCache.create_location_key(-13.96, 33.77)
        test_data = {
            'precipitation': {'2023-01-01': 10.5},
            'temperature': {'2023-01-01': 25.0},
            'solar_radiation': {'2023-01-01': 200.0},
            'metadata': {}
        }
        
        # Create cache
        WeatherCache.objects.create(
            location_key=location_key,
            latitude=-13.96,
            longitude=33.77,
            data=test_data,
            expires_at=timezone.now() + timedelta(hours=12)
        )
        
        # Fetch data - should use cache, not call API
        data = WeatherService.fetch_rainfall_data(-13.96, 33.77)
        
        self.assertEqual(data, test_data)
        mock_get.assert_not_called()
    
    @patch('weather.services.requests.get')
    def test_api_fallback_to_stale_cache(self, mock_get):
        """Test fallback to stale cache when API fails."""
        # Mock API failure
        mock_get.side_effect = Exception("API unavailable")
        
        location_key = WeatherCache.create_location_key(-13.96, 33.77)
        test_data = {
            'precipitation': {'2023-01-01': 10.5},
            'temperature': {'2023-01-01': 25.0},
            'solar_radiation': {'2023-01-01': 200.0},
            'metadata': {}
        }
        
        # Create expired cache
        WeatherCache.objects.create(
            location_key=location_key,
            latitude=-13.96,
            longitude=33.77,
            data=test_data,
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Fetch data - should use stale cache as fallback
        data = WeatherService.fetch_rainfall_data(-13.96, 33.77)
        
        self.assertIn('precipitation', data)
        self.assertTrue(data.get('_stale_cache'))
        self.assertIn('_cache_warning', data)
        self.assertIn('unavailability', data.get('_cache_warning', '').lower())
    
    @patch('weather.services.requests.get')
    def test_api_failure_no_cache(self, mock_get):
        """Test that error is raised when API fails and no cache exists."""
        # Mock API failure
        mock_get.side_effect = Exception("API unavailable")
        
        with self.assertRaises(WeatherServiceError) as context:
            WeatherService.fetch_rainfall_data(-13.96, 33.77)
        
        self.assertIn("Failed to fetch weather data", str(context.exception))
    
    def test_parse_api_response_valid(self):
        """Test parsing valid API response."""
        response_data = {
            'properties': {
                'parameter': {
                    'PRECTOTCORR': {'2023-01-01': 10.5},
                    'T2M': {'2023-01-01': 25.0},
                    'ALLSKY_SFC_SW_DWN': {'2023-01-01': 200.0}
                }
            },
            'geometry': {
                'coordinates': [33.77, -13.96]
            }
        }
        
        parsed = WeatherService._parse_api_response(response_data)
        
        self.assertIn('precipitation', parsed)
        self.assertIn('temperature', parsed)
        self.assertIn('solar_radiation', parsed)
        self.assertEqual(parsed['precipitation']['2023-01-01'], 10.5)
        self.assertEqual(parsed['metadata']['latitude'], -13.96)
        self.assertEqual(parsed['metadata']['longitude'], 33.77)
    
    def test_parse_api_response_missing_data(self):
        """Test parsing API response with missing precipitation data."""
        response_data = {
            'properties': {
                'parameter': {}
            },
            'geometry': {
                'coordinates': [33.77, -13.96]
            }
        }
        
        with self.assertRaises(ValueError) as context:
            WeatherService._parse_api_response(response_data)
        
        self.assertIn("No precipitation data", str(context.exception))



class PlantingCalendarTest(TestCase):
    """
    Test cases for planting calendar calculations.
    Validates: Requirements 2.2, 2.3, 2.4, 2.5
    """
    
    def setUp(self):
        """Set up test data."""
        from locations.models import District, Village
        from django.contrib.gis.geos import Point, MultiPolygon, Polygon
        
        # Create test district
        boundary = MultiPolygon(Polygon(((33.0, -14.0), (34.0, -14.0), (34.0, -13.0), (33.0, -13.0), (33.0, -14.0))))
        self.district = District.objects.create(
            name="Test District",
            name_chichewa="Test District CH",
            boundary=boundary,
            centroid=Point(33.5, -13.5)
        )
        
        # Create test village
        self.village = Village.objects.create(
            name="Test Village",
            name_chichewa="Test Village CH",
            district=self.district,
            location=Point(33.77, -13.96),
            elevation=1200.0
        )
    
    def test_analyze_rainfall_patterns(self):
        """Test rainfall pattern analysis with 10 years of data."""
        # Create 10 years of synthetic rainfall data
        # Simulate Malawi's rainy season: November (day 305) to March (day 90)
        precipitation = {}
        for year in range(2014, 2024):
            for doy in range(1, 366):
                date_str = f"{year}{doy:03d}"
                # Heavy rain from November to March
                if 305 <= doy <= 365:
                    rainfall = 10.0  # Heavy rainy season
                elif 1 <= doy <= 90:
                    rainfall = 8.0  # Continuing rainy season
                else:
                    rainfall = 0.1  # Dry season
                precipitation[date_str] = rainfall
        
        analysis = WeatherService._analyze_rainfall_patterns(precipitation)
        
        # Verify analysis results
        self.assertIn('rainy_season_start_doy', analysis)
        self.assertIn('onset_variability', analysis)
        self.assertIn('years_analyzed', analysis)
        self.assertEqual(analysis['years_analyzed'], 10)
        
        # With this pattern, onset should be detected in the dry season
        # when cumulative rainfall reaches 20% threshold
        self.assertGreater(analysis['rainy_season_start_doy'], 0)
        self.assertLess(analysis['rainy_season_start_doy'], 366)
    
    def test_calculate_confidence_level(self):
        """Test confidence level calculation."""
        # Low variability = high confidence
        analysis_low_var = {
            'rainy_season_start_doy': 300,
            'onset_variability': 5.0,
            'years_analyzed': 10
        }
        confidence_high = WeatherService._calculate_confidence_level(analysis_low_var)
        self.assertGreater(confidence_high, 0.7)
        self.assertLessEqual(confidence_high, 1.0)
        
        # High variability = low confidence
        analysis_high_var = {
            'rainy_season_start_doy': 300,
            'onset_variability': 100.0,
            'years_analyzed': 10
        }
        confidence_low = WeatherService._calculate_confidence_level(analysis_high_var)
        self.assertLess(confidence_low, 0.5)
        self.assertGreaterEqual(confidence_low, 0.0)
    
    def test_calculate_planting_window(self):
        """Test planting window calculation."""
        # Create synthetic rainfall data
        precipitation = {}
        for year in range(2014, 2024):
            for doy in range(1, 366):
                date_str = f"{year}{doy:03d}"
                if 280 <= doy <= 365 or doy <= 90:
                    rainfall = 5.0
                else:
                    rainfall = 0.5
                precipitation[date_str] = rainfall
        
        rainfall_data = {'precipitation': precipitation}
        
        window = WeatherService.calculate_planting_window(rainfall_data)
        
        # Verify window structure
        self.assertIn('start_date', window)
        self.assertIn('end_date', window)
        self.assertIn('confidence_level', window)
        
        # Verify dates are valid
        self.assertIsNotNone(window['start_date'])
        self.assertIsNotNone(window['end_date'])
        
        # Start date should be before end date
        self.assertLess(window['start_date'], window['end_date'])
        
        # Confidence level should be between 0 and 1
        self.assertGreaterEqual(window['confidence_level'], 0.0)
        self.assertLessEqual(window['confidence_level'], 1.0)
    
    def test_planting_window_model_validation(self):
        """Test PlantingWindow model validation."""
        from .models import PlantingWindow
        from datetime import date
        from django.core.exceptions import ValidationError
        
        # Valid planting window
        window = PlantingWindow(
            village=self.village,
            start_date=date(2024, 11, 1),
            end_date=date(2024, 12, 1),
            confidence_level=0.85
        )
        window.full_clean()  # Should not raise
        window.save()
        
        # Invalid: start_date after end_date
        invalid_window = PlantingWindow(
            village=self.village,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 11, 1),
            confidence_level=0.85
        )
        with self.assertRaises(ValidationError):
            invalid_window.full_clean()
        
        # Invalid: confidence level out of range
        invalid_confidence = PlantingWindow(
            village=self.village,
            start_date=date(2024, 11, 1),
            end_date=date(2024, 12, 1),
            confidence_level=1.5
        )
        with self.assertRaises(ValidationError):
            invalid_confidence.full_clean()
    
    @patch('weather.services.WeatherService.fetch_rainfall_data')
    def test_planting_calendar_service(self, mock_fetch):
        """Test PlantingCalendarService integration."""
        from .services import PlantingCalendarService
        from datetime import date
        
        # Mock rainfall data
        precipitation = {}
        for year in range(2014, 2024):
            for doy in range(1, 366):
                date_str = f"{year}{doy:03d}"
                if 280 <= doy <= 365 or doy <= 90:
                    rainfall = 5.0
                else:
                    rainfall = 0.5
                precipitation[date_str] = rainfall
        
        mock_fetch.return_value = {'precipitation': precipitation}
        
        # Get planting window for village
        window = PlantingCalendarService.get_planting_window_for_village(self.village)
        
        # Verify window was created
        self.assertIsNotNone(window)
        self.assertEqual(window.village, self.village)
        self.assertIsNotNone(window.start_date)
        self.assertIsNotNone(window.end_date)
        self.assertGreaterEqual(window.confidence_level, 0.0)
        self.assertLessEqual(window.confidence_level, 1.0)
        
        # Verify it was saved to database
        from .models import PlantingWindow
        saved_window = PlantingWindow.objects.filter(village=self.village).first()
        self.assertIsNotNone(saved_window)



class SoilCacheModelTest(TestCase):
    """
    Test cases for SoilCache model.
    Validates: Requirements 3.1, 3.2
    """
    
    def test_create_location_key(self):
        """Test location key creation from coordinates."""
        from .models import SoilCache
        key = SoilCache.create_location_key(-13.9626, 33.7741)
        self.assertEqual(key, "-13.96_33.77")
    
    def test_cache_expiration(self):
        """Test cache expiration logic."""
        from .models import SoilCache
        cache = SoilCache.objects.create(
            location_key="test_soil_key",
            latitude=-13.96,
            longitude=33.77,
            data={"clay_content": 25.0},
            expires_at=timezone.now() - timedelta(hours=1)  # Expired
        )
        self.assertTrue(cache.is_expired())
        
        cache.expires_at = timezone.now() + timedelta(hours=1)  # Not expired
        cache.save()
        self.assertFalse(cache.is_expired())
    
    def test_get_cached_data_valid(self):
        """Test retrieving valid cached soil data."""
        from .models import SoilCache
        location_key = "test_soil_location"
        test_data = {
            "clay_content": 25.0,
            "sand_content": 45.0,
            "ph_level": 6.5,
            "organic_carbon": 1.2
        }
        
        SoilCache.objects.create(
            location_key=location_key,
            latitude=-13.96,
            longitude=33.77,
            data=test_data,
            expires_at=timezone.now() + timedelta(hours=12)
        )
        
        cached = SoilCache.get_cached_data(location_key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached.data, test_data)
    
    def test_get_cached_data_expired(self):
        """Test that expired cache is deleted and returns None."""
        from .models import SoilCache
        location_key = "expired_soil_location"
        
        SoilCache.objects.create(
            location_key=location_key,
            latitude=-13.96,
            longitude=33.77,
            data={"clay_content": 25.0},
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        cached = SoilCache.get_cached_data(location_key)
        self.assertIsNone(cached)
        
        # Verify cache was deleted
        self.assertFalse(SoilCache.objects.filter(location_key=location_key).exists())
    
    def test_auto_set_expiration(self):
        """Test that expiration is automatically set to 24 hours."""
        from .models import SoilCache
        cache = SoilCache.objects.create(
            location_key="auto_expire_soil",
            latitude=-13.96,
            longitude=33.77,
            data={"clay_content": 25.0}
        )
        
        # Check that expires_at is set to approximately 24 hours from now
        time_diff = cache.expires_at - timezone.now()
        self.assertAlmostEqual(time_diff.total_seconds(), 24 * 3600, delta=10)


class SoilServiceTest(TestCase):
    """
    Test cases for SoilService.
    Validates: Requirements 3.1, 3.2
    """
    
    def test_validate_coordinates_valid(self):
        """Test coordinate validation with valid coordinates."""
        from .services import SoilService
        self.assertTrue(SoilService._validate_coordinates(-13.96, 33.77))
        self.assertTrue(SoilService._validate_coordinates(0, 0))
        self.assertTrue(SoilService._validate_coordinates(90, 180))
        self.assertTrue(SoilService._validate_coordinates(-90, -180))
    
    def test_validate_coordinates_invalid(self):
        """Test coordinate validation with invalid coordinates."""
        from .services import SoilService
        self.assertFalse(SoilService._validate_coordinates(91, 0))
        self.assertFalse(SoilService._validate_coordinates(-91, 0))
        self.assertFalse(SoilService._validate_coordinates(0, 181))
        self.assertFalse(SoilService._validate_coordinates(0, -181))
    
    def test_fetch_soil_properties_invalid_coordinates(self):
        """Test that invalid coordinates raise an error."""
        from .services import SoilService, SoilServiceError
        with self.assertRaises(SoilServiceError) as context:
            SoilService.fetch_soil_properties(100, 200)
        
        self.assertIn("Invalid coordinates", str(context.exception))
    
    @patch('weather.services.requests.get')
    def test_fetch_from_api_success(self, mock_get):
        """Test successful API fetch."""
        from .services import SoilService
        
        # Mock API response (SoilGrids format)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'properties': {
                'layers': [
                    {
                        'name': 'clay',
                        'depths': [
                            {
                                'values': {'mean': 250}  # 25.0% after conversion
                            }
                        ]
                    },
                    {
                        'name': 'sand',
                        'depths': [
                            {
                                'values': {'mean': 450}  # 45.0% after conversion
                            }
                        ]
                    },
                    {
                        'name': 'phh2o',
                        'depths': [
                            {
                                'values': {'mean': 65}  # 6.5 pH after conversion
                            }
                        ]
                    },
                    {
                        'name': 'soc',
                        'depths': [
                            {
                                'values': {'mean': 12}  # 1.2 g/kg after conversion
                            }
                        ]
                    }
                ]
            },
            'geometry': {
                'coordinates': [33.77, -13.96]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        data = SoilService._fetch_from_api(-13.96, 33.77)
        
        self.assertIn('clay_content', data)
        self.assertIn('sand_content', data)
        self.assertIn('ph_level', data)
        self.assertIn('organic_carbon', data)
        self.assertIn('metadata', data)
        
        # Verify conversions
        self.assertAlmostEqual(data['clay_content'], 25.0, places=1)
        self.assertAlmostEqual(data['sand_content'], 45.0, places=1)
        self.assertAlmostEqual(data['ph_level'], 6.5, places=1)
        self.assertAlmostEqual(data['organic_carbon'], 1.2, places=1)
    
    @patch('weather.services.requests.get')
    def test_fetch_soil_properties_with_cache(self, mock_get):
        """Test that cached data is used when available."""
        from .services import SoilService
        from .models import SoilCache
        
        location_key = SoilCache.create_location_key(-13.96, 33.77)
        test_data = {
            'clay_content': 25.0,
            'sand_content': 45.0,
            'ph_level': 6.5,
            'organic_carbon': 1.2,
            'metadata': {}
        }
        
        # Create cache
        SoilCache.objects.create(
            location_key=location_key,
            latitude=-13.96,
            longitude=33.77,
            data=test_data,
            expires_at=timezone.now() + timedelta(hours=12)
        )
        
        # Fetch data - should use cache, not call API
        data = SoilService.fetch_soil_properties(-13.96, 33.77)
        
        self.assertEqual(data, test_data)
        mock_get.assert_not_called()
    
    @patch('weather.services.requests.get')
    def test_api_fallback_to_stale_cache(self, mock_get):
        """Test fallback to stale cache when API fails."""
        from .services import SoilService
        from .models import SoilCache
        
        # Mock API failure
        mock_get.side_effect = Exception("API unavailable")
        
        location_key = SoilCache.create_location_key(-13.96, 33.77)
        test_data = {
            'clay_content': 25.0,
            'sand_content': 45.0,
            'ph_level': 6.5,
            'organic_carbon': 1.2,
            'metadata': {}
        }
        
        # Create expired cache
        SoilCache.objects.create(
            location_key=location_key,
            latitude=-13.96,
            longitude=33.77,
            data=test_data,
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Fetch data - should use stale cache as fallback
        data = SoilService.fetch_soil_properties(-13.96, 33.77)
        
        self.assertIn('clay_content', data)
        self.assertTrue(data.get('_stale_cache'))
        self.assertIn('_cache_warning', data)
        self.assertIn('unavailability', data.get('_cache_warning', '').lower())
    
    @patch('weather.services.requests.get')
    def test_api_failure_no_cache(self, mock_get):
        """Test that error is raised when API fails and no cache exists."""
        from .services import SoilService, SoilServiceError
        
        # Mock API failure
        mock_get.side_effect = Exception("API unavailable")
        
        with self.assertRaises(SoilServiceError) as context:
            SoilService.fetch_soil_properties(-13.96, 33.77)
        
        self.assertIn("Failed to fetch soil data", str(context.exception))
    
    def test_parse_soil_response_valid(self):
        """Test parsing valid SoilGrids API response."""
        from .services import SoilService
        
        response_data = {
            'properties': {
                'layers': [
                    {
                        'name': 'clay',
                        'depths': [{'values': {'mean': 250}}]
                    },
                    {
                        'name': 'sand',
                        'depths': [{'values': {'mean': 450}}]
                    },
                    {
                        'name': 'phh2o',
                        'depths': [{'values': {'mean': 65}}]
                    },
                    {
                        'name': 'soc',
                        'depths': [{'values': {'mean': 12}}]
                    }
                ]
            },
            'geometry': {
                'coordinates': [33.77, -13.96]
            }
        }
        
        parsed = SoilService._parse_soil_response(response_data)
        
        self.assertIn('clay_content', parsed)
        self.assertIn('sand_content', parsed)
        self.assertIn('ph_level', parsed)
        self.assertIn('organic_carbon', parsed)
        self.assertIn('metadata', parsed)
        
        self.assertAlmostEqual(parsed['clay_content'], 25.0, places=1)
        self.assertAlmostEqual(parsed['sand_content'], 45.0, places=1)
        self.assertAlmostEqual(parsed['ph_level'], 6.5, places=1)
        self.assertAlmostEqual(parsed['organic_carbon'], 1.2, places=1)
        
        self.assertEqual(parsed['metadata']['latitude'], -13.96)
        self.assertEqual(parsed['metadata']['longitude'], 33.77)
    
    def test_parse_soil_response_missing_properties(self):
        """Test parsing API response with missing soil properties."""
        from .services import SoilService
        
        response_data = {
            'properties': {
                'layers': [
                    {
                        'name': 'clay',
                        'depths': [{'values': {'mean': 250}}]
                    }
                    # Missing sand, pH, and organic carbon
                ]
            },
            'geometry': {
                'coordinates': [33.77, -13.96]
            }
        }
        
        with self.assertRaises(ValueError) as context:
            SoilService._parse_soil_response(response_data)
        
        self.assertIn("Missing soil properties", str(context.exception))
    
    @patch('weather.services.requests.get')
    def test_cache_soil_data(self, mock_get):
        """Test that soil data is cached after API fetch."""
        from .services import SoilService
        from .models import SoilCache
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'properties': {
                'layers': [
                    {'name': 'clay', 'depths': [{'values': {'mean': 250}}]},
                    {'name': 'sand', 'depths': [{'values': {'mean': 450}}]},
                    {'name': 'phh2o', 'depths': [{'values': {'mean': 65}}]},
                    {'name': 'soc', 'depths': [{'values': {'mean': 12}}]}
                ]
            },
            'geometry': {'coordinates': [33.77, -13.96]}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Fetch data
        data = SoilService.fetch_soil_properties(-13.96, 33.77)
        
        # Verify cache was created
        location_key = SoilCache.create_location_key(-13.96, 33.77)
        cache = SoilCache.objects.filter(location_key=location_key).first()
        
        self.assertIsNotNone(cache)
        self.assertEqual(cache.latitude, -13.96)
        self.assertEqual(cache.longitude, 33.77)
        self.assertIn('clay_content', cache.data)
        self.assertIn('sand_content', cache.data)
        self.assertIn('ph_level', cache.data)
        self.assertIn('organic_carbon', cache.data)
