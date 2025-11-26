# Quick Deployment Guide

## TL;DR - Deploy in 3 Steps

### 1. Create Database on Render (2 minutes)

1. Go to https://dashboard.render.com → New + → PostgreSQL
2. Name: `mlimi-wanzeru-db`, Plan: Free
3. After creation, connect via psql and run: `CREATE EXTENSION postgis;`

### 2. Deploy Backend with Docker (5 minutes)

1. Push code to GitHub
2. Render → New + → Web Service
3. Connect your repo
4. **Important**: Select **Docker** as environment (not Python)
5. Add environment variables:
   - `DATABASE_URL`: (link to database)
   - `SECRET_KEY`: (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com`
6. Deploy

### 3. Deploy Frontend on Vercel (3 minutes)

1. Update `smart-farmer-frontend/.env.production` with your backend URL
2. Push to GitHub
3. Vercel → Import Project → Deploy
4. Add env var: `VITE_API_URL=https://your-backend.onrender.com/api`

### 4. Connect Them

1. Add frontend URL to backend `CORS_ALLOWED_ORIGINS` env var
2. Redeploy backend
3. Done! 🎉

## Why Docker?

The Docker approach installs GDAL automatically, which GeoDjango needs for spatial operations. The Python buildpack on Render doesn't support GDAL installation.

## Testing

```bash
# Test backend
curl https://your-backend.onrender.com/api/

# Test crops endpoint
curl https://your-backend.onrender.com/api/weather/crops/
```

## Troubleshooting

**Build fails**: Check Render logs, ensure Dockerfile is in repo root
**Database connection fails**: Verify DATABASE_URL is set correctly
**CORS errors**: Add frontend URL to CORS_ALLOWED_ORIGINS

## Files You Need

- ✅ `Dockerfile` - Docker configuration with GDAL
- ✅ `render.yaml` - Render configuration (uses Docker)
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.production` - Frontend API URL

All files are already created and ready to deploy!
