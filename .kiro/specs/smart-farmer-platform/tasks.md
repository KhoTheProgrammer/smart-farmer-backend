# Implementation Plan

- [x] 1. Set up project infrastructure and database

  - Create Django project with GeoDjango configuration
  - Set up PostgreSQL with PostGIS extension
  - Configure environment variables for API keys
  - Create initial database migrations
  - _Requirements: 5.1, 5.2, 5.4_

- [ ]\* 1.1 Write property test for coordinate validation

  - **Property 4: Coordinate retrieval validity**
  - **Validates: Requirements 1.4**

- [ ] 2. Implement location models and services

  - Create District and Village models with spatial fields
  - Implement LocationService with district/village queries
  - Add spatial indexes for performance
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]\* 2.1 Write property test for district list completeness

  - **Property 1: District list completeness**
  - **Validates: Requirements 1.1**

- [ ]\* 2.2 Write property test for village-district association

  - **Property 2: Village-district association**
  - **Validates: Requirements 1.2**

- [ ]\* 2.3 Write property test for location coordinate persistence

  - **Property 3: Location coordinate persistence**
  - **Validates: Requirements 1.3**

- [ ]\* 2.4 Write property test for point-in-polygon accuracy

  - **Property 28: Point-in-polygon accuracy**
  - **Validates: Requirements 8.4**

- [ ] 3. Import administrative boundary data

  - Download Malawi boundaries from HDX
  - Create management command to import GeoJSON
  - Validate and store district polygons and village points
  - Verify CRS is WGS84 (EPSG:4326)
  - _Requirements: 5.1, 5.2, 5.4_

- [ ]\* 3.1 Write property test for GeoJSON parsing correctness

  - **Property 17: GeoJSON parsing correctness**
  - **Validates: Requirements 5.1, 5.2**

- [ ]\* 3.2 Write property test for CRS validation

  - **Property 18: Coordinate reference system validation**
  - **Validates: Requirements 5.4**

- [ ] 4. Implement weather data integration

  - Create WeatherCache model for caching
  - Implement WeatherService with NASA POWER API integration
  - Add cache lookup and storage logic (24-hour TTL)
  - Handle API errors and fallback to cache
  - _Requirements: 2.1, 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ]\* 4.1 Write property test for weather API integration

  - **Property 5: Weather API integration**
  - **Validates: Requirements 2.1**

- [ ]\* 4.2 Write property test for NASA POWER API parameters

  - **Property 30: NASA POWER API parameter correctness**
  - **Validates: Requirements 9.1**

- [ ]\* 4.3 Write property test for JSON parsing

  - **Property 31: JSON parsing robustness**
  - **Validates: Requirements 9.2**

- [ ]\* 4.4 Write property test for weather parameter extraction

  - **Property 32: Weather parameter extraction**
  - **Validates: Requirements 9.5**

- [ ]\* 4.5 Write property test for weather data caching

  - **Property 21: Weather data caching**
  - **Validates: Requirements 9.3**

- [ ]\* 4.6 Write property test for API fallback behavior

  - **Property 22: API fallback behavior**
  - **Validates: Requirements 9.4**

- [ ] 5. Implement planting calendar calculations

  - Create PlantingWindow model
  - Implement rainfall pattern analysis (10-year historical data)
  - Calculate optimal planting window based on rainy season onset
  - Calculate confidence level based on rainfall variability
  - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [ ]\* 5.1 Write property test for rainfall analysis period

  - **Property 6: Rainfall analysis period**
  - **Validates: Requirements 2.2**

- [ ]\* 5.2 Write property test for planting window validity

  - **Property 7: Planting window validity**
  - **Validates: Requirements 2.3, 2.4**

- [ ]\* 5.3 Write property test for confidence level bounds

  - **Property 8: Confidence level bounds**
  - **Validates: Requirements 2.5**

- [ ] 6. Checkpoint - Ensure all backend core services are working

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement soil data integration

  - Create SoilCache model for caching
  - Implement SoilService with SoilGrids API integration
  - Parse soil properties (clay, sand, pH, organic carbon)
  - Add cache lookup and storage logic
  - _Requirements: 3.1, 3.2_

- [ ]\* 7.1 Write property test for soil data retrieval

  - **Property 9: Soil data retrieval**
  - **Validates: Requirements 3.1**

- [ ]\* 7.2 Write property test for soil property completeness

  - **Property 10: Soil property completeness**
  - **Validates: Requirements 3.2**

- [ ] 8. Import elevation data

  - Download SRTM elevation data for Malawi
  - Process raster files using GDAL
  - Extract elevation values for village locations
  - Store elevation in Village model
  - _Requirements: 3.3, 5.3_

- [ ] 9. Create crop database

  - Create Crop model with soil, climate, and elevation requirements
  - Add common Malawian crops (maize, tobacco, groundnuts, beans, cassava, sweet potato)
  - Include Chichewa translations for crop names
  - _Requirements: 3.4, 3.5, 3.6, 7.2, 7.3_

