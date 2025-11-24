"""
Weather services for integrating with NASA POWER API.
Provides methods for fetching and caching weather data.
"""
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import WeatherCache

logger = logging.getLogger(__name__)


class WeatherServiceError(Exception):
    """Custom exception for weather service errors."""
    pass


class WeatherService:
    """
    Service class for handling weather data integration with NASA POWER API.
    Implements caching with 24-hour TTL and fallback to cached data on API failure.
    
    Validates: Requirements 2.1, 9.1, 9.2, 9.3, 9.4, 9.5
    """
    
    REQUEST_TIMEOUT = 30  # seconds
    
    # Weather parameters to request from NASA POWER API
    PARAMETERS = [
        "PRECTOTCORR",  # Precipitation Corrected
        "T2M",          # Temperature at 2 Meters
        "ALLSKY_SFC_SW_DWN",  # Solar Radiation
    ]
    
    @classmethod
    def fetch_rainfall_data(
        cls,
        lat: float,
        lon: float,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> Dict:
        """
        Retrieve historical rainfall and weather data from NASA POWER API.
        Uses cache if available and not expired, otherwise fetches from API.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            start_year: Starting year for data (default: 10 years ago)
            end_year: Ending year for data (default: last year)
            
        Returns:
            Dictionary containing weather data
            
        Raises:
            WeatherServiceError: If API request fails and no cache available
            
        Validates: Requirements 2.1, 9.1, 9.2, 9.3, 9.4
        """
        # Validate coordinates
        if not cls._validate_coordinates(lat, lon):
            raise WeatherServiceError(
                f"Invalid coordinates: lat={lat}, lon={lon}. "
                "Latitude must be between -90 and 90, longitude between -180 and 180."
            )
        
        # Set default date range (10 years of historical data)
        if not end_year:
            end_year = datetime.now().year - 1
        if not start_year:
            start_year = end_year - 9  # 10 years total
        
        # Create cache key
        location_key = WeatherCache.create_location_key(lat, lon)
        
        # Check cache first (but don't delete if expired - we might need it as fallback)
        try:
            cache = WeatherCache.objects.get(location_key=location_key)
            if not cache.is_expired():
                logger.info(f"Using cached weather data for {location_key}")
                return cache.data
        except WeatherCache.DoesNotExist:
            cache = None
        
        # Fetch from API
        try:
            data = cls._fetch_from_api(lat, lon, start_year, end_year)
            # Cache the data
            cls._cache_weather_data(location_key, lat, lon, data)
            return data
        except Exception as e:
            logger.error(f"Failed to fetch weather data from API: {e}")
            # Try to use expired cache as fallback
            if cache:
                logger.warning(f"Using stale cached data for {location_key}")
                fallback_data = cache.data.copy()
                fallback_data['_stale_cache'] = True
                fallback_data['_cache_warning'] = "Using cached data due to API unavailability"
                return fallback_data
            raise WeatherServiceError(
                f"Failed to fetch weather data and no cache available: {str(e)}"
            )
    
    @classmethod
    def _fetch_from_api(
        cls,
        lat: float,
        lon: float,
        start_year: int,
        end_year: int
    ) -> Dict:
        """
        Fetch weather data directly from NASA POWER API.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            Parsed weather data dictionary
            
        Raises:
            WeatherServiceError: If API request fails
            
        Validates: Requirements 9.1, 9.2, 9.5
        """
        # Build API request parameters
        params = {
            "parameters": ",".join(cls.PARAMETERS),
            "community": "AG",  # Agricultural community
            "longitude": lon,
            "latitude": lat,
            "start": f"{start_year}0101",
            "end": f"{end_year}1231",
            "format": "JSON"
        }
        
        logger.info(f"Fetching weather data from NASA POWER API for lat={lat}, lon={lon}")
        
        try:
            response = requests.get(
                settings.NASA_POWER_API_URL,
                params=params,
                timeout=cls.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Extract and validate weather parameters
            parsed_data = cls._parse_api_response(data)
            
            return parsed_data
            
        except requests.exceptions.Timeout:
            raise WeatherServiceError("NASA POWER API request timed out")
        except requests.exceptions.RequestException as e:
            raise WeatherServiceError(f"NASA POWER API request failed: {str(e)}")
        except ValueError as e:
            raise WeatherServiceError(f"Failed to parse NASA POWER API response: {str(e)}")
    
    @classmethod
    def _parse_api_response(cls, response_data: Dict) -> Dict:
        """
        Parse and extract relevant data from NASA POWER API response.
        
        Args:
            response_data: Raw API response
            
        Returns:
            Parsed data with precipitation, temperature, and solar radiation
            
        Validates: Requirements 9.2, 9.5
        """
        try:
            parameters = response_data.get('properties', {}).get('parameter', {})
            
            # Extract weather parameters
            parsed = {
                'precipitation': parameters.get('PRECTOTCORR', {}),
                'temperature': parameters.get('T2M', {}),
                'solar_radiation': parameters.get('ALLSKY_SFC_SW_DWN', {}),
                'metadata': {
                    'latitude': response_data.get('geometry', {}).get('coordinates', [None, None])[1],
                    'longitude': response_data.get('geometry', {}).get('coordinates', [None, None])[0],
                    'source': 'NASA POWER API',
                    'fetched_at': timezone.now().isoformat(),
                }
            }
            
            # Validate that we got data
            if not parsed['precipitation']:
                raise ValueError("No precipitation data in API response")
            
            return parsed
            
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid API response structure: {str(e)}")
    
    @classmethod
    def _validate_coordinates(cls, lat: float, lon: float) -> bool:
        """
        Validate latitude and longitude coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if valid, False otherwise
        """
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    @classmethod
    def _get_cached_weather(cls, location_key: str) -> Optional[Dict]:
        """
        Retrieve valid cached weather data.
        
        Args:
            location_key: Cache key for location
            
        Returns:
            Cached data dictionary or None
            
        Validates: Requirements 9.3
        """
        cache = WeatherCache.get_cached_data(location_key)
        if cache:
            return cache.data
        return None
    
    @classmethod
    def _get_fallback_cache(cls, location_key: str) -> Optional[Dict]:
        """
        Retrieve cached data even if expired (for fallback).
        
        Args:
            location_key: Cache key for location
            
        Returns:
            Cached data dictionary or None
            
        Validates: Requirements 9.4
        """
        try:
            cache = WeatherCache.objects.get(location_key=location_key)
            return cache.data
        except WeatherCache.DoesNotExist:
            return None
    
    @classmethod
    def _cache_weather_data(
        cls,
        location_key: str,
        lat: float,
        lon: float,
        data: Dict
    ) -> None:
        """
        Store weather data in cache with 24-hour TTL.
        
        Args:
            location_key: Cache key for location
            lat: Latitude
            lon: Longitude
            data: Weather data to cache
            
        Validates: Requirements 9.3
        """
        try:
            # Update existing cache or create new
            cache, created = WeatherCache.objects.update_or_create(
                location_key=location_key,
                defaults={
                    'latitude': lat,
                    'longitude': lon,
                    'data': data,
                    'expires_at': timezone.now() + timedelta(hours=24)
                }
            )
            action = "Created" if created else "Updated"
            logger.info(f"{action} weather cache for {location_key}")
        except Exception as e:
            logger.error(f"Failed to cache weather data: {e}")
            # Don't raise exception - caching failure shouldn't break the request
    
    @classmethod
    def calculate_planting_window(cls, rainfall_data: Dict) -> Dict:
        """
        Calculate optimal planting window based on rainfall patterns.
        Analyzes onset of rainy season from 10-year historical data.
        
        Args:
            rainfall_data: Dictionary containing precipitation data
            
        Returns:
            Dictionary with start_date, end_date, and confidence_level
            
        Validates: Requirements 2.2, 2.3, 2.4, 2.5
        """
        import numpy as np
        from datetime import date
        
        precipitation = rainfall_data.get('precipitation', {})
        
        if not precipitation:
            raise WeatherServiceError("No precipitation data available for analysis")
        
        # Analyze rainfall patterns to find rainy season onset
        analysis = cls._analyze_rainfall_patterns(precipitation)
        
        # Calculate planting window based on rainy season onset
        start_doy = analysis['rainy_season_start_doy']
        end_doy = analysis['rainy_season_start_doy'] + 30  # 30-day planting window
        
        # Use current year for dates (this is simplified)
        current_year = datetime.now().year
        start_date = date(current_year, 1, 1) + timedelta(days=start_doy - 1)
        end_date = date(current_year, 1, 1) + timedelta(days=end_doy - 1)
        
        # Calculate confidence level based on rainfall variability
        confidence_level = cls._calculate_confidence_level(analysis)
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'confidence_level': confidence_level,
            'analysis': analysis
        }
    
    @classmethod
    def _analyze_rainfall_patterns(cls, precipitation: Dict) -> Dict:
        """
        Analyze 10-year historical rainfall data to identify patterns.
        
        Args:
            precipitation: Dictionary with date keys and rainfall values
            
        Returns:
            Dictionary containing analysis results
            
        Validates: Requirements 2.2
        """
        import numpy as np
        from collections import defaultdict
        
        # Group rainfall by year and day of year
        yearly_data = defaultdict(dict)
        
        for date_str, rainfall in precipitation.items():
            if rainfall == -999:  # NASA POWER missing data indicator
                continue
            
            try:
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                year = date_obj.year
                doy = date_obj.timetuple().tm_yday
                yearly_data[year][doy] = rainfall
            except (ValueError, AttributeError):
                continue
        
        # Verify we have 10 years of data
        years = sorted(yearly_data.keys())
        if len(years) < 10:
            logger.warning(f"Only {len(years)} years of data available, expected 10")
        
        # Calculate cumulative rainfall for each year
        yearly_cumulative = {}
        for year in years:
            daily_rainfall = [yearly_data[year].get(doy, 0) for doy in range(1, 366)]
            yearly_cumulative[year] = np.cumsum(daily_rainfall)
        
        # Find rainy season onset (when cumulative rainfall reaches threshold)
        # Simplified: find when 20% of annual rainfall has fallen
        onset_days = []
        for year in years:
            annual_total = yearly_cumulative[year][-1]
            threshold = annual_total * 0.2
            
            # Find first day when cumulative exceeds threshold
            cumulative = yearly_cumulative[year]
            onset_doy = next((i + 1 for i, val in enumerate(cumulative) if val >= threshold), 180)
            onset_days.append(onset_doy)
        
        # Calculate statistics
        mean_onset = int(np.mean(onset_days))
        std_onset = float(np.std(onset_days))
        
        return {
            'rainy_season_start_doy': mean_onset,
            'onset_variability': std_onset,
            'years_analyzed': len(years),
            'onset_days_by_year': onset_days
        }
    
    @classmethod
    def _calculate_confidence_level(cls, analysis: Dict) -> float:
        """
        Calculate confidence level based on rainfall variability.
        Lower variability = higher confidence.
        
        Args:
            analysis: Rainfall pattern analysis results
            
        Returns:
            Confidence level between 0 and 1
            
        Validates: Requirements 2.5
        """
        # Use coefficient of variation to determine confidence
        # Lower CV = more consistent = higher confidence
        variability = analysis['onset_variability']
        mean_onset = analysis['rainy_season_start_doy']
        
        if mean_onset == 0:
            return 0.5  # Default moderate confidence
        
        cv = variability / mean_onset  # Coefficient of variation
        
        # Map CV to confidence (0-1 range)
        # CV < 0.1 = high confidence (0.9-1.0)
        # CV > 0.3 = low confidence (0.0-0.5)
        if cv < 0.1:
            confidence = 0.9 + (0.1 - cv)
        elif cv > 0.3:
            confidence = max(0.0, 0.5 - (cv - 0.3) * 2)
        else:
            confidence = 0.5 + (0.1 - cv) * 2
        
        # Ensure bounds
        return max(0.0, min(1.0, confidence))



class PlantingCalendarService:
    """
    Service for calculating and managing planting calendars.
    Integrates weather data analysis with planting window calculations.
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
    """
    
    @classmethod
    def get_planting_window_for_village(cls, village, crop=None, force_refresh=False):
        """
        Get or calculate planting window for a village.
        
        Args:
            village: Village model instance
            crop: Optional Crop model instance
            force_refresh: If True, recalculate even if cached
            
        Returns:
            PlantingWindow model instance
            
        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
        """
        from .models import PlantingWindow
        from datetime import date
        
        # Check if we have a recent calculation (within last 30 days)
        if not force_refresh:
            recent_window = PlantingWindow.objects.filter(
                village=village,
                crop=crop,
                calculated_at__gte=timezone.now() - timedelta(days=30)
            ).first()
            
            if recent_window:
                logger.info(f"Using cached planting window for {village.name}")
                return recent_window
        
        # Calculate new planting window
        logger.info(f"Calculating planting window for {village.name}")
        
        # Get coordinates from village
        lat = village.location.y
        lon = village.location.x
        
        # Fetch 10 years of rainfall data
        rainfall_data = WeatherService.fetch_rainfall_data(lat, lon)
        
        # Calculate planting window
        window_data = WeatherService.calculate_planting_window(rainfall_data)
        
        # Create or update PlantingWindow record
        planting_window, created = PlantingWindow.objects.update_or_create(
            village=village,
            crop=crop,
            defaults={
                'start_date': window_data['start_date'],
                'end_date': window_data['end_date'],
                'confidence_level': window_data['confidence_level']
            }
        )
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} planting window for {village.name}")
        
        return planting_window
    
    @classmethod
    def get_planting_windows_for_district(cls, district, crop=None):
        """
        Get planting windows for all villages in a district.
        
        Args:
            district: District model instance
            crop: Optional Crop model instance
            
        Returns:
            List of PlantingWindow instances
        """
        windows = []
        for village in district.villages.all():
            try:
                window = cls.get_planting_window_for_village(village, crop)
                windows.append(window)
            except Exception as e:
                logger.error(f"Failed to get planting window for {village.name}: {e}")
                continue
        
        return windows


