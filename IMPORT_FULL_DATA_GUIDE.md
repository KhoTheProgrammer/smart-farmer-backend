# Import Full Dataset to Production - Step by Step Guide

This guide walks you through importing all 28 districts and 400+ villages to your production database on Render.

## 📋 Prerequisites

- ✅ Backend deployed on Render
- ✅ Database created on Render with PostGIS enabled
- ✅ Data files exist locally in `data/` folder
- ✅ Python virtual environment activated

## 🎯 Overview

You'll connect from your local machine directly to the production database and import the data. This is faster than uploading files to Render.

## 📝 Step-by-Step Instructions

### Step 1: Get Production Database URL

1. Go to https://dashboard.render.com
2. Click on your database: **mlimi-wanzeru-db**
3. Go to the **"Connect"** tab
4. Copy the **"External Database URL"**

It will look like:

```
postgresql://mlimi_user:LONG_PASSWORD_HERE@dpg-xxxxx.oregon-postgres.render.com/mlimi_wanzeru
```

⚠️ **Important**: Use the **External** URL, not the Internal one!

### Step 2: Set Environment Variable

In your terminal (in the `smart-farmer-backend` directory):

**Linux/macOS:**

```bash
export PRODUCTION_DATABASE_URL='postgresql://mlimi_user:PASSWORD@host/mlimi_wanzeru'
```

**Windows (PowerShell):**

```powershell
$env:PRODUCTION_DATABASE_URL='postgresql://mlimi_user:PASSWORD@host/mlimi_wanzeru'
```

**Windows (CMD):**

```cmd
set PRODUCTION_DATABASE_URL=postgresql://mlimi_user:PASSWORD@host/mlimi_wanzeru
```

Replace with your actual database URL from Step 1.

### Step 3: Activate Virtual Environment

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 4: Verify Data Files

Check that your data files exist:

```bash
ls -lh data/malawi_districts.geojson
ls -lh data/malawi_villages.geojson
```

You should see:

- `malawi_districts.geojson` (~9-20 MB)
- `malawi_villages.geojson` (~48 MB)

### Step 5: Run Import Script

**Option A: Using Python script (Recommended)**

```bash
python import_to_production.py
```

**Option B: Using bash script**

```bash
./import_to_production.sh
```

### Step 6: Confirm Import

The script will show you:

- Current database contents
- Files to be imported
- Database connection info

Type `yes` to confirm and start the import.

### Step 7: Wait for Import

The import will take 5-15 minutes depending on your internet speed:

```
1/2 Importing districts...
Processing: malawi_districts.geojson
✓ Imported 28 districts

2/2 Importing villages...
Processing: malawi_villages.geojson
✓ Imported 400+ villages

✅ Import Complete!
```

### Step 8: Verify Import

Test your production API:

```bash
# Get your backend URL from Render
BACKEND_URL="https://your-app.onrender.com"

# Test districts endpoint
curl $BACKEND_URL/api/locations/districts/ | jq '.count'
# Should return: 28

# Test villages endpoint
curl $BACKEND_URL/api/locations/villages/ | jq '.count'
# Should return: 400+

# Test a specific district
curl $BACKEND_URL/api/locations/districts/ | jq '.results[0]'
```

## 🔧 Troubleshooting

### Connection Timeout

**Problem**: Import times out or connection drops

**Solution**:

- Check your internet connection
- Try importing districts and villages separately:
  ```bash
  python manage.py import_boundaries --districts data/malawi_districts.geojson
  python manage.py import_boundaries --villages data/malawi_villages.geojson
  ```

### "Database connection failed"

**Problem**: Cannot connect to production database

**Solutions**:

1. Verify DATABASE_URL is correct (check for typos)
2. Ensure you're using the **External** URL, not Internal
3. Check if your IP is allowed (Render allows all IPs by default)
4. Verify database is running in Render dashboard

### "Permission denied"

**Problem**: Cannot write to database

**Solution**:

- Verify you're using the correct database user credentials
- Check that the database user has write permissions

### "Duplicate key error"

**Problem**: Data already exists in database

**Solution**:

- The sample locations migration may have already run
- You can either:
  - Delete existing locations via Django admin
  - Or skip this import (sample data is already there)

### Import is Very Slow

**Problem**: Import taking longer than 20 minutes

**Solutions**:

1. Check your internet upload speed
2. Try importing from a location with better internet
3. Consider using Render Shell instead (Option 1 in import_production_data.md)

## 📊 What Gets Imported

### Districts (28 total)

- All administrative districts in Malawi
- Includes boundaries (MultiPolygon geometry)
- Includes centroids for quick lookups
- Names in English and Chichewa

### Villages (400+ total)

- Villages across all districts
- Point locations (lat/lon)
- Elevation data
- District associations

## 🔐 Security Notes

- The External Database URL contains your password
- Don't commit it to Git
- Don't share it publicly
- Unset the environment variable after import:
  ```bash
  unset PRODUCTION_DATABASE_URL  # Linux/macOS
  $env:PRODUCTION_DATABASE_URL = $null  # PowerShell
  ```

## ✅ After Import

Once import is complete:

1. **Test your API endpoints** - Verify all location data is accessible
2. **Update frontend** - Your app can now use real location data
3. **Remove sample migration** (optional) - If you don't want duplicate data:
   ```bash
   # In your repo, you can remove or comment out:
   # weather/migrations/0005_add_sample_locations.py
   ```

## 🎉 Success!

Your production database now has:

- ✅ 6 crops with requirements
- ✅ 28 districts with boundaries
- ✅ 400+ villages with locations
- ✅ Full location-based features enabled

All API endpoints are now fully functional with real Malawi data!

## 📞 Need Help?

If you encounter issues:

1. Check the error message carefully
2. Verify all prerequisites are met
3. Try the troubleshooting steps above
4. Check Render logs for database issues

---

**Estimated Time**: 15-20 minutes total
**Data Size**: ~60 MB upload
**Database Impact**: ~100-150 MB storage
