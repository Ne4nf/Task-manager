# Deployment Checklist

## Pre-Deployment

### Backend Preparation
- [x] Create `.env` file with production values
- [x] Set `DEBUG=False` for production
- [x] Add production frontend URL to `CORS_ORIGINS`
- [x] Verify all environment variables in `.env.example`
- [x] Test all API endpoints locally
- [x] Create `render.yaml` for Render deployment

### Frontend Preparation
- [x] Create `.env.local` with production API URL
- [x] Test build locally: `npm run build`
- [x] Verify all API calls use `VITE_API_URL`
- [x] Create `vercel.json` for Vercel deployment

### Database
- [x] Run migrations in Supabase
- [x] Verify all tables created
- [x] Test database triggers for auto-calculation
- [ ] Backup database before deployment

### Security
- [ ] Never commit `.env` files
- [ ] Use environment variables for all secrets
- [ ] Verify `.gitignore` includes `.env`
- [x] Use service keys only on backend

## Deployment Steps

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Rockship v1.0.0"
git branch -M main
git remote add origin https://github.com/yourusername/rockship.git
git push -u origin main
```

### 2. Deploy Backend to Render

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: rockship-backend
   - **Region**: Choose closest to you
   - **Branch**: main
   - **Root Directory**: backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. Add Environment Variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_anon_key
   SUPABASE_SERVICE_KEY=your_service_key
   ANTHROPIC_API_KEY=your_anthropic_key
   CLAUDE_MODEL=claude-3-5-sonnet-20241022
   DEBUG=False
   API_V1_PREFIX=/api/v1
   MAX_FILE_SIZE=10485760
   ```

6. **IMPORTANT**: After first deploy, get your backend URL (e.g., `https://rockship-backend.onrender.com`)

7. Update `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=["https://your-frontend-url.vercel.app"]
   ```
   (Update this after deploying frontend)

8. Click "Create Web Service"

### 3. Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variables:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-backend-url.onrender.com/api/v1`
   (Use the URL from Render deployment)

6. Click "Deploy"

7. After deployment, get your frontend URL (e.g., `https://rockship.vercel.app`)

### 4. Update CORS in Backend

1. Go back to Render dashboard
2. Open your backend service
3. Go to "Environment" tab
4. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=["https://rockship.vercel.app","https://your-custom-domain.com"]
   ```
5. Save changes (this will trigger auto-redeploy)

### 5. Test Production

1. Visit your Vercel URL
2. Test login (username + password: 123)
3. Test creating project
4. Test uploading document
5. Test generating modules with AI
6. Test generating tasks with AI
7. Test updating task status
8. Test deleting items

## Post-Deployment

### Monitoring
- [ ] Check Render logs for errors
- [ ] Check Vercel deployment logs
- [ ] Monitor Supabase usage
- [ ] Monitor Anthropic API usage

### Custom Domain (Optional)

#### Frontend (Vercel)
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed
4. Wait for SSL certificate

#### Backend (Render)
1. Go to Service Settings → Custom Domains
2. Add your custom domain
3. Configure DNS records
4. Wait for SSL certificate

### Performance Optimization
- [ ] Enable Vercel Edge Network
- [ ] Configure Render auto-scaling
- [ ] Set up CDN for static assets
- [ ] Enable response compression

### Maintenance
- [ ] Set up error monitoring (Sentry)
- [ ] Configure backup schedule for database
- [ ] Document API changes
- [ ] Plan feature updates

## Troubleshooting

### Backend Issues

**500 Internal Server Error**
- Check Render logs
- Verify environment variables
- Check Supabase connection
- Verify ANTHROPIC_API_KEY

**CORS Errors**
- Update CORS_ORIGINS in Render
- Include https:// in URLs
- Check for trailing slashes

**Database Connection Failed**
- Verify SUPABASE_URL and keys
- Check Supabase project status
- Test connection from Render logs

### Frontend Issues

**API Connection Failed**
- Verify VITE_API_URL in Vercel
- Check backend is running
- Test API endpoint directly
- Check CORS settings

**Build Failed**
- Check Node.js version (18+)
- Verify all dependencies in package.json
- Test build locally first
- Check build logs in Vercel

**White Screen**
- Check browser console for errors
- Verify all routes configured
- Test with browser cache cleared
- Check vercel.json rewrites

## Environment Variables Reference

### Backend (.env)
```env
APP_NAME=Rockship Backend
APP_VERSION=1.0.0
DEBUG=False
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["https://your-app.vercel.app"]
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...
SUPABASE_SERVICE_KEY=eyJxxx...
ANTHROPIC_API_KEY=sk-ant-xxx...
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_FILE_SIZE=10485760
```

### Frontend (.env.local)
```env
VITE_API_URL=https://your-backend.onrender.com/api/v1
```

## Cost Estimation

### Free Tier Limits

**Vercel (Frontend)**
- Bandwidth: 100GB/month
- Build time: 6000 minutes/year
- Deployments: Unlimited
- **Cost**: Free

**Render (Backend)**
- Hours: 750/month (sleeps after 15 min inactivity)
- Memory: 512MB
- **Cost**: Free
- **Note**: Paid plan ($7/month) for always-on

**Supabase (Database)**
- Database: 500MB
- Storage: 1GB
- Bandwidth: 2GB
- **Cost**: Free
- **Note**: Paid plan starts at $25/month

**Anthropic (AI)**
- Claude API usage charged per token
- Estimate: $0.003 per 1K input tokens, $0.015 per 1K output tokens
- **Cost**: Pay-as-you-go

### Estimated Monthly Cost
- Free tier: $0 (with usage limits)
- Basic production: ~$32/month ($7 Render + $25 Supabase + usage-based AI)

## Support

If you encounter issues:
1. Check Render logs
2. Check Vercel deployment logs
3. Check browser console
4. Verify all environment variables
5. Test API endpoints with curl/Postman
6. Review this checklist again

Good luck with deployment! 🚀