class CropSuitabilityServiceError(Exception):
    """Custom exception for crop suitability service errors."""
    pass


class CropSuitabilityService:
    """
    Service class for calculating crop suitability scores.
    Analyzes soil, elevation, and climate data to rank crops by suitability.
    
    Validates: Requirements 3.4, 3.5, 3.6
    """
    
    @classmethod
    def calculate_suitability(
        cls,
        crop,
        soil_data: Dict,
        elevation: float,
        climate_data: Optional[Dict] = None
    ) -> float:
        """
        Calculate suitability score for a specific crop based on location conditions.
        
        Args:
            crop: Crop model instance
            soil_data: Dictionary with clay_content, sand_content, ph_level, organic_carbon
            elevation: Elevation in meters
            climate_data: Optional dictionary with rainfall and temperature data
            
        Returns:
            Suitability score between 0 and 100
            
        Validates: Requirements 3.4
        """
        # Calculate individual component scores
        soil_score = cls._calculate_soil_score(crop, soil_data)
        elevation_score = cls._calculate_elevation_score(crop, elevation)
        
        # If climate data is available, include it in the calculation
        if climate_data:
            climate_score = cls._calculate_climate_score(crop, climate_data)
            # Weighted average: soil 40%, elevation 30%, climate 30%
            total_score = (soil_score * 0.4) + (elevation_score * 0.3) + (climate_score * 0.3)
        else:
            # Without climate data: soil 60%, elevation 40%
            total_score = (soil_score * 0.6) + (elevation_score * 0.4)
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, total_score))
    
    @classmethod
    def _calculate_soil_score(cls, crop, soil_data: Dict) -> float:
        """
        Calculate soil suitability score based on pH, clay content, and organic carbon.
        
        Args:
            crop: Crop model instance
            soil_data: Dictionary with soil properties
            
        Returns:
            Soil score between 0 and 100
        """
        ph = soil_data.get('ph_level', 0)
        clay = soil_data.get('clay_content', 0)
        organic_carbon = soil_data.get('organic_carbon', 0)
        
        # Calculate pH score
        ph_score = cls._calculate_range_score(
            ph,
            crop.min_ph,
            crop.max_ph,
            optimal_range=0.5  # pH within 0.5 of ideal is optimal
        )
        
        # Calculate clay content score
        clay_score = cls._calculate_range_score(
            clay,
            crop.min_clay_content,
            crop.max_clay_content,
            optimal_range=5.0  # Within 5% of ideal is optimal
        )
        
        # Calculate organic carbon score (higher is generally better, but check minimum)
        if organic_carbon >= crop.min_organic_carbon:
            # Score based on how much above minimum
            oc_score = min(100.0, 70.0 + (organic_carbon - crop.min_organic_carbon) * 3)
        else:
            # Penalize if below minimum
            oc_score = (organic_carbon / crop.min_organic_carbon) * 70.0
        
        # Weighted average: pH 40%, clay 35%, organic carbon 25%
        soil_score = (ph_score * 0.4) + (clay_score * 0.35) + (oc_score * 0.25)
        
        return soil_score
    
    @classmethod
    def _calculate_elevation_score(cls, crop, elevation: float) -> float:
        """
        Calculate elevation suitability score.
        
        Args:
            crop: Crop model instance
            elevation: Elevation in meters
            
        Returns:
            Elevation score between 0 and 100
        """
        return cls._calculate_range_score(
            elevation,
            crop.min_elevation,
            crop.max_elevation,
            optimal_range=100.0  # Within 100m of ideal is optimal
        )
    
    @classmethod
    def _calculate_climate_score(cls, crop, climate_data: Dict) -> float:
        """
        Calculate climate suitability score based on rainfall and temperature.
        
        Args:
            crop: Crop model instance
            climate_data: Dictionary with rainfall and temperature data
            
        Returns:
            Climate score between 0 and 100
        """
        rainfall = climate_data.get('annual_rainfall', 0)
        temperature = climate_data.get('mean_temperature', 0)
        
        # Calculate rainfall score
        rainfall_score = cls._calculate_range_score(
            rainfall,
            crop.min_rainfall,
            crop.max_rainfall,
            optimal_range=100.0  # Within 100mm of ideal is optimal
        )
        
        # Calculate temperature score
        temp_score = cls._calculate_range_score(
            temperature,
            crop.min_temperature,
            crop.max_temperature,
            optimal_range=2.0  # Within 2°C of ideal is optimal
        )
        
        # Weighted average: rainfall 60%, temperature 40%
        climate_score = (rainfall_score * 0.6) + (temp_score * 0.4)
        
        return climate_score
    
    @classmethod
    def _calculate_range_score(
        cls,
        value: float,
        min_value: float,
        max_value: float,
        optimal_range: float = 0.0
    ) -> float:
        """
        Calculate a score based on how well a value fits within a range.
        
        Args:
            value: The actual value
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value
            optimal_range: Range around the midpoint considered optimal
            
        Returns:
            Score between 0 and 100
        """
        # If value is outside the acceptable range, score is low
        if value < min_value:
            # Penalize based on how far below minimum
            distance_below = min_value - value
            range_size = max_value - min_value
            penalty_factor = distance_below / range_size
            return max(0.0, 50.0 - (penalty_factor * 50.0))
        
        if value > max_value:
            # Penalize based on how far above maximum
            distance_above = value - max_value
            range_size = max_value - min_value
            penalty_factor = distance_above / range_size
            return max(0.0, 50.0 - (penalty_factor * 50.0))
        
        # Value is within acceptable range
        midpoint = (min_value + max_value) / 2.0
        distance_from_midpoint = abs(value - midpoint)
        
        # If within optimal range of midpoint, score is 100
        if distance_from_midpoint <= optimal_range:
            return 100.0
        
        # Otherwise, score decreases as we move away from midpoint
        max_distance = (max_value - min_value) / 2.0
        score = 100.0 - ((distance_from_midpoint - optimal_range) / max_distance) * 30.0
        
        return max(70.0, score)  # Minimum score of 70 if within range
    
    @classmethod
    def get_crop_requirements(cls, crop_id: str) -> Dict:
        """
        Get the ideal conditions for a specific crop.
        
        Args:
            crop_id: UUID of the crop
            
        Returns:
            Dictionary containing crop requirements
            
        Raises:
            CropSuitabilityServiceError: If crop not found
            
        Validates: Requirements 3.6
        """
        from .models import Crop
        
        try:
            crop = Crop.objects.get(id=crop_id)
        except Crop.DoesNotExist:
            raise CropSuitabilityServiceError(f"Crop with id {crop_id} not found")
        
        return {
            'name': crop.name,
            'name_chichewa': crop.name_chichewa,
            'scientific_name': crop.scientific_name,
            'soil_requirements': {
                'min_ph': crop.min_ph,
                'max_ph': crop.max_ph,
                'min_clay_content': crop.min_clay_content,
                'max_clay_content': crop.max_clay_content,
                'min_organic_carbon': crop.min_organic_carbon,
            },
            'climate_requirements': {
                'min_rainfall': crop.min_rainfall,
                'max_rainfall': crop.max_rainfall,
                'min_temperature': crop.min_temperature,
                'max_temperature': crop.max_temperature,
            },
            'elevation_requirements': {
                'min_elevation': crop.min_elevation,
                'max_elevation': crop.max_elevation,
            },
            'growing_season_days': crop.growing_season_days,
        }
    
    @classmethod
    def rank_crops(
        cls,
        location,
        soil_data: Optional[Dict] = None,
        climate_data: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Calculate suitability scores for all crops and return them ranked.
        
        Args:
            location: Village or District model instance with location/centroid
            soil_data: Optional pre-fetched soil data
            climate_data: Optional pre-fetched climate data
            
        Returns:
            List of dictionaries with crop info and suitability scores, sorted by score
            
        Validates: Requirements 3.4, 3.5, 3.6
        """
        from .models import Crop
        
        # Get location coordinates
        if hasattr(location, 'location'):
            # Village
            lat = location.location.y
            lon = location.location.x
            elevation = location.elevation
        elif hasattr(location, 'centroid'):
            # District
            lat = location.centroid.y
            lon = location.centroid.x
            elevation = None  # Districts don't have elevation
        else:
            raise CropSuitabilityServiceError("Invalid location object")
        
        # Fetch soil data if not provided
        if soil_data is None:
            try:
                soil_data = SoilService.fetch_soil_properties(lat, lon)
            except SoilServiceError as e:
                logger.error(f"Failed to fetch soil data: {e}")
                raise CropSuitabilityServiceError(f"Failed to fetch soil data: {str(e)}")
        
        # Use a default elevation if not available
        if elevation is None:
            elevation = 1000.0  # Default elevation for Malawi (approximate average)
            logger.warning(f"No elevation data available, using default: {elevation}m")
        
        # Get all crops
        crops = Crop.objects.all()
        
        if not crops.exists():
            logger.warning("No crops found in database")
            return []
        
        # Calculate suitability for each crop
        results = []
        for crop in crops:
            try:
                score = cls.calculate_suitability(
                    crop,
                    soil_data,
                    elevation,
                    climate_data
                )
                
                results.append({
                    'crop_id': str(crop.id),
                    'name': crop.name,
                    'name_chichewa': crop.name_chichewa,
                    'scientific_name': crop.scientific_name,
                    'suitability_score': round(score, 2),
                    'soil_requirements': {
                        'min_ph': crop.min_ph,
                        'max_ph': crop.max_ph,
                        'min_clay_content': crop.min_clay_content,
                        'max_clay_content': crop.max_clay_content,
                        'min_organic_carbon': crop.min_organic_carbon,
                    },
                    'elevation_requirements': {
                        'min_elevation': crop.min_elevation,
                        'max_elevation': crop.max_elevation,
                    },
                })
            except Exception as e:
                logger.error(f"Failed to calculate suitability for {crop.name}: {e}")
                continue
        
        # Sort by suitability score (highest first)
        results.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return results
    
    @classmethod
    def generate_suitability_raster(
        cls,
        crop,
        bounds: Dict,
        resolution: float = 0.01
    ) -> List[Dict]:
        """
        Generate a grid of suitability scores for map visualization.
        
        Args:
            crop: Crop model instance
            bounds: Dictionary with 'min_lat', 'max_lat', 'min_lon', 'max_lon'
            resolution: Grid resolution in degrees (default 0.01 = ~1km)
            
        Returns:
            List of dictionaries with lat, lon, and suitability_score
            
        Note: This is a simplified implementation for the 2-week project.
        A production system would use raster processing libraries.
        """
        import numpy as np
        
        min_lat = bounds['min_lat']
        max_lat = bounds['max_lat']
        min_lon = bounds['min_lon']
        max_lon = bounds['max_lon']
        
        # Create grid of points
        lats = np.arange(min_lat, max_lat, resolution)
        lons = np.arange(min_lon, max_lon, resolution)
        
        results = []
        
        # Calculate suitability for each grid point
        # Note: This is simplified - in production, we'd batch API calls
        for lat in lats:
            for lon in lons:
                try:
                    # Fetch soil data for this point
                    soil_data = SoilService.fetch_soil_properties(lat, lon)
                    
                    # Use default elevation (would need elevation raster in production)
                    elevation = 1000.0
                    
                    # Calculate suitability
                    score = cls.calculate_suitability(crop, soil_data, elevation)
                    
                    results.append({
                        'lat': lat,
                        'lon': lon,
                        'suitability_score': round(score, 2)
                    })
                except Exception as e:
                    logger.debug(f"Failed to calculate suitability for point ({lat}, {lon}): {e}")
                    continue
        
        return results


class SoilServiceError(Exception):
    """Custom exception for soil service errors."""
    pass


class SoilService:
    """
    Service class for handling soil data integration with SoilGrids API.
    Implements caching with 24-hour TTL and fallback to cached data on API failure.
    
    Validates: Requirements 3.1, 3.2
    """
    
    REQUEST_TIMEOUT = 30  # seconds
    
    # SoilGrids API base URL
    SOILGRIDS_API_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    
    # Soil properties to request from SoilGrids API
    # Using standard SoilGrids property names
    PROPERTIES = [
        "clay",           # Clay content (%)
        "sand",           # Sand content (%)
        "phh2o",          # pH in H2O
        "soc",            # Soil organic carbon (g/kg)
    ]
    
    # Depth range (0-5cm topsoil - SoilGrids standard depth)
    DEPTH = "0-5cm"
    
    @classmethod
    def fetch_soil_properties(
        cls,
        lat: float,
        lon: float
    ) -> Dict:
        """
        Retrieve soil properties from SoilGrids API.
        Uses cache if available and not expired, otherwise fetches from API.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            
        Returns:
            Dictionary containing soil properties (clay, sand, pH, organic carbon)
            
        Raises:
            SoilServiceError: If API request fails and no cache available
            
        Validates: Requirements 3.1, 3.2
        """
        from .models import SoilCache
        
        # Validate coordinates
        if not cls._validate_coordinates(lat, lon):
            raise SoilServiceError(
                f"Invalid coordinates: lat={lat}, lon={lon}. "
                "Latitude must be between -90 and 90, longitude between -180 and 180."
            )
        
        # Create cache key
        location_key = SoilCache.create_location_key(lat, lon)
        
        # Check cache first (but don't delete if expired - we might need it as fallback)
        try:
            cache = SoilCache.objects.get(location_key=location_key)
            if not cache.is_expired():
                logger.info(f"Using cached soil data for {location_key}")
                return cache.data
        except SoilCache.DoesNotExist:
            cache = None
        
        # Fetch from API
        try:
            data = cls._fetch_from_api(lat, lon)
            # Cache the data
            cls._cache_soil_data(location_key, lat, lon, data)
            return data
        except Exception as e:
            logger.error(f"Failed to fetch soil data from API: {e}")
            # Try to use expired cache as fallback
            if cache:
                logger.warning(f"Using stale cached soil data for {location_key}")
                fallback_data = cache.data.copy()
                fallback_data['_stale_cache'] = True
                fallback_data['_cache_warning'] = "Using cached data due to API unavailability"
                return fallback_data
            raise SoilServiceError(
                f"Failed to fetch soil data and no cache available: {str(e)}"
            )
    
    @classmethod
    def _fetch_from_api(
        cls,
        lat: float,
        lon: float
    ) -> Dict:
        """
        Fetch soil data directly from SoilGrids API.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            
        Returns:
            Parsed soil data dictionary
            
        Raises:
            SoilServiceError: If API request fails
            
        Validates: Requirements 3.1, 3.2
        """
        # Build API request parameters
        params = {
            "lon": lon,
            "lat": lat,
            "property": cls.PROPERTIES,
            "depth": cls.DEPTH,
            "value": "mean"  # Get mean values
        }
        
        logger.info(f"Fetching soil data from SoilGrids API for lat={lat}, lon={lon}")
        
        try:
            response = requests.get(
                cls.SOILGRIDS_API_URL,
                params=params,
                timeout=cls.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Extract and validate soil properties
            parsed_data = cls._parse_soil_response(data)
            
            return parsed_data
            
        except requests.exceptions.Timeout:
            raise SoilServiceError("SoilGrids API request timed out")
        except requests.exceptions.RequestException as e:
            raise SoilServiceError(f"SoilGrids API request failed: {str(e)}")
        except ValueError as e:
            raise SoilServiceError(f"Failed to parse SoilGrids API response: {str(e)}")
    
    @classmethod
    def _parse_soil_response(cls, response_data: Dict) -> Dict:
        """
        Parse and extract relevant soil properties from SoilGrids API response.
        
        Args:
            response_data: Raw API response
            
        Returns:
            Parsed data with clay, sand, pH, and organic carbon
            
        Raises:
            ValueError: If response structure is invalid
            
        Validates: Requirements 3.2
        """
        try:
            properties = response_data.get('properties', {})
            layers = properties.get('layers', [])
            
            # Extract soil properties from layers
            soil_data = {}
            
            for layer in layers:
                property_name = layer.get('name')
                depths = layer.get('depths', [])
                
                # Get the first depth layer (0-30cm)
                if depths:
                    depth_data = depths[0]
                    values = depth_data.get('values')
                    
                    if values:
                        mean_value = values.get('mean')
                        
                        # Skip if mean_value is None
                        if mean_value is None:
                            continue
                        
                        # Map property names and convert units
                        if property_name == 'clay':
                            soil_data['clay_content'] = mean_value / 10.0  # Convert g/kg to %
                        elif property_name == 'sand':
                            soil_data['sand_content'] = mean_value / 10.0  # Convert g/kg to %
                        elif property_name == 'phh2o':
                            soil_data['ph_level'] = mean_value / 10.0  # Convert to pH scale
                        elif property_name == 'soc':
                            soil_data['organic_carbon'] = mean_value / 10.0  # Convert dg/kg to g/kg
            
            # Validate that we got all required properties
            required_props = ['clay_content', 'sand_content', 'ph_level', 'organic_carbon']
            missing_props = [prop for prop in required_props if prop not in soil_data]
            
            if missing_props:
                raise ValueError(f"Missing soil properties in API response: {missing_props}")
            
            # Add metadata
            soil_data['metadata'] = {
                'latitude': response_data.get('geometry', {}).get('coordinates', [None, None])[1],
                'longitude': response_data.get('geometry', {}).get('coordinates', [None, None])[0],
                'source': 'SoilGrids API',
                'depth': cls.DEPTH,
                'fetched_at': timezone.now().isoformat(),
            }
            
            return soil_data
            
        except (KeyError, TypeError, IndexError) as e:
            raise ValueError(f"Invalid API response structure: {str(e)}")
    
    @classmethod
    def _validate_coordinates(cls, lat: float, lon: float) -> bool:
        """
        Validate latitude and longitude coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if valid, False otherwise
        """
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    @classmethod
    def _get_cached_soil(cls, location_key: str) -> Optional[Dict]:
        """
        Retrieve valid cached soil data.
        
        Args:
            location_key: Cache key for location
            
        Returns:
            Cached data dictionary or None
        """
        from .models import SoilCache
        
        cache = SoilCache.get_cached_data(location_key)
        if cache:
            return cache.data
        return None
    
    @classmethod
    def _cache_soil_data(
        cls,
        location_key: str,
        lat: float,
        lon: float,
        data: Dict
    ) -> None:
        """
        Store soil data in cache with 24-hour TTL.
        
        Args:
            location_key: Cache key for location
            lat: Latitude
            lon: Longitude
            data: Soil data to cache
        """
        from .models import SoilCache
        
        try:
            # Update existing cache or create new
            cache, created = SoilCache.objects.update_or_create(
                location_key=location_key,
                defaults={
                    'latitude': lat,
                    'longitude': lon,
                    'data': data,
                    'expires_at': timezone.now() + timedelta(hours=24)
                }
            )
            action = "Created" if created else "Updated"
            logger.info(f"{action} soil cache for {location_key}")
        except Exception as e:
            logger.error(f"Failed to cache soil data: {e}")
            # Don't raise exception - caching failure shouldn't break the request
