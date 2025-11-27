# Production Data Strategy

## ✅ What's Already Included (Deploys Automatically)

### Crops Data (6 crops)

- Maize, Tobacco, Groundnuts, Beans, Cassava, Sweet Potato
- Includes soil, climate, and elevation requirements
- **File**: `weather/migrations/0004_add_malawian_crops.py`
- **Status**: ✅ Ready to deploy

### Sample Locations (5 districts, 12 villages)

- Major cities: Lilongwe, Blantyre, Mzuzu, Zomba, Kasungu
- Key villages in each district
- Includes coordinates and elevation data
- **File**: `weather/migrations/0005_add_sample_locations.py`
- **Status**: ✅ Ready to deploy

## 📊 What This Gives You

### Working Features

- ✅ Crops API - List all crops
- ✅ Crop details with requirements
- ✅ Crop suitability analysis by lat/lon
- ✅ Districts API - 5 major districts
- ✅ Villages API - 12 sample villages
- ✅ Weather data (NASA POWER API)
- ✅ Soil data (SoilGrids API)
- ✅ Planting calendar
- ✅ Location-based queries

### API Endpoints That Work

```bash
# Crops
GET /api/weather/crops/
GET /api/weather/crops/{id}/
GET /api/weather/crops/{id}/suitability/?lat=-13.98&lon=33.78

# Locations
GET /api/locations/districts/
GET /api/locations/districts/{id}/
GET /api/locations/districts/{id}/villages/
GET /api/locations/villages/
GET /api/locations/villages/nearby/?lat=-13.98&lon=33.78&radius=50

# Calendar
GET /api/weather/planting-calendar/?lat=-13.98&lon=33.78&season=rainy
```

## 🎯 For Full Production (Optional)

If you need all 28 districts and 400+ villages later:

### Option 1: Import via Render Shell

1. Upload GeoJSON files to cloud storage
2. Access Render shell
3. Run import commands
4. See `import_production_data.md` for details

### Option 2: Import from Local Machine

1. Get production database URL from Render
2. Run import commands locally
3. Data uploads directly to production

### Option 3: Add More Locations via Migration

I can create additional migrations with more districts/villages if needed.

## 📝 Current Data Summary

| Data Type        | Count | Size   | Status             |
| ---------------- | ----- | ------ | ------------------ |
| Crops            | 6     | Small  | ✅ In migration    |
| Districts        | 5     | Small  | ✅ In migration    |
| Villages         | 12    | Small  | ✅ In migration    |
| Full Districts   | 28    | 20MB   | ⏳ Optional import |
| Full Villages    | 400+  | 48MB   | ⏳ Optional import |
| Elevation Raster | -     | 100MB+ | ⏳ Optional import |

## 🚀 Deployment Impact

**With current migrations:**

- Deploy time: ~5-10 minutes
- Database size: < 10MB
- All core features work
- Perfect for demo and testing

**With full dataset:**

- Import time: +10-20 minutes
- Database size: ~100-200MB
- More comprehensive location data
- Better for production use

## 💡 Recommendation

**Start with migrations (current setup):**

1. Deploy with sample data
2. Test all features
3. Show to users/stakeholders
4. Import full dataset later if needed

**Benefits:**

- Fast deployment
- All features work
- Easy to test
- Can scale up anytime

## 🔄 Adding More Data Later

You can always add more data after deployment:

```bash
# Via Render shell
python manage.py import_boundaries \
    --districts data/malawi_districts.geojson \
    --villages data/malawi_villages.geojson

# Or via Django admin
# Add locations manually through the admin interface
```

## ✅ Ready to Deploy!

Your current setup includes:

- ✅ 6 crops with full requirements
- ✅ 5 major districts with boundaries
- ✅ 12 villages with coordinates and elevation
- ✅ All API endpoints functional
- ✅ No large file uploads needed

Just push and deploy! 🚀
