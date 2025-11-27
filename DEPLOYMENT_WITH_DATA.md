# Complete Deployment with Full Data - Checklist

Follow this checklist to deploy your application with full location data.

## Phase 1: Deploy Infrastructure (20 minutes)

### ☐ 1. Deploy Database

- [ ] Go to https://dashboard.render.com
- [ ] Create PostgreSQL database (free tier)
- [ ] Name: `mlimi-wanzeru-db`
- [ ] Wait for creation (~2 minutes)
- [ ] Connect via psql and run: `CREATE EXTENSION postgis;`
- [ ] Copy **External Database URL** (save for later)

### ☐ 2. Deploy Backend

- [ ] Push code to GitHub
- [ ] Create Web Service on Render
- [ ] Select **Docker** environment (important!)
- [ ] Set environment variables:
  - [ ] `DATABASE_URL` (link to database)
  - [ ] `SECRET_KEY` (generate new)
  - [ ] `DEBUG=False`
  - [ ] `ALLOWED_HOSTS=.onrender.com`
- [ ] Deploy and wait (~10 minutes)
- [ ] Copy backend URL

### ☐ 3. Verify Basic Deployment

- [ ] Test: `curl https://your-backend.onrender.com/api/`
- [ ] Test crops: `curl https://your-backend.onrender.com/api/weather/crops/`
- [ ] Should see 6 crops and 5 sample districts

## Phase 2: Import Full Data (15 minutes)

### ☐ 4. Prepare Local Environment

- [ ] Open terminal in `smart-farmer-backend` directory
- [ ] Activate virtual environment: `source venv/bin/activate`
- [ ] Verify data files exist:
  - [ ] `data/malawi_districts.geojson` (~9-20 MB)
  - [ ] `data/malawi_villages.geojson` (~48 MB)

### ☐ 5. Set Production Database URL

```bash
export PRODUCTION_DATABASE_URL='postgresql://user:pass@host/db'
```

(Use the External URL from Step 1)

### ☐ 6. Run Import Script

```bash
python import_to_production.py
```

- [ ] Review the confirmation prompt
- [ ] Type `yes` to confirm
- [ ] Wait for import to complete (~10 minutes)

### ☐ 7. Verify Full Data Import

```bash
# Test districts (should return 28)
curl https://your-backend.onrender.com/api/locations/districts/ | jq '.count'

# Test villages (should return 400+)
curl https://your-backend.onrender.com/api/locations/villages/ | jq '.count'
```

## Phase 3: Deploy Frontend (10 minutes)

### ☐ 8. Configure Frontend

- [ ] Update `smart-farmer-frontend/.env.production`:
  ```
  VITE_API_URL=https://your-backend.onrender.com/api
  ```
- [ ] Commit and push to GitHub

### ☐ 9. Deploy on Vercel

- [ ] Go to https://vercel.com/dashboard
- [ ] Import project from GitHub
- [ ] Set environment variable: `VITE_API_URL`
- [ ] Deploy
- [ ] Copy frontend URL

### ☐ 10. Connect Frontend and Backend

- [ ] Go to Render → Backend service → Environment
- [ ] Update `CORS_ALLOWED_ORIGINS`:
  ```
  https://your-frontend.vercel.app,http://localhost:5173
  ```
- [ ] Save and redeploy backend

## Phase 4: Final Testing (5 minutes)

### ☐ 11. Test All Endpoints

- [ ] Crops: `GET /api/weather/crops/`
- [ ] Districts: `GET /api/locations/districts/`
- [ ] Villages: `GET /api/locations/villages/`
- [ ] Crop suitability: `GET /api/weather/crops/1/suitability/?lat=-13.98&lon=33.78`
- [ ] Nearby villages: `GET /api/locations/villages/nearby/?lat=-13.98&lon=33.78&radius=50`

### ☐ 12. Test Frontend

- [ ] Visit your Vercel URL
- [ ] Check all pages load
- [ ] Test API calls (check browser console)
- [ ] Verify data displays correctly

### ☐ 13. Create Superuser (Optional)

In Render Shell:

```bash
python manage.py createsuperuser
```

Access admin at: `https://your-backend.onrender.com/admin/`

## ✅ Deployment Complete!

Your application is now live with:

- ✅ 6 crops with full requirements
- ✅ 28 districts with boundaries
- ✅ 400+ villages with locations and elevation
- ✅ All API endpoints functional
- ✅ Frontend connected to backend

## 📝 Save These URLs

Update `DEPLOYMENT_URLS.md` with:

- Frontend: `https://________________.vercel.app`
- Backend: `https://________________.onrender.com`
- API Docs: `https://________________.onrender.com/api/docs/`
- Admin: `https://________________.onrender.com/admin/`

## ⚠️ Important Reminders

- **Database expires in 90 days** - Set calendar reminder to backup!
- **Backend spins down after 15 min** - First request will be slow
- **Free tier limits**: 750 hours/month, 100GB bandwidth

## 🔄 Future Updates

To update your deployment:

```bash
# Backend
git push origin main  # Auto-deploys on Render

# Frontend
git push origin main  # Auto-deploys on Vercel
```

## 📚 Documentation

- `DEPLOYMENT_QUICK.md` - Quick reference
- `IMPORT_FULL_DATA_GUIDE.md` - Detailed import guide
- `DATA_STRATEGY.md` - Data overview
- `import_production_data.md` - Alternative import methods

---

**Total Time**: ~50 minutes
**Result**: Fully deployed application with complete dataset! 🎉
