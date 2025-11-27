# Importing Data to Production Database

Guide for importing districts, villages, and elevation data to your production database on Render.

## 🎯 What Data Needs Importing?

### Already Included (Automatic)

- ✅ **Crops**: 6 Malawian crops via migration

### Needs Manual Import

- 📍 **Districts**: 28 districts (~20MB)
- 📍 **Villages**: 400+ villages (~48MB)
- 🗻 **Elevation**: SRTM raster data (~100MB+)

## 📋 Option 1: Import via Render Shell (Recommended)

### Step 1: Upload Data Files

You need to get your GeoJSON files accessible to the Render server. Options:

**A. Upload to GitHub (if files aren't too large)**

```bash
# Add data files to repo (if under 100MB)
cd smart-farmer-backend
git add data/malawi_districts.geojson data/malawi_villages.geojson
git commit -m "Add geospatial data for production"
git push origin main
```

**B. Use a cloud storage service**

- Upload to Google Drive, Dropbox, or AWS S3
- Get public download links
- Download in Render shell

### Step 2: Access Render Shell

1. Go to Render dashboard
2. Open your `mlimi-wanzeru-api` service
3. Click **"Shell"** tab
4. You'll get a terminal in your container

### Step 3: Import Data

In the Render shell:

```bash
# If data is in repo
python manage.py import_boundaries \
    --districts data/malawi_districts.geojson \
    --villages data/malawi_villages.geojson

# If downloading from URL
wget https://your-storage-url/malawi_districts.geojson
wget https://your-storage-url/malawi_villages.geojson
python manage.py import_boundaries \
    --districts malawi_districts.geojson \
    --villages malawi_villages.geojson
```

**Note**: This may take 5-10 minutes for large files.

## 📋 Option 2: Import from Local to Production Database

Connect directly to your Render PostgreSQL database from your local machine.

### Step 1: Get Database Credentials

From Render dashboard:

1. Go to your database
2. Copy the **External Database URL**

### Step 2: Import Locally

```bash
# Set production database URL temporarily
export DATABASE_URL="postgresql://user:pass@host/db"

# Run import command
python manage.py import_boundaries \
    --districts data/malawi_districts.geojson \
    --villages data/malawi_villages.geojson
```

**Pros**: Faster upload from your machine
**Cons**: Requires exposing database externally (security consideration)

## 📋 Option 3: Create Data Migration

Convert your data to a Django migration file (for smaller datasets).

### Create Migration Script

```bash
python manage.py makemigrations --empty locations --name add_districts_villages
```

Then edit the migration file to include your data. This works well for:

- Small datasets (< 100 records)
- Key locations only (major districts/cities)

**Example**: I can create a migration with the top 10 districts if you want.

## 📋 Option 4: Start Without Location Data

For initial deployment and testing:

1. Deploy without location data
2. Test crops API and suitability analysis
3. Import locations later when needed

**What works without location data:**

- ✅ Crops listing and details
- ✅ Crop suitability by lat/lon
- ✅ Weather data queries
- ✅ Soil data queries
- ✅ Planting calendar

**What requires location data:**

- ❌ Districts/Villages endpoints
- ❌ "Find nearby villages" feature
- ❌ Location-based filtering

## 🎯 Recommended Approach

**For Demo/Testing:**

1. Deploy without location data (Option 4)
2. Test crops and suitability features
3. Add 2-3 sample locations via Django admin

**For Production:**

1. Deploy application first
2. Upload data files to cloud storage
3. Import via Render shell (Option 1)
4. Or import from local machine (Option 2)

## 🔧 Troubleshooting

**Import takes too long:**

- Break into smaller chunks
- Import districts first, then villages
- Consider importing only major locations

**Out of memory:**

- Render free tier has limited RAM
- May need to upgrade or reduce dataset size

**File too large for GitHub:**

- Use Git LFS (Large File Storage)
- Or use cloud storage approach

## 📝 Sample Data Migration

Want to start with just a few key locations? I can create a migration with:

- 5-10 major districts (Lilongwe, Blantyre, Mzuzu, etc.)
- 20-30 key villages

This would be included in migrations and deploy automatically.

Let me know if you want me to create this!
