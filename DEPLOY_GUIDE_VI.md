# Production Deployment Guide

## ✅ Checklist trước khi deploy

### 1. Kiểm tra Backend
- [x] File `.env` đã có đầy đủ thông tin
- [x] `requirements.txt` đầy đủ dependencies
- [x] `.gitignore` không commit `.env`
- [x] `render.yaml` đã configure đúng
- [x] Test local: `uvicorn src.main:app --reload`

### 2. Kiểm tra Frontend  
- [x] File `.env.local` đã có `VITE_API_URL`
- [x] `package.json` đầy đủ dependencies
- [x] `.gitignore` không commit `.env.local`
- [x] `vercel.json` đã configure đúng
- [x] Test build: `npm run build`

### 3. Kiểm tra Database
- [x] Migrations đã chạy trong Supabase
- [x] Test data có thể tạo/đọc/xóa
- [x] Triggers auto-calculate hoạt động

## 🚀 Các bước deploy

### BACKEND - Deploy lên Render

1. **Tạo tài khoản Render**: https://render.com
   
2. **Tạo Web Service mới**:
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   
3. **Configure service**:
   ```
   Name: rockship-backend
   Region: Oregon (hoặc gần bạn nhất)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Thêm Environment Variables** (Settings → Environment):
   ```
   SUPABASE_URL=https://iituikpbiesgofuraclk.supabase.co
   SUPABASE_KEY=eyJhbGc...
   SUPABASE_SERVICE_KEY=eyJhbGc...
   ANTHROPIC_API_KEY=sk-ant-api03-...
   CLAUDE_MODEL=claude-3-5-sonnet-20241022
   DEBUG=False
   API_V1_PREFIX=/api/v1
   MAX_FILE_SIZE=10485760
   ```

5. **Deploy** - Render sẽ tự động build và deploy

6. **Lấy Backend URL**: 
   - Sau khi deploy xong, copy URL (VD: `https://rockship-backend.onrender.com`)

---

### FRONTEND - Deploy lên Vercel

1. **Tạo tài khoản Vercel**: https://vercel.com

2. **Import project**:
   - Click "Add New..." → "Project"
   - Import GitHub repository

3. **Configure project**:
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **Thêm Environment Variables**:
   ```
   Name: VITE_API_URL
   Value: https://rockship-backend.onrender.com/api/v1
   ```
   (Thay bằng URL backend từ Render)

5. **Deploy** - Vercel sẽ tự động build và deploy

6. **Lấy Frontend URL**:
   - Sau khi deploy xong, copy URL (VD: `https://rockship.vercel.app`)

---

### Update CORS sau khi deploy Frontend

1. **Quay lại Render Dashboard**
2. Vào backend service → Environment
3. **Thêm/Update biến `CORS_ORIGINS`**:
   ```
   CORS_ORIGINS=["https://rockship.vercel.app"]
   ```
   (Thay bằng URL frontend thực tế từ Vercel)

4. Save → Service sẽ tự động redeploy

---

## 🧪 Test Production

1. Mở frontend URL từ Vercel
2. Login với username bất kỳ + password `123`
3. Test các chức năng:
   - ✅ Tạo project
   - ✅ Upload document
   - ✅ Generate modules với AI
   - ✅ Generate tasks với AI
   - ✅ Update task status
   - ✅ Delete items

---

## ⚠️ Lưu ý quan trọng

### Backend (Render Free Tier)
- Service sẽ **sleep sau 15 phút không hoạt động**
- Lần đầu truy cập sẽ mất ~30s để wake up
- Nâng cấp lên **$7/month** để always-on

### Frontend (Vercel)
- Miễn phí hoàn toàn cho personal projects
- Auto-deploy khi push code lên GitHub
- SSL certificate tự động

### Database (Supabase)
- Free tier: 500MB database, 1GB storage
- Đủ cho development và MVP
- Nâng cấp $25/month khi scale

### AI (Anthropic Claude)
- Tính phí theo usage (pay-as-you-go)
- ~$0.003 per 1K input tokens
- ~$0.015 per 1K output tokens
- Monitor usage tại: https://console.anthropic.com

---

## 🔒 Bảo mật

### ⚠️ QUAN TRỌNG - Không commit secrets

**Đã gitignore**:
- ✅ `backend/.env`
- ✅ `frontend/.env.local`
- ✅ `__pycache__/`
- ✅ `node_modules/`

**Kiểm tra trước khi push**:
```bash
git status
# Đảm bảo không có file .env trong danh sách
```

**Nếu đã commit nhầm `.env`**:
```bash
# Xóa khỏi Git history
git rm --cached backend/.env
git commit -m "Remove .env from tracking"

# Rotate tất cả API keys ngay lập tức!
```

---

## 📊 Monitor & Logs

### Backend Logs (Render)
- Dashboard → Service → Logs
- Xem real-time logs
- Debug errors

### Frontend Logs (Vercel)  
- Dashboard → Project → Deployments → View Logs
- Build logs và runtime logs

### Database (Supabase)
- Dashboard → Database → Logs
- Query performance
- Connection logs

---

## 🎯 Production Checklist

Trước khi đi live:

- [ ] Test toàn bộ user flow
- [ ] Verify CORS settings
- [ ] Check all environment variables
- [ ] Monitor API usage (Anthropic)
- [ ] Setup error tracking (optional: Sentry)
- [ ] Document API endpoints
- [ ] Prepare support documentation
- [ ] Backup database

---

## 💰 Chi phí ước tính

### Free Tier (MVP)
```
Vercel Frontend:    $0/month
Render Backend:     $0/month (có sleep)
Supabase Database:  $0/month
Claude AI:          ~$5-10/month (depending on usage)
-----------------------------------
TOTAL:              ~$5-10/month
```

### Production Tier
```
Vercel Frontend:    $0/month
Render Backend:     $7/month (always-on)
Supabase Database:  $25/month
Claude AI:          ~$20-50/month
-----------------------------------
TOTAL:              ~$52-82/month
```

---

## 🐛 Troubleshooting

### "Failed to fetch" error
- ❌ CORS chưa đúng → Update CORS_ORIGINS trong Render
- ❌ Backend sleeping → Đợi 30s hoặc upgrade plan
- ❌ Wrong API URL → Check VITE_API_URL trong Vercel

### "500 Internal Server Error"
- ❌ Check Render logs
- ❌ Verify environment variables
- ❌ Test Supabase connection
- ❌ Verify ANTHROPIC_API_KEY

### Build Failed
- ❌ Check dependencies versions
- ❌ Node.js version (cần 18+)
- ❌ Python version (cần 3.11+)
- ❌ Review build logs

---

## 🎓 Tài liệu tham khảo

- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)

---

## ✨ Sau khi deploy thành công

1. **Share URL** với team/users
2. **Monitor usage** hàng ngày
3. **Collect feedback** từ users
4. **Plan improvements** dựa trên feedback
5. **Scale** khi cần thiết

---

**Chúc bạn deploy thành công! 🚀**

Nếu cần support, check:
- Render logs
- Vercel deployment logs  
- Browser console
- DEPLOYMENT.md file
