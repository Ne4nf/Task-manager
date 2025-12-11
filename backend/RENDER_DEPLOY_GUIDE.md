# 🚀 Hướng Dẫn Deploy Backend Lên Render (Hoàn Toàn Mới)

## 📋 Checklist Trước Khi Deploy

- [ ] Code đã được push lên GitHub
- [ ] File `render.yaml` đã có trong repo
- [ ] File `requirements.txt` đã đầy đủ dependencies
- [ ] Có sẵn API keys (Anthropic, Supabase)

---

## 🔧 Bước 1: Chuẩn Bị Files

### 1.1 Kiểm tra `render.yaml`

File này đã được tạo sẵn tại `backend/render.yaml`. Nội dung:

```yaml
services:
  - type: web
    name: rockship-backend
    env: python
    region: singapore  # Hoặc oregon
    plan: free
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: APP_NAME
        value: Rockship Backend
      - key: APP_VERSION
        value: 1.0.0
      - key: DEBUG
        value: False
      - key: API_V1_PREFIX
        value: /api/v1
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: CLAUDE_MODEL
        value: claude-3-5-sonnet-latest
      - key: CORS_ORIGINS
        value: '["https://task-manager-mijz.vercel.app"]'
      - key: MAX_FILE_SIZE
        value: 10485760
```

### 1.2 Kiểm tra `requirements.txt`

File `backend/requirements.txt` phải có:

```txt
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-dotenv
anthropic
supabase
python-multipart
```

### 1.3 Tạo file `runtime.txt` (nếu chưa có)

```txt
python-3.11.0
```

---

## 🌐 Bước 2: Tạo Web Service Mới Trên Render

### 2.1 Vào Render Dashboard

1. Truy cập: https://dashboard.render.com
2. Click nút **"New +"** (góc trên bên phải)
3. Chọn **"Web Service"**

### 2.2 Connect Repository

**Cách 1: Connect GitHub Repository**
1. Click **"Connect account"** nếu chưa connect GitHub
2. Authorize Render truy cập GitHub
3. Chọn repository: **Ne4nf/Task-manager**

**Cách 2: Public Git Repository**
1. Chọn **"Public Git repository"**
2. Paste URL: `https://github.com/Ne4nf/Task-manager.git`

### 2.3 Cấu Hình Service

Điền thông tin sau:

| Field | Value |
|-------|-------|
| **Name** | `task-manager-backend` hoặc tên bạn muốn |
| **Region** | `Singapore` (gần Việt Nam hơn) |
| **Branch** | `main` |
| **Root Directory** | `backend` ⚠️ QUAN TRỌNG |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn src.main:app --host 0.0.0.0 --port $PORT` |

⚠️ **Lưu ý:** Phải set **Root Directory = `backend`** để Render biết code nằm trong folder `backend/`

---

## 🔐 Bước 3: Thêm Environment Variables

Sau khi điền xong thông tin trên, kéo xuống phần **"Environment Variables"**.

Click **"Add Environment Variable"** và thêm từng biến sau:

### 3.1 Application Config

```
APP_NAME = Rockship Backend
APP_VERSION = 1.0.0
DEBUG = False
API_V1_PREFIX = /api/v1
```

### 3.2 Supabase Config

```
SUPABASE_URL = https://iituikpbiesgofuraclk.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlpdHVpa3BiaWVzZ29mdXJhY2xrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2OTc3MTksImV4cCI6MjA4MDI3MzcxOX0.1RrqnJBruY43ObzmWucWB9Dsm5Jj6oMMF2ezTpiSzOw
SUPABASE_SERVICE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlpdHVpa3BiaWVzZ29mdXJhY2xrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDY5NzcxOSwiZXhwIjoyMDgwMjczNzE5fQ.XKzKOrYsxGfgF5ueAlF0KN75vTceYMYkXg8SpG18q6I
```

### 3.3 Claude AI Config (⚠️ QUAN TRỌNG)

```
ANTHROPIC_API_KEY = [YOUR_ANTHROPIC_API_KEY_HERE]
CLAUDE_MODEL = claude-3-5-sonnet-latest
```

⚠️ **Lấy API key từ file `.env` local hoặc tạo mới tại:** https://console.anthropic.com/settings/keys

### 3.4 CORS Config

```
CORS_ORIGINS = ["https://task-manager-mijz.vercel.app"]
```

⚠️ **Chú ý:** Nếu frontend của bạn có URL khác, thay đổi URL trong `CORS_ORIGINS`

### 3.5 File Upload Config

```
MAX_FILE_SIZE = 10485760
```

---

## 📝 Bước 4: Tạo Service

1. Kiểm tra lại tất cả thông tin
2. Click nút **"Create Web Service"**
3. Render sẽ bắt đầu deploy (5-10 phút)

---

## 🧪 Bước 5: Kiểm Tra Deploy

### 5.1 Xem Logs

Trong lúc deploy, click tab **"Logs"** để xem tiến trình:

```bash
# Logs thành công sẽ như sau:
==> Installing dependencies from requirements.txt
Successfully installed fastapi-0.xxx uvicorn-0.xxx ...
==> Build successful 🎉
==> Starting service with 'uvicorn src.main:app --host 0.0.0.0 --port 10000'
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

