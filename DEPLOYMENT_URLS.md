# Deployment URLs Reference

Quick reference for your deployed application URLs.

## 🔗 Production URLs

### Frontend

- **URL**: `https://your-app-name.vercel.app` (or `.netlify.app`)
- **Platform**: Vercel / Netlify
- **Dashboard**: https://vercel.com/dashboard or https://app.netlify.com

### Backend API

- **URL**: `https://mlimi-wanzeru-api.onrender.com`
- **API Root**: `https://mlimi-wanzeru-api.onrender.com/api/`
- **API Docs**: `https://mlimi-wanzeru-api.onrender.com/api/docs/`
- **Admin Panel**: `https://mlimi-wanzeru-api.onrender.com/admin/`
- **Platform**: Render
- **Dashboard**: https://dashboard.render.com

### Database

- **Name**: `mlimi-wanzeru-db`
- **Type**: PostgreSQL 15 with PostGIS
- **Platform**: Render
- **Dashboard**: https://dashboard.render.com

## 📝 Update After Deployment

After deploying, update this file with your actual URLs:

```markdown
## Your Deployed URLs

- Frontend: https://_____________________.vercel.app
- Backend: https://_____________________.onrender.com
- API Docs: https://_____________________.onrender.com/api/docs/
```

## 🔑 Important Links

- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Netlify Dashboard**: https://app.netlify.com
- **GitHub Repository**: https://github.com/your-username/your-repo

## ⚠️ Free Tier Reminders

- **Backend**: Spins down after 15 min inactivity (30s cold start)
- **Database**: Expires after 90 days - set backup reminder!
- **Bandwidth**: 100GB/month on Vercel/Netlify

## 🔄 Redeploy

To redeploy after changes:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Both platforms auto-deploy on push to main branch.
