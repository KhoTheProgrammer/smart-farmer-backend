# Deployment Checklist

Quick checklist for deploying Smart Farmer platform.

## ✅ Pre-Deployment

### Backend

- [ ] All code committed and pushed to GitHub
- [ ] `requirements.txt` includes gunicorn, whitenoise, dj-database-url
- [ ] `build.sh` is executable (`chmod +x build.sh`)
- [ ] `runtime.txt` specifies Python version
- [ ] `.env.example` is up to date
- [ ] Sensitive data not in Git (check `.gitignore`)

### Frontend

- [ ] All code committed and pushed to GitHub
- [ ] `.env.production` configured with backend URL
- [ ] `vercel.json` or `netlify.toml` exists
- [ ] Build command works locally (`npm run build`)

## 🗄️ Database Deployment (Render)

- [ ] Create PostgreSQL database on Render
- [ ] Enable PostGIS extension
- [ ] Save Internal Database URL

## 🚀 Backend Deployment (Render)

- [ ] Create Web Service on Render
- [ ] Connect GitHub repository
- [ ] Set build command: `./build.sh`
- [ ] Set start command: `gunicorn mlimi_wanzeru.wsgi:application`
- [ ] Add environment variables:
  - [ ] `DATABASE_URL`
  - [ ] `SECRET_KEY` (generate new one)
  - [ ] `DEBUG=False`
  - [ ] `ALLOWED_HOSTS=.onrender.com`
  - [ ] `NASA_POWER_API_URL`
- [ ] Deploy and wait for build
- [ ] Check logs for errors
- [ ] Test API endpoints
- [ ] Save backend URL

## 🌐 Frontend Deployment (Vercel/Netlify)

- [ ] Update `.env.production` with backend URL
- [ ] Push to GitHub
- [ ] Create project on Vercel/Netlify
- [ ] Set build command: `npm run build` or `pnpm build`
- [ ] Set output directory: `dist`
- [ ] Add environment variable: `VITE_API_URL`
- [ ] Deploy
- [ ] Save frontend URL

## 🔧 Post-Deployment

- [ ] Update backend CORS with frontend URL
- [ ] Redeploy backend
- [ ] Test frontend → backend connection
- [ ] Test all pages and features
- [ ] Check browser console for errors
- [ ] Test on mobile device

## 📊 Optional

- [ ] Add custom domain (Vercel/Netlify)
- [ ] Set up monitoring/analytics
- [ ] Configure error tracking (Sentry)
- [ ] Set calendar reminder for database backup (80 days)

## 🎉 Done!

Your application is live:

- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.onrender.com/api`
- API Docs: `https://your-backend.onrender.com/api/docs/`

---

**Remember**: Render free tier spins down after 15 minutes of inactivity. First request will be slow (30 seconds).
