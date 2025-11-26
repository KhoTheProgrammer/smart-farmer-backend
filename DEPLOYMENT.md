# Deployment Guide - Mlimi Wanzeru

Complete guide for deploying the Smart Farmer platform for free using Render (backend + database) and Vercel/Netlify (frontend).

## 🎯 Deployment Architecture

- **Frontend**: Vercel or Netlify (React + Vite)
- **Backend**: Render Web Service (Django + GeoDjango)
- **Database**: Render PostgreSQL with PostGIS extension

## 📋 Prerequisites

1. GitHub account (to connect repositories)
2. Render account (sign up at https://render.com)
3. Vercel account (sign up at https://vercel.com) OR Netlify account

## 🗄️ Part 1: Deploy Database (Render PostgreSQL)

### Step 1: Create PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `mlimi-wanzeru-db`
   - **Database**: `mlimi_wanzeru`
   - **User**: `mlimi_user` (or leave default)
   - **Region**: Choose closest to your users
   - **Plan**: **Free**
4. Click **"Create Database"**
5. Wait for database to be created (~2 minutes)

### Step 2: Enable PostGIS Extension

1. In your database dashboard, go to **"Connect"** tab
2. Copy the **"PSQL Command"**
3. Run it in your local terminal:
   ```bash
   psql postgresql://mlimi_user:password@host/mlimi_wanzeru
   ```
4. In the PostgreSQL shell, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   SELECT PostGIS_version();
   \q
   ```

### Step 3: Save Database Credentials

From the database dashboard, copy:

- **Internal Database URL** (for backend connection)
- Keep this for the next step

## 🚀 Part 2: Deploy Backend (Render Web Service)

### Step 1: Prepare Repository

Make sure these files exist in your backend repo:

- ✅ `runtime.txt` - Python version
- ✅ `build.sh` - Build script
- ✅ `render.yaml` - Render configuration
- ✅ `requirements.txt` - Updated with gunicorn, whitenoise

### Step 2: Update Django Settings for Production

The settings are already configured to use environment variables. Render will automatically set `DATABASE_URL`.

### Step 3: Push to GitHub

```bash
cd smart-farmer-backend
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### Step 4: Create Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `mlimi-wanzeru-api`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `smart-farmer-backend` if monorepo)
   - **Runtime**: **Python 3**
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn mlimi_wanzeru.wsgi:application`
   - **Plan**: **Free**

### Step 5: Set Environment Variables

In the **"Environment"** tab, add:

```
DATABASE_URL=<paste Internal Database URL from Step 1>
SECRET_KEY=<generate a random 50-character string>
DEBUG=False
ALLOWED_HOSTS=.onrender.com
NASA_POWER_API_URL=https://power.larc.nasa.gov/api/temporal/daily/point
```

To generate SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait for build to complete (~5-10 minutes)
3. Check logs for any errors
4. Once deployed, copy your backend URL: `https://mlimi-wanzeru-api.onrender.com`

## 🌐 Part 3: Deploy Frontend (Vercel)

### Step 1: Update API URL

Create `.env.production` in frontend:

```env
VITE_API_URL=https://mlimi-wanzeru-api.onrender.com/api
```

### Step 2: Update CORS Settings

Add your frontend URL to backend CORS settings. In Render dashboard, add environment variable:

```
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app,https://mlimi-wanzeru-api.onrender.com
```

### Step 3: Deploy on Vercel

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import your frontend repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `smart-farmer-frontend` (if monorepo) or leave empty
   - **Build Command**: `npm run build` or `pnpm build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - `VITE_API_URL` = `https://mlimi-wanzeru-api.onrender.com/api`
6. Click **"Deploy"**

## ✅ Verify Deployment

Test backend:

```bash
curl https://mlimi-wanzeru-api.onrender.com/api/
```

Visit your frontend URL and test the application.

## 🔧 Troubleshooting

**Cold starts**: Render free tier spins down after 15 minutes of inactivity. First request will be slow.

**CORS errors**: Update `CORS_ALLOWED_ORIGINS` in backend environment variables with your frontend URL.

**Database expires**: Free PostgreSQL expires after 90 days. Backup regularly.

## 📊 Free Tier Limitations

- **Render**: 750 hours/month, 15 min inactivity spin-down, 1GB database (90 days)
- **Vercel**: 100GB bandwidth/month, 6000 build minutes/month

---

**Built with ❤️ for Malawian farmers**
