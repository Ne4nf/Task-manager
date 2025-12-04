# ✅ PRE-DEPLOYMENT CHECKLIST

## 📦 Files Created/Updated

### Configuration Files
- ✅ `.gitignore` (root và backend)
- ✅ `README.md` - Full documentation
- ✅ `DEPLOYMENT.md` - English deployment guide
- ✅ `DEPLOY_GUIDE_VI.md` - Vietnamese deployment guide
- ✅ `package.json` (root)
- ✅ `frontend/vercel.json` - Vercel config
- ✅ `frontend/.env.example` - Frontend env template
- ✅ `backend/render.yaml` - Render config
- ✅ `backend/.env.example` - Backend env template
- ✅ `backend/.gitignore` - Backend specific ignores

### Code Quality
- ✅ All TypeScript errors fixed
- ✅ Production build successful
- ✅ No unused imports
- ✅ All API endpoints tested

## 🔍 Final Verification

### Backend ✅
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8000
```
- ✅ Server starts without errors
- ✅ API docs accessible at http://localhost:8000/docs
- ✅ All endpoints working

### Frontend ✅
```bash
cd frontend
npm install
npm run build  # ✅ Build successful
npm run dev    # Test locally
```
- ✅ Build completes without errors
- ✅ No TypeScript errors
- ✅ All pages load correctly

### Environment Variables ✅

**Backend (.env)** - READY
```env
✅ SUPABASE_URL
✅ SUPABASE_KEY
✅ SUPABASE_SERVICE_KEY
✅ ANTHROPIC_API_KEY
✅ CLAUDE_MODEL
✅ DEBUG
✅ CORS_ORIGINS
```

**Frontend (.env.local)** - NEED TO CREATE
```env
VITE_API_URL=http://localhost:8000/api/v1  # Development
```

### Database ✅
- ✅ Migrations executed in Supabase
- ✅ All tables created
- ✅ Triggers working (auto-calculate progress)
- ✅ Test data available

## 📝 BEFORE PUSHING TO GIT

### 1. Create .env.local for frontend
```bash
cd frontend
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
```

### 2. Verify .gitignore
```bash
git status
# Should NOT see:
# - backend/.env
# - frontend/.env.local
# - __pycache__/
# - node_modules/
```

### 3. Initialize Git (if not done)
```bash
git init
git add .
git commit -m "Initial commit - Rockship v1.0.0"
```

### 4. Create GitHub Repository
```
Repository name: rockship (or your choice)
Visibility: Public or Private
```

### 5. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

## 🚀 DEPLOYMENT STEPS

### Step 1: Deploy Backend to Render

1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   ```
   Name: rockship-backend
   Region: Oregon
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```
5. Add environment variables (copy from your .env)
6. Click "Create Web Service"
7. Wait for deployment (3-5 minutes)
8. **Copy backend URL** (e.g., https://rockship-backend.onrender.com)

### Step 2: Deploy Frontend to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure:
   ```
   Framework: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```
4. Add environment variable:
   ```
   VITE_API_URL = https://your-backend-url.onrender.com/api/v1
   ```
5. Click "Deploy"
6. Wait for deployment (1-2 minutes)
7. **Copy frontend URL** (e.g., https://rockship.vercel.app)

### Step 3: Update CORS

1. Go back to Render dashboard
2. Open backend service → Environment
3. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=["https://your-frontend-url.vercel.app"]
   ```
4. Save (triggers automatic redeploy)

## ✅ POST-DEPLOYMENT TESTING

Visit your Vercel URL and test:

1. **Login**
   - Username: test
   - Password: 123
   - ✅ User created/logged in

2. **Create Project**
   - Click "New Project"
   - Fill form
   - ✅ Project created

3. **Upload Document**
   - Go to Documentation tab
   - Upload .md file
   - ✅ Document uploaded and displayed

4. **Generate Modules**
   - Click "Generate with AI" (purple button)
   - Enter prompt
   - ✅ Modules generated

5. **Generate Tasks**
   - Open a module
   - Click "Generate with AI"
   - ✅ Tasks generated

6. **Update Task Status**
   - Change status dropdown
   - ✅ Status updated, progress recalculated

7. **Delete Operations**
   - Test delete task, module, project
   - ✅ All deletions work with confirmations

## 📊 MONITORING

### Check Logs

**Backend (Render)**
```
Dashboard → Service → Logs
```
Watch for:
- ❌ Errors
- ✅ Successful API calls
- ⚠️ Slow queries

**Frontend (Vercel)**
```
Dashboard → Project → Deployments → Logs
```

**Database (Supabase)**
```
Dashboard → Database → Logs
```

### Monitor Usage

**Anthropic Console**
```
https://console.anthropic.com
```
- Check token usage
- Monitor costs

## 💰 COST TRACKING

### Free Tier Limits
- Vercel: 100GB bandwidth/month
- Render: 750 hours/month (sleeps after 15min)
- Supabase: 500MB database, 1GB storage
- Anthropic: Pay-as-you-go (~$5-10/month typical)

### When to Upgrade
- Render: $7/month for always-on
- Supabase: $25/month for more storage
- Total: ~$32-50/month for production

## 🎯 SUCCESS CRITERIA

- ✅ Backend deployed and accessible
- ✅ Frontend deployed and accessible
- ✅ CORS configured correctly
- ✅ All features working
- ✅ No console errors
- ✅ Login flow works
- ✅ AI generation works
- ✅ CRUD operations work

## 🆘 TROUBLESHOOTING

### "Failed to fetch" error
→ Check CORS_ORIGINS in Render includes Vercel URL

### "500 Internal Server Error"
→ Check Render logs, verify environment variables

### Build failed
→ Review build logs in Vercel/Render dashboard

### AI generation not working
→ Verify ANTHROPIC_API_KEY in Render environment

## 📚 RESOURCES

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Detailed English guide
- [DEPLOY_GUIDE_VI.md](./DEPLOY_GUIDE_VI.md) - Detailed Vietnamese guide
- [README.md](./README.md) - Project documentation
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)

---

## ✨ READY TO DEPLOY!

Everything is configured and tested. Follow the deployment steps above and you're good to go! 🚀

**Good luck!** 🎉
