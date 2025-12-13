# 🚀 Deployment Guide - Render + Vercel

## 📋 Tổng Quan

**Backend**: Render (Free tier)  
**Frontend**: Vercel (Free tier)  
**Database**: Supabase (đã có sẵn)

---

## 1️⃣ Deploy Backend lên Render

### Bước 1: Tạo Web Service
1. Truy cập https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub account (nếu chưa)
4. Chọn repository: **`Ne4nf/Task-manager`**

### Bước 2: Configure Service
Render sẽ **tự động phát hiện** `backend/render.yaml`. Bạn chỉ cần:

1. **Name**: `task-manager-backend` (hoặc tên bạn muốn)
2. **Branch**: `main`
3. Render sẽ load config từ `render.yaml`

### Bước 3: Add Environment Variables

Click vào **Environment** tab và thêm các biến sau:

```bash
# Supabase (REQUIRED)
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_KEY=<your-supabase-service-role-key>

# Anthropic (REQUIRED)
ANTHROPIC_API_KEY=<your-anthropic-api-key>

# CORS (IMPORTANT - sẽ update sau khi có Vercel URL)
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

**⚠️ LƯU Ý**: 
- `CORS_ORIGINS` phải là JSON array format: `["url1","url2"]`
- URL Vercel bạn sẽ có sau bước 2

### Bước 4: Deploy

1. Click **"Create Web Service"**
2. Render sẽ:
   - Clone repo
   - Detect `render.yaml`
   - Install Python 3.11.9
   - Run `pip install -r requirements.txt`
   - Start server với uvicorn
3. Đợi 5-10 phút

### Bước 5: Lấy Backend URL

Sau khi deploy xong, bạn sẽ có URL:
```
https://task-manager-backend-xxxx.onrender.com
```

**Copy URL này** - cần cho frontend!

---

## 2️⃣ Deploy Frontend lên Vercel

### Bước 1: Import Repository

1. Truy cập https://vercel.com/new
2. Import Git Repository
3. Chọn **`Ne4nf/Task-manager`**

### Bước 2: Configure Project

1. **Framework Preset**: Vite (auto-detected)
2. **Root Directory**: `frontend` ⚠️ QUAN TRỌNG!
3. **Build Command**: `npm run build` (auto-filled)
4. **Output Directory**: `dist` (auto-filled)

### Bước 3: Environment Variables

Click **"Environment Variables"** và thêm:

```bash
# Production Backend URL (thay XXXX bằng URL Render của bạn)
VITE_API_URL=https://task-manager-backend-xxxx.onrender.com/api/v1
```

**Ví dụ**:
```bash
VITE_API_URL=https://task-manager-backend-abc123.onrender.com/api/v1
```

### Bước 4: Deploy

1. Click **"Deploy"**
2. Đợi 2-3 phút
3. Vercel sẽ:
   - Install dependencies
   - Run `npm run build`
   - Deploy static files

### Bước 5: Lấy Frontend URL

Sau khi deploy xong, bạn sẽ có URL:
```
https://task-manager-abc123.vercel.app
```

---

## 3️⃣ Update CORS (QUAN TRỌNG!)

Sau khi có Frontend URL, **PHẢI** update CORS trong Render:

### Cách 1: Qua Render Dashboard
1. Vào Render → Service → Environment
2. Edit `CORS_ORIGINS`:
   ```
   ["https://task-manager-abc123.vercel.app"]
   ```
3. Save → Service sẽ auto-redeploy

### Cách 2: Update render.yaml (recommended)
1. Edit `backend/render.yaml`:
   ```yaml
   - key: CORS_ORIGINS
     value: '["https://your-actual-vercel-url.vercel.app"]'
   ```
2. Commit & push:
   ```bash
   git add backend/render.yaml
   git commit -m "Update CORS for production"
   git push
   ```
3. Render sẽ auto-redeploy

---

## 4️⃣ Verify Deployment

### Test Backend

```bash
# Health check
curl https://task-manager-backend-xxxx.onrender.com/health

# Should return: {"status": "healthy"}