### 5.2 Test API

Sau khi deploy xong, Render sẽ cung cấp URL dạng:
```
https://task-manager-backend-xxxx.onrender.com
```

**Test endpoints:**

```bash
# 1. Health check
curl https://task-manager-backend-xxxx.onrender.com/health

# 2. Config check
curl https://task-manager-backend-xxxx.onrender.com/config-check

# 3. API docs
Mở browser: https://task-manager-backend-xxxx.onrender.com/docs
```

---

## 🔧 Bước 6: Cấu Hình Frontend

### 6.1 Update Vercel Environment Variable

1. Vào Vercel Dashboard: https://vercel.com/dashboard
2. Chọn project frontend
3. Settings → Environment Variables
4. Thêm/Update biến:

```
VITE_API_URL = https://task-manager-backend-xxxx.onrender.com/api/v1
```

⚠️ Thay `xxxx` bằng URL thực tế của bạn

5. Redeploy frontend

### 6.2 Update CORS trên Render

Nếu frontend URL thay đổi:

1. Vào Render Dashboard
2. Chọn service vừa tạo
3. Environment → Edit `CORS_ORIGINS`
4. Thêm URL mới: `["https://your-frontend-url.vercel.app"]`
5. Save → Auto redeploy

---

## ✅ Bước 7: Test End-to-End

### 7.1 Test Task Generation

1. Vào frontend: https://task-manager-mijz.vercel.app
2. Login
3. Chọn 1 project
4. Chọn 1 module
5. Click **"Gen AI Tasks"**
6. Nếu tasks được tạo → ✅ **THÀNH CÔNG!**

### 7.2 Test Document Upload

1. Vào module bất kỳ
2. Upload document
3. Kiểm tra xử lý
4. Nếu upload thành công → ✅ **THÀNH CÔNG!**

---

## 🐛 Troubleshooting

### Lỗi 1: Build Failed - "No module named 'src'"

**Nguyên nhân:** Root Directory không đúng

**Giải pháp:**
1. Settings → Root Directory = `backend`
2. Manual Deploy

### Lỗi 2: 502 Bad Gateway

**Nguyên nhân:** Service chưa start hoặc port không đúng

**Giải pháp:**
1. Kiểm tra Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
2. Xem Logs để biết chi tiết

### Lỗi 3: CORS Error trên Frontend

**Nguyên nhân:** Frontend URL không có trong CORS_ORIGINS

**Giải pháp:**
1. Environment → Edit `CORS_ORIGINS`
2. Thêm URL frontend chính xác
3. Format: `["https://url1.com","https://url2.com"]`

### Lỗi 4: 404 Model Not Found (Claude)

**Nguyên nhân:** API key không hợp lệ

**Giải pháp:**
1. Kiểm tra API key trên Anthropic Console
2. Tạo key mới nếu cần
3. Update `ANTHROPIC_API_KEY` trên Render

### Lỗi 5: 500 Internal Server Error

**Kiểm tra:**
1. Tab Logs trên Render
2. Tìm dòng lỗi đỏ
3. Debug theo message cụ thể

---

## 🔄 Auto Deploy từ GitHub

Render sẽ tự động deploy khi:
- Push code mới lên branch `main`
- Merge pull request vào `main`

**Tắt auto deploy:**
1. Settings → Build & Deploy
2. Tắt "Auto-Deploy"

---

## 📊 Monitoring

### Free Plan Limitations

- **RAM:** 512 MB
- **CPU:** Shared
- **Sleep:** Service ngủ sau 15 phút không hoạt động
- **Cold start:** 30-60 giây để wake up

### Xem Metrics

1. Dashboard → Service
2. Tab "Metrics"
3. Xem CPU, Memory, Response time

---

## 💰 Chi Phí

**Free Plan:**
- ✅ 750 giờ/tháng miễn phí
- ✅ Đủ cho development/testing
- ⚠️ Service ngủ sau 15 phút idle

**Paid Plan ($7/tháng):**
- ✅ Không ngủ
- ✅ RAM nhiều hơn
- ✅ Priority support

---

## 📝 Checklist Deploy Thành Công

- [ ] Service status: **Live** (màu xanh)
- [ ] Logs không có error
- [ ] `/health` endpoint returns 200
- [ ] `/config-check` shows correct config
- [ ] `/docs` (Swagger UI) accessible
- [ ] Frontend có thể call API
- [ ] Task generation hoạt động
- [ ] Document upload hoạt động

---

## 🆘 Cần Trợ Giúp?

### Render Logs
```bash
Dashboard → Service → Logs tab
```

### Test API Key Local
```bash
cd backend
python test_anthropic.py
```

### Check Environment Variables
```bash
Dashboard → Service → Environment tab
```

---

## 🎉 Hoàn Thành!

Sau khi làm theo các bước trên, backend sẽ:
- ✅ Deploy thành công trên Render
- ✅ Có SSL certificate tự động
- ✅ Auto deploy khi push code
- ✅ Hoạt động ổn định

**URL cuối cùng của bạn:**
```
Backend: https://task-manager-backend-xxxx.onrender.com
Frontend: https://task-manager-mijz.vercel.app
```

Copy URL này và cập nhật trong các config cần thiết!
