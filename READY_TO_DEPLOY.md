# ✅ Pre-Deployment Checklist - READY TO DEPLOY

## 📦 Code Status
- ✅ All changes committed
- ✅ Pushed to GitHub (commit: 303a885)
- ✅ No TypeScript/Python errors
- ✅ Frontend build tested
- ✅ Backend dependencies updated

---

## 🎯 What's New in This Release

### 🧠 GenAI with Memories
- [x] 3-layer semantic search (L1: Intent, L2: Tech, L3: Domain)
- [x] Smart reuse (Direct 90%+ / Partial 65-90% / New <65%)
- [x] Auto-tagging system (self-learning)
- [x] Reuse history tracking

### 🎨 UI Improvements
- [x] **Reused badge** shows on module cards (Blue badge)
- [x] **View Source button** links to original module
- [x] Strategy indicator (Direct/Partial/Logic Ref)
- [x] Git Analyzer component

### 🔧 Backend
- [x] 3 generation endpoints
- [x] Tag extraction with reasoning
- [x] Claude-based semantic similarity
- [x] Fix database constraints
- [x] Better error handling

### 📊 Database
- [x] Migration 002: module_tags, reuse_history tables
- [x] Migration 003: Single tag per layer
- [x] All migrations ready to run

---

## 🚀 Deployment Steps

### 1️⃣ Backend (Render) - AUTO DEPLOY

**Render will auto-detect `render.yaml` and deploy!**

1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub repo: `Ne4nf/Task-manager`
4. Render detects `render.yaml` automatically
5. Add Environment Variables:

```
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_anon_key>
SUPABASE_SERVICE_KEY=<your_service_key>
ANTHROPIC_API_KEY=<your_claude_key>
CLAUDE_MODEL=claude-3-5-sonnet-20241022
DEBUG=False
CORS_ORIGINS=["https://*.vercel.app"]
```

6. Click "Create Web Service"
7. Wait 5-10 minutes
8. **Copy your backend URL:** `https://rockship-backend.onrender.com`

---

### 2️⃣ Database (Supabase) - RUN MIGRATIONS

**IMPORTANT: Run migrations in SQL Editor**

1. Go to Supabase Dashboard → SQL Editor
2. Run migrations **IN ORDER:**

**Migration 1: Initial Schema** (if not done)
```sql
-- Copy content from: database/migrations/001_initial_schema.sql
-- Paste and Execute
```

**Migration 2: Memory System** (NEW)
```sql
-- Copy content from: database/migrations/002_module_memory_system.sql
-- Creates: module_tags, scoring_weights_config, reuse_history tables
-- Paste and Execute
```

**Migration 3: Single Tag Per Layer** (NEW)
```sql
-- Copy content from: database/migrations/003_single_tag_per_layer.sql
-- Updates: module_tags structure
-- Paste and Execute
```

3. Verify tables exist:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Should see:
-- modules, projects, tasks, users, module_tags, 
-- scoring_weights_config, reuse_history
```

---

### 3️⃣ Frontend (Vercel) - ONE COMMAND

**Option A: Vercel CLI (Fastest)**
```bash
cd frontend
npm install -g vercel
vercel login
vercel
```

Follow prompts:
- Project name: `rockship` (or your choice)
- Add environment variable:
  - Name: `VITE_API_URL`
  - Value: `https://rockship-backend.onrender.com/api/v1`

**Option B: Vercel Dashboard**
1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import `Ne4nf/Task-manager`
4. Root Directory: `frontend`
5. Framework: Vite (auto-detected)
6. Add Environment Variable:
   ```
   VITE_API_URL=https://rockship-backend.onrender.com/api/v1
   ```
7. Click "Deploy"

---

### 4️⃣ Post-Deployment Tests

**Test Backend:**
```bash
curl https://rockship-backend.onrender.com/health
# Expected: {"status":"healthy"}
```

**Test Frontend:**
1. Visit your Vercel URL
2. Create account / Login
3. Create new project
4. Click "Gen AI with Memories"
5. Upload requirements or use test data
6. Check modules generated
7. **Verify reused badge shows** (if similar modules exist)
8. **Click "View Source"** button → Should navigate to source module

**Test Reuse System:**
1. Generate modules for Project A (e.g., inventory system)
2. Generate modules for Project B (similar requirements)
3. Check that Project B modules show:
   - Blue "Reused (Direct)" badge
   - "View Source" button
   - Higher generation speed (~30s vs 5min)

---

## 🎉 Success Criteria

- [ ] Backend deployed on Render
- [ ] Frontend deployed on Vercel
- [ ] Database migrations completed
- [ ] Can login/register
- [ ] Can create projects
- [ ] Can generate modules (direct AI)
- [ ] Can generate with memories (reuse)
- [ ] Reused badge shows correctly
- [ ] "View Source" button works
- [ ] No console errors
- [ ] API response < 2 seconds

---

## 📊 Expected Results

### Performance Improvements
- **Without Memories:** 6 modules in ~5 minutes (generate all from scratch)
- **With Memories:** 3 modules in ~30 seconds (90% similarity → direct reuse)
- **Cost Reduction:** ~50% (fewer Claude API calls)
- **Quality:** Higher (reuse proven designs)

### UI Indicators
| Module Type | Badge Color | Strategy | Button |
|-------------|-------------|----------|--------|
| AI Generated | Purple 🟣 | - | None |
| Direct Reuse | Blue 🔵 | Direct | View Source |
| Partial Reuse | Blue 🔵 | Partial | View Source |
| Logic Reference | Blue 🔵 | Logic Ref | View Source |

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check logs in Render Dashboard
# Common fix: Verify environment variables are set
```

### CORS errors
```bash
# Update CORS_ORIGINS in Render env vars:
CORS_ORIGINS=["https://your-app.vercel.app","https://*.vercel.app"]
# Save and redeploy
```

### Reused badge not showing
```bash
# 1. Check API response includes reused_from_module_id
# 2. Verify backend saved field during generation
# 3. Check frontend Module interface has field
# 4. Clear browser cache
```

### Database migration fails
```sql
-- Rollback and retry:
-- Use: database/migrations/002_rollback_and_rerun.sql
```

---

## 📱 Share Your Deployment

After successful deployment:

1. **Update CORS:** Add your Vercel domain to backend
2. **Test thoroughly:** All features work end-to-end
3. **Monitor:** Check Render logs for errors
4. **Document:** Save your URLs for reference

**Your URLs:**
- Frontend: `https://<your-app>.vercel.app`
- Backend: `https://rockship-backend.onrender.com`
- API Docs: `https://rockship-backend.onrender.com/docs`

---

## 🎯 Next Steps (Optional)

1. **Custom Domain**
   - Vercel: Settings → Domains
   - Render: Settings → Custom Domain

2. **Monitoring**
   - Set up Sentry for error tracking
   - Monitor Claude API usage in Anthropic Console
   - Track performance in Vercel Analytics

3. **Scale**
   - Upgrade Render plan for more resources
   - Enable Vercel Pro for better performance
   - Optimize database queries

---

## ✨ Congratulations!

You're ready to deploy! Follow the steps above and you'll have a production-ready AI-powered project management system with intelligent memory-based module generation.

**Deployment Time Estimate:** 20-30 minutes

**Questions?** Check DEPLOYMENT.md for detailed troubleshooting.
