# 🚀 Deployment Checklist & Instructions

## ✅ Pre-Deployment Checklist

### Backend (Render)
- [x] `render.yaml` configured
- [x] Environment variables documented in `.env.example`
- [x] Python dependencies in `requirements.txt`
- [x] `runtime.txt` specifies Python version
- [x] FastAPI app configured for production
- [x] CORS configured for frontend domain
- [x] Database (Supabase) connected
- [x] Claude API configured

### Frontend (Vercel)
- [x] `vercel.json` configured
- [x] Build command set to `npm run build`
- [x] Output directory set to `dist`
- [x] SPA routing configured
- [x] Environment variable documented
- [x] API URL configurable via `VITE_API_URL`

### Features Completed
- [x] User authentication
- [x] Project management
- [x] Module generation (AI + Memory-based)
- [x] Task management
- [x] Document upload & Git analysis
- [x] **NEW:** Reused badge with source module link
- [x] Tag-based semantic search
- [x] Auto-tagging system

---

## 🎯 Deployment Steps

### 1️⃣ Deploy Backend to Render

**Option A: Automatic (Recommended)**
1. Push code to GitHub:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will auto-detect `render.yaml` and configure everything

**Option B: Manual**
1. Create new Web Service on Render
2. Configure:
   - Name: `rockship-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - Branch: `main`

3. Add Environment Variables:
   ```
   SUPABASE_URL=<your_supabase_url>
   SUPABASE_KEY=<your_supabase_anon_key>
   SUPABASE_SERVICE_KEY=<your_service_key>
   ANTHROPIC_API_KEY=<your_claude_api_key>
   CLAUDE_MODEL=claude-3-5-sonnet-20241022
   DEBUG=False
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   ```

4. Click "Create Web Service"
5. Wait for deployment (5-10 minutes)
6. Copy your backend URL: `https://rockship-backend.onrender.com`

---

### 2️⃣ Deploy Frontend to Vercel

**Option A: Vercel CLI (Fast)**
```bash
cd frontend
npm install -g vercel  # If not installed
vercel login
vercel  # Follow prompts
```

**Option B: Vercel Dashboard**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Vercel auto-detects Vite config
5. Add Environment Variable:
   ```
   VITE_API_URL=https://rockship-backend.onrender.com/api/v1
   ```
6. Click "Deploy"
7. Wait 2-3 minutes
8. Your app is live at `https://your-app.vercel.app`

---

### 3️⃣ Post-Deployment Configuration

**Update Backend CORS:**
1. Go to Render Dashboard → Your service → Environment
2. Update `CORS_ORIGINS`:
   ```
   ["https://your-app.vercel.app","https://your-app-*.vercel.app"]
   ```
3. Save and redeploy

**Test Deployment:**
1. Visit your Vercel URL
2. Try login/register
3. Create a project
4. Generate modules with AI
5. Test "Gen AI with Memories" feature
6. Check reused badge shows correctly
7. Click "View Source" button on reused modules

---

## 🔧 Environment Variables Reference

### Backend (Render)
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SUPABASE_URL` | ✅ | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | ✅ | Supabase anon key | `eyJhb...` |
| `SUPABASE_SERVICE_KEY` | ✅ | Service role key | `eyJhb...` |
| `ANTHROPIC_API_KEY` | ✅ | Claude API key | `sk-ant-...` |
| `CLAUDE_MODEL` | ✅ | Model version | `claude-3-5-sonnet-20241022` |
| `DEBUG` | ⚠️ | Debug mode | `False` (production) |
| `CORS_ORIGINS` | ✅ | Allowed origins | `["https://your-app.vercel.app"]` |

### Frontend (Vercel)
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | ✅ | Backend API URL | `https://your-backend.onrender.com/api/v1` |

---

## 🐛 Troubleshooting

### Backend Issues

**Problem: "Module not found" error**
```bash
# Solution: Check requirements.txt includes all dependencies
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

**Problem: "Connection refused" to Supabase**
- Check `SUPABASE_URL` is correct
- Verify `SUPABASE_SERVICE_KEY` has proper permissions
- Check Supabase project is active

**Problem: CORS errors**
- Update `CORS_ORIGINS` to include your Vercel domain
- Include wildcard for preview deployments: `https://*.vercel.app`

### Frontend Issues

**Problem: API calls failing**
- Check `VITE_API_URL` points to correct backend
- Verify backend is deployed and healthy
- Check browser console for CORS errors

**Problem: "Reused" badge not showing**
- Module must have `reused_from_module_id` field
- Backend needs to save this field when generating modules
- Check network tab: Does API response include `reused_from_module_id`?

**Problem: Build fails**
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📊 Monitoring

### Backend Health Check
```bash
curl https://your-backend.onrender.com/health
# Expected: {"status": "healthy"}
```

### Test Endpoints
```bash
# Login
curl -X POST https://your-backend.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# List projects
curl https://your-backend.onrender.com/api/v1/projects/ \
  -H "X-User-ID: your-user-id"
```

### Logs
- **Render:** Dashboard → Your Service → Logs
- **Vercel:** Dashboard → Your Project → Deployments → View Logs

---

## 🎉 Success Criteria

- ✅ Backend responds to health check
- ✅ Frontend loads without errors
- ✅ User can login/register
- ✅ Projects can be created
- ✅ Modules can be generated with AI
- ✅ "Gen AI with Memories" workflow works
- ✅ Reused badge shows with correct strategy
- ✅ "View Source" button navigates to source module
- ✅ No console errors in browser
- ✅ API response times < 2 seconds

---

## 📝 Post-Deployment TODO

1. **Custom Domain (Optional)**
   - Vercel: Settings → Domains → Add
   - Render: Settings → Custom Domain

2. **Analytics Setup**
   - Add Google Analytics to frontend
   - Set up error tracking (Sentry)

3. **Performance Monitoring**
   - Monitor API response times
   - Track Claude API usage/costs

4. **Database Backup**
   - Set up Supabase backup schedule
   - Export important data regularly

---

## 🆘 Support

- Backend Issues: Check `backend/README.md`
- Frontend Issues: Check `frontend/README.md`
- GenAI Features: Check `backend/GENAI_MEMORIES_SIMPLE.md`

**Need Help?**
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs
