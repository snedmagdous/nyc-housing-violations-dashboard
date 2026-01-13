# Deployment Guide: NYC Housing Violations Dashboard

This guide will help you deploy your full-stack app so it's accessible from anywhere and shareable with nonprofits.

## Architecture Overview

- **Frontend**: React/Vite app → Deploy to **Netlify** (free)
- **Backend**: FastAPI + PostgreSQL → Deploy to **Render** (free)
- **Database**: PostgreSQL → Hosted on Render (free tier)

Your NYC Open Data token stays secure on the backend and is never exposed to users.

---

## Part 1: Deploy Backend to Render (FREE)

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your GitHub repos

### Step 2: Create PostgreSQL Database
1. Click **"New +"** → **"PostgreSQL"**
2. Settings:
   - **Name**: `nyc-violations-db`
   - **Database**: `nyc_housing_violations`
   - **User**: `postgres`
   - **Region**: Choose closest to you
   - **Plan**: **Free**
3. Click **"Create Database"**
4. Wait 2-3 minutes for database to be ready
5. **Copy the "Internal Database URL"** - you'll need this

### Step 3: Upload Your Data to Render Database
You need to migrate your local PostgreSQL data to Render:

```bash
# 1. Export your local database
pg_dump -h localhost -U postgres -d nyc_housing_violations -F c -b -v -f nyc_violations_backup.dump

# 2. Restore to Render (replace with your Render database URL)
pg_restore -h <render-host> -U <render-user> -d nyc_housing_violations -v nyc_violations_backup.dump
```

**Alternative**: If pg_dump doesn't work, you can:
- Run your data pipeline scripts on a cloud VM, OR
- Use Render's PostgreSQL external connection to restore data

### Step 4: Deploy FastAPI Backend
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `nyc-housing-violations`
3. Settings:
   - **Name**: `nyc-violations-api`
   - **Region**: Same as your database
   - **Branch**: `main`
   - **Root Directory**: leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**

4. **Environment Variables** (click "Advanced" → "Add Environment Variable"):
   ```
   DATABASE_URL = (paste the Internal Database URL from Step 2)
   NYC_OPEN_DATA_TOKEN = a9pfihsihtdmkgmyzmabsrp9a
   ENVIRONMENT = production
   PYTHON_VERSION = 3.11
   ```

5. Click **"Create Web Service"**
6. Wait 5-10 minutes for deployment
7. Once live, **copy your API URL**: `https://nyc-violations-api.onrender.com`

### Step 5: Test Your Backend
Visit: `https://your-backend-url.onrender.com/docs`

You should see the FastAPI Swagger documentation! Try a test query.

---

## Part 2: Deploy Frontend to Netlify (FREE)

### Step 1: Create Netlify Account
1. Go to [netlify.com](https://netlify.com)
2. Sign up with GitHub
3. Authorize Netlify to access your repos

### Step 2: Deploy Your Site
1. Click **"Add new site"** → **"Import an existing project"**
2. Choose **GitHub** → Select `nyc-housing-violations` repo
3. Settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
4. Click **"Show advanced"** → **"Add environment variable"**:
   ```
   VITE_API_URL = https://your-backend-url.onrender.com
   ```
   (Use the URL from Part 1, Step 4)

5. Click **"Deploy site"**
6. Wait 2-3 minutes for build
7. Your site is live! Copy the URL: `https://random-name-123.netlify.app`

### Step 3: Customize Your Domain (Optional)
1. In Netlify, go to **Site settings** → **Domain management**
2. Click **"Options"** → **"Edit site name"**
3. Change to something memorable: `nyc-housing-violations.netlify.app`

---

## Part 3: Update CORS Settings

Since your frontend URL is now live, update backend CORS for better security:

### Update `src/api/main.py`:
```python
# Replace this line:
allow_origins=["*"],

# With your actual frontend URL:
allow_origins=[
    "https://nyc-housing-violations.netlify.app",  # Your Netlify URL
    "http://localhost:5173",  # For local development
],
```

Commit and push - Render will auto-deploy the update.

---

## Part 4: Share with Nonprofits

Your app is now live and accessible from any device! Share these URLs:

- **Dashboard**: `https://nyc-housing-violations.netlify.app`
- **API Docs**: `https://nyc-violations-api.onrender.com/docs`

### Important Notes:

✅ **Free tier limitations**:
- Render Free: Backend sleeps after 15 min inactivity (15-30s cold start on first request)
- Database: 90 days free, then $7/month (or migrate to a paid tier)
- Netlify Free: 100GB bandwidth/month (plenty for nonprofits)

✅ **Your NYC token is secure**: It's stored on the backend and never exposed to users

✅ **Auto-deployments**: Both Netlify and Render auto-deploy when you push to GitHub

---

## Troubleshooting

### Frontend can't connect to backend
- Check `VITE_API_URL` in Netlify environment variables
- Ensure it starts with `https://` and has no trailing slash
- Check browser console for CORS errors

### Backend shows "Application failed to respond"
- Check Render logs: Dashboard → your service → "Logs"
- Verify `DATABASE_URL` is correct
- Ensure `requirements.txt` includes all dependencies

### Database connection error
- Verify database is "Available" in Render dashboard
- Check `DATABASE_URL` environment variable format
- Ensure database has been restored with your data

### Data is missing
- You need to migrate your local PostgreSQL data to Render
- Use `pg_dump` and `pg_restore` commands from Step 3

---

## Cost Summary

- **Netlify**: Free forever (100GB/month bandwidth)
- **Render Database**: Free for 90 days, then $7/month
- **Render Web Service**: Free (with cold starts)

**Total cost**: $0/month for first 90 days, then ~$7/month for database

---

## Next Steps

Once deployed, you can:
1. Get a custom domain from Namecheap (~$10/year)
2. Upgrade Render to paid tier ($7/month) to remove cold starts
3. Add Google Analytics to track nonprofit usage
4. Set up monitoring with Sentry (free tier)

Need help? Check the logs in Render and Netlify dashboards!
