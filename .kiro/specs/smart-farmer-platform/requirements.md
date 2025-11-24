# Requirements Document

## Introduction

Mlimi Wanzeru (Smart Farmer) is a database-driven web application designed to empower smallholder farmers in Malawi with location-specific, data-driven agricultural advisory services. The system addresses critical challenges faced by Malawian farmers including climate vulnerability, limited access to information, low productivity, and market inefficiencies through spatial analysis and integration of multiple data sources.

## Glossary

- **System**: The Mlimi Wanzeru web application
- **User**: A smallholder farmer or agricultural extension worker accessing the application
- **District**: An administrative division in Malawi used for location identification
- **Village**: A smaller administrative unit within a district
- **Crop Suitability Score**: A numerical value (0-100) indicating how suitable a location is for growing a specific crop
- **Planting Window**: The optimal date range for planting a crop based on rainfall patterns
- **Agro-dealer**: A supplier of agricultural inputs such as seeds and fertilizer
- **Market Price**: The current selling price of agricultural produce at a specific market location
- **Spatial Data**: Geographic information including coordinates, boundaries, and location-based attributes
- **Weather Station**: A virtual or physical location providing meteorological data
- **Rainfall Pattern**: Historical precipitation data aggregated over multiple years
- **Soil Type**: Classification of soil based on texture, composition, and properties
- **Elevation**: Height above sea level measured in meters

## Requirements

### Requirement 1

**User Story:** As a farmer, I want to select my location by district and village, so that I can receive location-specific agricultural advice.

#### Acceptance Criteria

1. WHEN a user accesses the location selection interface THEN the System SHALL display a list of all districts in Malawi
2. WHEN a user selects a district THEN the System SHALL display all villages within that district
3. WHEN a user selects a village THEN the System SHALL store the user location coordinates for subsequent queries
4. WHEN a user location is stored THEN the System SHALL retrieve the latitude and longitude coordinates for that village
5. WHEN location data is unavailable for a selected village THEN the System SHALL use the district centroid coordinates as a fallback

### Requirement 2

**User Story:** As a farmer, I want to view optimal planting dates for my crops, so that I can maximize rainfall utilization and crop yields.

#### Acceptance Criteria

1. WHEN a user requests planting calendar information THEN the System SHALL retrieve historical rainfall data from NASA POWER API for the user location
2. WHEN historical rainfall data is retrieved THEN the System SHALL analyze rainfall patterns over the previous ten years
3. WHEN rainfall patterns are analyzed THEN the System SHALL calculate the optimal planting window based on onset of rainy season
4. WHEN the planting window is calculated THEN the System SHALL display start date and end date for planting
5. WHEN displaying planting dates THEN the System SHALL include confidence level based on rainfall variability

### Requirement 3

**User Story:** As a farmer, I want to see which crops are most suitable for my location, so that I can make informed decisions about what to plant.

#### Acceptance Criteria

1. WHEN a user requests crop suitability information THEN the System SHALL retrieve soil data from SoilGrids API for the user location
2. WHEN soil data is retrieved THEN the System SHALL extract soil properties including clay content, sand content, pH level, and organic carbon
3. WHEN a user requests crop suitability THEN the System SHALL retrieve elevation data for the user location
4. WHEN soil and elevation data are available THEN the System SHALL calculate suitability scores for each crop in the database
5. WHEN suitability scores are calculated THEN the System SHALL display crops ranked by suitability score from highest to lowest
6. WHEN displaying crop suitability THEN the System SHALL show suitability score, soil requirements, and elevation requirements for each crop

### Requirement 4

**User Story:** As a farmer, I want to view crop suitability on an interactive map, so that I can understand spatial variations in my region.

#### Acceptance Criteria

1. WHEN a user accesses the crop suitability map THEN the System SHALL display an interactive map centered on the user location
2. WHEN the map is displayed THEN the System SHALL render suitability zones using color gradients from red (unsuitable) to green (highly suitable)
3. WHEN a user selects a crop from the dropdown THEN the System SHALL update the map to show suitability for that specific crop
4. WHEN a user clicks on a map location THEN the System SHALL display detailed suitability information for that point
5. WHEN the map is rendered THEN the System SHALL overlay district and village boundaries for reference

### Requirement 5

**User Story:** As a system administrator, I want to import and process spatial data from multiple sources, so that the system has accurate and up-to-date information.

#### Acceptance Criteria

1. WHEN administrative boundary data is imported THEN the System SHALL parse GeoJSON format from HDX
2. WHEN administrative boundaries are parsed THEN the System SHALL store district polygons and village points in the PostGIS database
3. WHEN elevation data is imported THEN the System SHALL process SRTM raster files using GDAL
4. WHEN any spatial data is imported THEN the System SHALL validate coordinate reference system as WGS84 (EPSG:4326)

### Requirement 6

**User Story:** As a user, I want the application to work on my mobile phone, so that I can access it from the field.

#### Acceptance Criteria

1. WHEN a user accesses the application on a mobile device THEN the System SHALL display a responsive layout optimized for small screens
2. WHEN a user interacts with maps on mobile THEN the System SHALL support touch gestures including pinch-to-zoom and pan
3. WHEN a user accesses the application on a slow connection THEN the System SHALL load critical content within five seconds
4. WHEN displaying data on mobile THEN the System SHALL prioritize essential information and minimize data transfer
5. WHEN a user rotates their mobile device THEN the System SHALL adjust the layout to accommodate the new orientation

### Requirement 7

**User Story:** As a user, I want to view information in Chichewa, so that I can understand the agricultural advice in my native language.

#### Acceptance Criteria

1. WHEN a user accesses the application THEN the System SHALL detect the browser language preference
2. WHEN the browser language is Chichewa THEN the System SHALL display all interface text in Chichewa
3. WHEN the browser language is English THEN the System SHALL display all interface text in English
4. WHEN a user manually selects a language THEN the System SHALL override the browser preference and display content in the selected language
5. WHEN language is changed THEN the System SHALL persist the language preference for subsequent visits

### Requirement 8

**User Story:** As a developer, I want to query spatial data efficiently, so that the application responds quickly to user requests.

#### Acceptance Criteria

1. WHEN a spatial query is executed THEN the System SHALL use PostGIS spatial indexes for location-based searches
2. WHEN calculating distances THEN the System SHALL use the ST_Distance function with geography type for accurate results
3. WHEN retrieving nearby locations THEN the System SHALL use ST_DWithin for efficient radius searches
4. WHEN performing point-in-polygon queries THEN the System SHALL use ST_Contains to determine if a point falls within a district or village boundary
5. WHEN spatial queries exceed two seconds THEN the System SHALL log a performance warning for optimization review

### Requirement 9

**User Story:** As a data analyst, I want to access weather data through a reliable API, so that planting recommendations are based on accurate climate information.

#### Acceptance Criteria

1. WHEN requesting weather data THEN the System SHALL query the NASA POWER API with latitude and longitude parameters
2. WHEN the NASA POWER API returns data THEN the System SHALL parse JSON format responses
3. WHEN weather data is retrieved THEN the System SHALL cache the data for twenty-four hours to minimize API calls
4. WHEN the NASA POWER API is unavailable THEN the System SHALL use cached data and display a staleness warning
5. WHEN weather data includes multiple parameters THEN the System SHALL extract precipitation, temperature, and solar radiation values
