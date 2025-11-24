# Mlimi Wanzeru (Smart Farmer)

A database-driven web application designed to empower smallholder farmers in Malawi with location-specific, data-driven agricultural advisory services.

## Table of Contents

1. [The Problem](#the-problem)
2. [Our Solution](#our-solution)
3. [Key Features](#key-features)
4. [Technology Stack](#technology-stack)
5. [Data Sources](#data-sources)
6. [System Architecture](#system-architecture)
7. [Installation & Setup](#installation--setup)
8. [Usage](#usage)
9. [Project Team](#project-team)
10. [Future Enhancements](#future-enhancements)
11. [License](#license)

## The Problem

### Context: Smallholder Agriculture in Malawi

Malawi's economy is heavily dependent on agriculture, which employs over 80% of the workforce and contributes about 30% to GDP. The majority of farmers are smallholders who face several critical challenges:

- **Climate Vulnerability**: Reliance on rain-fed agriculture makes farmers highly vulnerable to erratic rainfall patterns, droughts, and floods exacerbated by climate change.
- **Limited Access to Information**: Farmers lack access to timely, location-specific advice on planting times, crop selection, and market opportunities.
- **Low Productivity**: Without scientific guidance, farmers often experience low crop yields, contributing to food insecurity and poverty.
- **Market Inefficiencies**: Farmers struggle to find the best markets for their produce and often receive unfavorable prices due to information asymmetry.

### The Spatial Dimension

These challenges have a strong spatial component that existing solutions often ignore:

- **Weather patterns** vary significantly across different regions of Malawi
- **Soil suitability** for different crops changes based on location-specific conditions
- **Market accessibility** depends on physical distance and transportation networks
- **Climate risks** like flooding are highly localized

## Our Solution

**Mlimi Wanzeru** (which means "Smart Farmer" in Chichewa) is a database-driven web application that provides personalized agricultural advisory services based on the farmer's specific location and local conditions.

### Core Innovation

Unlike generic agricultural advice, our solution:
- Uses **spatial analysis** to provide location-specific recommendations
- Integrates **multiple data sources** (weather, soil, markets) into a unified platform
- Is **accessible** via basic web browsers, reaching farmers with limited technology access
- Provides **actionable insights** in simple, understandable language

## Key Features

### 1. Personalized Planting Calendar
- **Input**: User selects their district or village
- **Output**: Optimal planting dates based on historical rainfall patterns and short-term weather forecasts
- **Benefit**: Helps farmers time their planting to maximize rainfall utilization

### 2. Crop Suitability Mapping
- **Input**: User location and preferred crops
- **Output**: Interactive map showing suitability scores for different crops based on soil type, elevation, and climate
- **Benefit**: Guides farmers toward crops most likely to thrive in their specific conditions

### 3. Market Intelligence
- **Input**: User location and crop type
- **Output**: Map of nearby markets with current prices and contact information
- **Benefit**: Helps farmers get better prices for their produce

### 4. Input Supplier Locator
- **Input**: User location and required inputs (seeds, fertilizer)
- **Output**: Directory of nearby agro-dealers with locations and products
- **Benefit**: Reduces time and cost of accessing agricultural inputs

## Technology Stack

### Backend
- **Framework**: Python with Django
- **Database**: PostgreSQL with PostGIS extension
- **API**: Django REST Framework
- **Spatial Analysis**: GeoDjango, Rasterio, GDAL

### Frontend
- **Mapping**: Leaflet.js with custom tile layers
- **UI Framework**: Reactjs/Nextjs with Tailwind CSS

### Data Processing
- **QGIS**: For initial data processing and analysis
- **Python Scripts**: For automated data updates and processing

## Data Sources

| Data Type | Source | Usage |
|-----------|--------|-------|
| **Weather Data** | NASA POWER API | Historical climate data and planting calendars |
| **Soil Data** | SoilGrids | Crop suitability analysis |
| **Elevation Data** | SRTM via USGS EarthExplorer | Topographic analysis |
| **Market Locations** | OpenStreetMap | Market and agro-dealer locations |
| **Administrative Boundaries** | Humanitarian Data Exchange (HDX) | User location mapping |
| **Market Prices** | Malawi Agricultural Market Information System | Price information (manual entry in prototype) |