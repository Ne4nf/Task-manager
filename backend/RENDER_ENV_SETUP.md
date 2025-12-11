# 🚀 Render Environment Variables Setup

Copy and paste these environment variables into your Render service dashboard.

## 📋 Environment Variables

Go to: **Render Dashboard → Your Service → Environment**

```bash
# Application Configuration
APP_NAME=Rockship Backend
APP_VERSION=1.0.0
DEBUG=False
API_V1_PREFIX=/api/v1

# Supabase Configuration
SUPABASE_URL=https://iituikpbiesgofuraclk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlpdHVpa3BiaWVzZ29mdXJhY2xrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2OTc3MTksImV4cCI6MjA4MDI3MzcxOX0.1RrqnJBruY43ObzmWucWB9Dsm5Jj6oMMF2ezTpiSzOw
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlpdHVpa3BiaWVzZ29mdXJhY2xrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDY5NzcxOSwiZXhwIjoyMDgwMjczNzE5fQ.XKzKOrYsxGfgF5ueAlF0KN75vTceYMYkXg8SpG18q6I

# Claude AI Configuration (✅ VERIFIED WORKING - Dec 11, 2025)
ANTHROPIC_API_KEY=[YOUR_API_KEY_HERE]
CLAUDE_MODEL=claude-3-5-sonnet-latest

# CORS Configuration (Update with your Vercel URL)
CORS_ORIGINS=["https://task-manager-mijz.vercel.app","https://your-frontend-url.vercel.app"]

# File Upload Configuration
MAX_FILE_SIZE=10485760
```

---

## 🔑 Critical Variables to Update

### 1. **ANTHROPIC_API_KEY** (✅ Already Updated)
- New key created: Dec 11, 2025
- Never used before
- Should work immediately

### 2. **CORS_ORIGINS**
Replace with your actual Vercel frontend URL:
```
CORS_ORIGINS=["https://task-manager-mijz.vercel.app"]
```

---

## 📝 Step-by-Step Setup

### Step 1: Go to Render Dashboard
1. Visit: https://dashboard.render.com
2. Select your service: **rockship-backend**
3. Click **Environment** tab

### Step 2: Update Each Variable
For each variable above:
1. Find the KEY name in the list
2. Click the **edit icon** (pencil)
3. Paste the VALUE
4. Click **Save**

### Step 3: Critical Updates
⚠️ **MUST UPDATE:**
- `ANTHROPIC_API_KEY` - Use the new key from above
- `CORS_ORIGINS` - Add your Vercel URL

✅ **Already Set (no change needed):**
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_KEY`
- `CLAUDE_MODEL`
- `MAX_FILE_SIZE`

### Step 4: Verify After Deploy
Once Render redeploys (~5 minutes):

```bash
# Test configuration endpoint
curl https://task-manager-bzwfq.onrender.com/config-check

# Expected response:
{
  "anthropic_key_exists": true,
  "anthropic_key_length": 108,
  "claude_model": "claude-3-5-sonnet-latest"
}
```

---

## ✅ Verification Checklist

After updating environment variables:

- [ ] All environment variables saved in Render
- [ ] Service automatically redeployed
- [ ] `/config-check` endpoint returns success
- [ ] Test task generation on frontend
- [ ] No 404/500 errors in Render logs

---

## 🆘 Troubleshooting

### If Task Generation Still Fails:

1. **Check Render Logs:**
   ```
   Dashboard → Service → Logs tab
   ```

2. **Verify API Key:**
   - Go to https://console.anthropic.com/settings/keys
   - Check "LAST USED AT" column updates after testing

3. **Test API Key Locally:**
   ```bash
   cd backend
   python test_anthropic.py
   ```

### If CORS Errors:

Update `CORS_ORIGINS` with your exact Vercel URL (check browser console for the origin).

---

## 📅 Last Updated

**Date:** December 11, 2025  
**API Key Created:** Today (never used before)  
**Expected Status:** ✅ Should work immediately

---

## 🔒 Security Notes

- ⚠️ Never commit `.env` file to Git
- ✅ This file is safe to commit (documentation only)
- 🔄 Rotate API keys periodically
- 📝 Keep this file updated when keys change
