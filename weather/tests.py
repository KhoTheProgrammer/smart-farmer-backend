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



class CropSuitabilityServiceTest(TestCase):
    """
    Test cases for CropSuitabilityService.
    Validates: Requirements 3.4, 3.5, 3.6
    """
    
    def setUp(self):
        """Set up test data."""
        from locations.models import District, Village
        from django.contrib.gis.geos import Point, MultiPolygon, Polygon
        from .models import Crop
        
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
        
        # Create test crops
        self.maize = Crop.objects.create(
            name="Maize",
            name_chichewa="Chimanga",
            scientific_name="Zea mays",
            min_ph=5.5,
            max_ph=7.5,
            min_clay_content=15.0,
            max_clay_content=40.0,
            min_organic_carbon=1.0,
            min_rainfall=500.0,
            max_rainfall=1200.0,
            min_temperature=18.0,
            max_temperature=32.0,
            min_elevation=500.0,
            max_elevation=2000.0,
            growing_season_days=120
        )
        
        self.tobacco = Crop.objects.create(
            name="Tobacco",
            name_chichewa="Fodya",
            scientific_name="Nicotiana tabacum",
            min_ph=5.0,
            max_ph=6.5,
            min_clay_content=10.0,
            max_clay_content=30.0,
            min_organic_carbon=1.5,
            min_rainfall=800.0,
            max_rainfall=1500.0,
            min_temperature=20.0,
            max_temperature=30.0,
            min_elevation=800.0,
            max_elevation=1800.0,
            growing_season_days=90
        )
    
    def test_calculate_range_score_within_range(self):
        """Test range score calculation for values within acceptable range."""
        from .services import CropSuitabilityService
        
        # Value at midpoint should score 100
        score = CropSuitabilityService._calculate_range_score(6.0, 5.0, 7.0, optimal_range=0.5)
        self.assertEqual(score, 100.0)
        
        # Value within optimal range should score 100
        score = CropSuitabilityService._calculate_range_score(6.3, 5.0, 7.0, optimal_range=0.5)
        self.assertEqual(score, 100.0)
        
        # Value within acceptable range but outside optimal should score >= 70
        score = CropSuitabilityService._calculate_range_score(5.2, 5.0, 7.0, optimal_range=0.5)
        self.assertGreaterEqual(score, 70.0)
        self.assertLess(score, 100.0)
    
    def test_calculate_range_score_outside_range(self):
        """Test range score calculation for values outside acceptable range."""
        from .services import CropSuitabilityService
        
        # Value below minimum should score < 50
        score = CropSuitabilityService._calculate_range_score(4.0, 5.0, 7.0)
        self.assertLess(score, 50.0)
        self.assertGreaterEqual(score, 0.0)
        
        # Value above maximum should score < 50
        score = CropSuitabilityService._calculate_range_score(8.0, 5.0, 7.0)
        self.assertLess(score, 50.0)
        self.assertGreaterEqual(score, 0.0)
    
    def test_calculate_soil_score(self):
        """Test soil suitability score calculation."""
        from .services import CropSuitabilityService
        
        # Ideal soil conditions for maize
        soil_data = {
            'ph_level': 6.5,  # Midpoint of 5.5-7.5
            'clay_content': 27.5,  # Midpoint of 15-40
            'organic_carbon': 2.0  # Above minimum of 1.0
        }
        
        score = CropSuitabilityService._calculate_soil_score(self.maize, soil_data)
        
        # Should score high with ideal conditions
        self.assertGreater(score, 80.0)
        self.assertLessEqual(score, 100.0)
    
    def test_calculate_elevation_score(self):
        """Test elevation suitability score calculation."""
        from .services import CropSuitabilityService
        
        # Ideal elevation for maize (midpoint of 500-2000)
        score = CropSuitabilityService._calculate_elevation_score(self.maize, 1250.0)
        self.assertGreater(score, 90.0)
        
        # Elevation within range but not optimal
        score = CropSuitabilityService._calculate_elevation_score(self.maize, 600.0)
        self.assertGreater(score, 70.0)
        
        # Elevation outside range
        score = CropSuitabilityService._calculate_elevation_score(self.maize, 300.0)
        self.assertLess(score, 50.0)
    
    def test_calculate_climate_score(self):
        """Test climate suitability score calculation."""
        from .services import CropSuitabilityService
        
        # Ideal climate for maize
        climate_data = {
            'annual_rainfall': 850.0,  # Within 500-1200
            'mean_temperature': 25.0  # Within 18-32
        }
        
        score = CropSuitabilityService._calculate_climate_score(self.maize, climate_data)
        self.assertGreater(score, 80.0)
        self.assertLessEqual(score, 100.0)
    
    def test_calculate_suitability_with_all_factors(self):
        """Test overall suitability calculation with all factors."""
        from .services import CropSuitabilityService
        
        soil_data = {
            'ph_level': 6.5,
            'clay_content': 27.5,
            'organic_carbon': 2.0
        }
        
        climate_data = {
            'annual_rainfall': 850.0,
            'mean_temperature': 25.0
        }
        
        score = CropSuitabilityService.calculate_suitability(
            self.maize,
            soil_data,
            1250.0,  # elevation
            climate_data
        )
        
        # With ideal conditions, should score high
        self.assertGreater(score, 80.0)
        self.assertLessEqual(score, 100.0)
    
    def test_calculate_suitability_without_climate(self):
        """Test suitability calculation without climate data."""
        from .services import CropSuitabilityService
        
        soil_data = {
            'ph_level': 6.5,
            'clay_content': 27.5,
            'organic_carbon': 2.0
        }
        
        score = CropSuitabilityService.calculate_suitability(
            self.maize,
            soil_data,
            1250.0,  # elevation
            None  # no climate data
        )
        
        # Should still calculate score based on soil and elevation
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 100.0)
    
    def test_calculate_suitability_poor_conditions(self):
        """Test suitability calculation with poor conditions."""
        from .services import CropSuitabilityService
        
        # Poor soil conditions for maize
        soil_data = {
            'ph_level': 4.0,  # Too acidic
            'clay_content': 5.0,  # Too sandy
            'organic_carbon': 0.3  # Too low
        }
        
        score = CropSuitabilityService.calculate_suitability(
            self.maize,
            soil_data,
            300.0,  # Too low elevation
            None
        )
        
        # Should score low with poor conditions
        self.assertLess(score, 50.0)
        self.assertGreaterEqual(score, 0.0)
    
    def test_get_crop_requirements(self):
        """Test retrieving crop requirements."""
        from .services import CropSuitabilityService
        
        requirements = CropSuitabilityService.get_crop_requirements(str(self.maize.id))
        
        # Verify structure
        self.assertIn('name', requirements)
        self.assertIn('name_chichewa', requirements)
        self.assertIn('scientific_name', requirements)
        self.assertIn('soil_requirements', requirements)
        self.assertIn('climate_requirements', requirements)
        self.assertIn('elevation_requirements', requirements)
        self.assertIn('growing_season_days', requirements)
        
        # Verify values
        self.assertEqual(requirements['name'], 'Maize')
        self.assertEqual(requirements['name_chichewa'], 'Chimanga')
        self.assertEqual(requirements['soil_requirements']['min_ph'], 5.5)
        self.assertEqual(requirements['soil_requirements']['max_ph'], 7.5)
    
    def test_get_crop_requirements_not_found(self):
        """Test error handling when crop not found."""
        from .services import CropSuitabilityService, CropSuitabilityServiceError
        import uuid
        
        with self.assertRaises(CropSuitabilityServiceError) as context:
            CropSuitabilityService.get_crop_requirements(str(uuid.uuid4()))
        
        self.assertIn("not found", str(context.exception))
    
    @patch('weather.services.SoilService.fetch_soil_properties')
    def test_rank_crops(self, mock_fetch_soil):
        """Test ranking crops by suitability."""
        from .services import CropSuitabilityService
        from .models import Crop
        
        # Mock soil data
        mock_fetch_soil.return_value = {
            'ph_level': 6.0,
            'clay_content': 25.0,
            'organic_carbon': 1.5
        }
        
        # Rank crops for village
        results = CropSuitabilityService.rank_crops(self.village)
        
        # Verify results structure
        self.assertIsInstance(results, list)
        # Should have results for all crops in database (including migration-added crops)
        total_crops = Crop.objects.count()
        self.assertEqual(len(results), total_crops)
        
        # Verify each result has required fields
        for result in results:
            self.assertIn('crop_id', result)
            self.assertIn('name', result)
            self.assertIn('name_chichewa', result)
            self.assertIn('scientific_name', result)
            self.assertIn('suitability_score', result)
            self.assertIn('soil_requirements', result)
            self.assertIn('elevation_requirements', result)
            
            # Verify score is valid
            self.assertGreaterEqual(result['suitability_score'], 0.0)
            self.assertLessEqual(result['suitability_score'], 100.0)
        
        # Verify results are sorted by score (highest first)
        scores = [r['suitability_score'] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
    
    @patch('weather.services.SoilService.fetch_soil_properties')
    def test_rank_crops_with_district(self, mock_fetch_soil):
        """Test ranking crops using district centroid."""
        from .services import CropSuitabilityService
        
        # Mock soil data
        mock_fetch_soil.return_value = {
            'ph_level': 6.0,
            'clay_content': 25.0,
            'organic_carbon': 1.5
        }
        
        # Rank crops for district (no elevation)
        results = CropSuitabilityService.rank_crops(self.district)
        
        # Should still work with default elevation
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
    
    @patch('weather.services.SoilService.fetch_soil_properties')
    def test_rank_crops_with_provided_soil_data(self, mock_fetch_soil):
        """Test ranking crops with pre-fetched soil data."""
        from .services import CropSuitabilityService
        
        soil_data = {
            'ph_level': 6.0,
            'clay_content': 25.0,
            'organic_carbon': 1.5
        }
        
        # Rank crops with provided soil data
        results = CropSuitabilityService.rank_crops(self.village, soil_data=soil_data)
        
        # Should not call API since we provided data
        mock_fetch_soil.assert_not_called()
        
        # Should still return valid results
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
    
    @patch('weather.services.SoilService.fetch_soil_properties')
    def test_rank_crops_soil_fetch_error(self, mock_fetch_soil):
        """Test error handling when soil data fetch fails."""
        from .services import CropSuitabilityService, CropSuitabilityServiceError, SoilServiceError
        
        # Mock soil service error
        mock_fetch_soil.side_effect = SoilServiceError("API unavailable")
        
        with self.assertRaises(CropSuitabilityServiceError) as context:
            CropSuitabilityService.rank_crops(self.village)
        
        self.assertIn("Failed to fetch soil data", str(context.exception))
    
    def test_rank_crops_no_crops_in_database(self):
        """Test ranking when no crops exist in database."""
        from .services import CropSuitabilityService
        from .models import Crop
        
        # Delete all crops
        Crop.objects.all().delete()
        
        soil_data = {
            'ph_level': 6.0,
            'clay_content': 25.0,
            'organic_carbon': 1.5
        }
        
        # Should return empty list
        results = CropSuitabilityService.rank_crops(self.village, soil_data=soil_data)
        self.assertEqual(results, [])
    
    def test_suitability_score_bounds(self):
        """Test that suitability scores are always between 0 and 100."""
        from .services import CropSuitabilityService
        
        # Test with extreme values
        extreme_soil = {
            'ph_level': 10.0,  # Very high
            'clay_content': 90.0,  # Very high
            'organic_carbon': 0.01  # Very low
        }
        
        score = CropSuitabilityService.calculate_suitability(
            self.maize,
            extreme_soil,
            5000.0,  # Very high elevation
            None
        )
        
        # Score should still be bounded
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