- [ ] 10. Implement crop suitability calculations

  - Create CropSuitabilityService
  - Implement suitability scoring algorithm
  - Calculate scores based on soil, elevation, and climate match
  - Rank crops by suitability score
  - _Requirements: 3.4, 3.5, 3.6_

- [ ]\* 10.1 Write property test for suitability score calculation

  - **Property 11: Suitability score calculation**
  - **Validates: Requirements 3.4**

- [ ]\* 10.2 Write property test for crop ranking order

  - **Property 12: Crop ranking order**
  - **Validates: Requirements 3.5**

- [ ]\* 10.3 Write property test for crop result completeness

  - **Property 13: Crop result completeness**
  - **Validates: Requirements 3.6**

- [ ] 11. Create REST API endpoints

  - Implement location endpoints (districts, villages, reverse geocode)
  - Implement planting calendar endpoint
  - Implement crop suitability endpoint
  - Implement crop suitability map data endpoint
  - Add API documentation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4_

- [ ]\* 11.1 Write property test for distance calculation accuracy

  - **Property 27: Distance calculation accuracy**
  - **Validates: Requirements 8.2**

- [ ]\* 11.2 Write property test for query performance monitoring

  - **Property 29: Query performance monitoring**
  - **Validates: Requirements 8.5**

- [ ] 12. Checkpoint - Ensure all backend API endpoints work correctly

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Set up Next.js frontend project

  - Initialize Next.js project with TypeScript
  - Configure Tailwind CSS
  - Set up API client for backend communication
  - Create basic layout and navigation
  - _Requirements: 6.1, 6.5_

- [ ] 14. Implement location selector component

  - Create LocationSelector component with district dropdown
  - Add village dropdown that updates based on district selection
  - Store selected location in state
  - Display selected location coordinates
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 15. Implement planting calendar component

  - Create PlantingCalendar component
  - Fetch planting window data from API
  - Display start and end dates visually
  - Show confidence level indicator
  - Add loading and error states
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 16. Implement crop suitability list component

  - Create CropSuitabilityList component
  - Fetch and display ranked crops
  - Show suitability scores with visual indicators
  - Display soil and elevation requirements for each crop
  - Add crop selection for map view
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 17. Integrate Leaflet.js for mapping

  - Install and configure Leaflet.js
  - Create base map component
  - Add district and village boundary layers
  - Implement map centering on user location
  - Add touch gesture support for mobile
  - _Requirements: 4.1, 4.5, 6.2_

- [ ]\* 17.1 Write property test for map centering accuracy

  - **Property 14: Map centering accuracy**
  - **Validates: Requirements 4.1**

- [ ] 18. Implement crop suitability map visualization

  - Create CropSuitabilityMap component
  - Fetch suitability raster data from API
  - Render color-coded suitability zones (red to green gradient)
  - Update map when crop selection changes
  - Add click handler to show point-specific suitability
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]\* 18.1 Write property test for color gradient mapping

  - **Property 15: Color gradient mapping**
  - **Validates: Requirements 4.2**

- [ ]\* 18.2 Write property test for map data consistency

  - **Property 16: Map data consistency**
  - **Validates: Requirements 4.3**

- [ ] 19. Implement language switching

  - Create language context for English/Chichewa
  - Detect browser language preference
  - Add language selector component
  - Implement translation for all UI text
  - Persist language preference in localStorage
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]\* 19.1 Write property test for language detection

  - **Property 23: Language detection**
  - **Validates: Requirements 7.1**

- [ ]\* 19.2 Write property test for language-content mapping

  - **Property 24: Language-content mapping**
  - **Validates: Requirements 7.2, 7.3**

- [ ]\* 19.3 Write property test for language preference override

  - **Property 25: Language preference override**
  - **Validates: Requirements 7.4**

- [ ]\* 19.4 Write property test for language preference persistence

  - **Property 26: Language preference persistence**
  - **Validates: Requirements 7.5**

- [ ] 20. Implement responsive mobile design

  - Make all components responsive with Tailwind breakpoints
  - Optimize layout for small screens
  - Test touch interactions on mobile
  - Optimize API responses for mobile (reduce payload size)
  - Test load times on simulated 3G connection
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]\* 20.1 Write property test for mobile load time

  - **Property 19: Mobile load time**
  - **Validates: Requirements 6.3**

- [ ]\* 20.2 Write property test for mobile data optimization

  - **Property 20: Mobile data optimization**
  - **Validates: Requirements 6.4**

- [ ] 21. Integration testing and bug fixes

  - Test complete user flow: location selection → planting calendar → crop suitability → map
  - Test on multiple browsers (Chrome, Firefox)
  - Test on mobile devices
  - Fix any bugs discovered
  - Verify all API endpoints work correctly
  - _Requirements: All_

- [ ] 22. Final checkpoint - Make sure all tests are passing

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 23. Documentation and deployment preparation
  - Write README with setup instructions
  - Document API endpoints
  - Create sample data loading script
  - Prepare deployment configuration (if needed)
  - Create presentation materials
  - _Requirements: All_