# Config check
curl https://task-manager-backend-xxxx.onrender.com/config-check

# Should see: anthropic_key_exists: true, supabase_url_exists: true
```

### Test Frontend

1. Mở: `https://your-frontend.vercel.app`
2. Should see login page
3. Try login - should connect to backend

### Test API Docs

Mở: `https://task-manager-backend-xxxx.onrender.com/docs`

---

## 🐛 Troubleshooting

### Backend không start

**Check logs trong Render Dashboard:**

1. Vào Service → Logs
2. Tìm errors:

**Common issues:**

```bash
# Issue: Python version mismatch
Solution: render.yaml có PYTHON_VERSION=3.11.9

# Issue: Module not found
Solution: Đảm bảo requirements.txt đúng

# Issue: SUPABASE_URL missing
Solution: Add environment variable trong Render

# Issue: ANTHROPIC_API_KEY invalid
Solution: Check API key còn hoạt động không
```

### Frontend không connect Backend

**Check:**

1. **VITE_API_URL** trong Vercel environment variables
2. **CORS_ORIGINS** trong Render environment variables
3. Backend có đang chạy không (health check)

**Fix:**

```bash
# 1. Update VITE_API_URL trong Vercel
VITE_API_URL=https://your-actual-backend.onrender.com/api/v1

# 2. Update CORS trong Render
CORS_ORIGINS=["https://your-actual-frontend.vercel.app"]

# 3. Redeploy both
```

### CORS Error

**Symptom:**
```
Access to fetch at 'https://backend.onrender.com' from origin 
'https://frontend.vercel.app' has been blocked by CORS
```

**Fix:**

Render environment variables → Update `CORS_ORIGINS`:
```
["https://your-frontend.vercel.app"]
```

Format **PHẢI** là JSON array!

---

## 📋 Checklist

### Before Deploy
- [x] Code pushed to GitHub
- [x] `.env` files NOT pushed (gitignored)
- [x] `render.yaml` configured
- [x] `vercel.json` configured

### Backend (Render)
- [ ] Service created
- [ ] Environment variables added:
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_KEY
  - [ ] SUPABASE_SERVICE_KEY
  - [ ] ANTHROPIC_API_KEY
  - [ ] CORS_ORIGINS (update sau)
- [ ] Deploy successful
- [ ] Backend URL copied

### Frontend (Vercel)
- [ ] Project imported
- [ ] Root directory set to `frontend`
- [ ] Environment variable added:
  - [ ] VITE_API_URL (với backend URL)
- [ ] Deploy successful
- [ ] Frontend URL copied

### Final Steps
- [ ] Update CORS in Render với Vercel URL
- [ ] Test health check
- [ ] Test login
- [ ] Test creating project

---

## 🔑 Environment Variables Summary

### Render (Backend)
```bash
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_KEY=<your-supabase-service-role-key>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

### Vercel (Frontend)
```bash
VITE_API_URL=https://your-backend.onrender.com/api/v1
```

---

## 🎯 Quick Commands

### Redeploy Backend
```bash
# Update code
git add .
git commit -m "Update backend"
git push

# Render auto-deploys on push
```

### Redeploy Frontend
```bash
# Update code
git add .
git commit -m "Update frontend"
git push

# Vercel auto-deploys on push
```

### Force Redeploy
- **Render**: Dashboard → Manual Deploy
- **Vercel**: Dashboard → Deployments → Redeploy

---

## 🎉 Success Checklist

Sau khi deploy xong, verify:

- [ ] Backend health check returns OK
- [ ] Frontend loads without errors
- [ ] Login works
- [ ] Can create project
- [ ] Can generate modules with AI
- [ ] Git Analyzer works
- [ ] No CORS errors in console

---

**Bây giờ bắt đầu deploy theo từng bước ở trên nhé! 🚀**

**Thứ tự:**
1. Deploy Backend lên Render trước
2. Copy Backend URL
3. Deploy Frontend lên Vercel (với Backend URL)
4. Copy Frontend URL
5. Update CORS trong Render
6. Done!
