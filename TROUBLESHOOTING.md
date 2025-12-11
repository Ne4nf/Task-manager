# 🔧 Deployment Troubleshooting Guide

## ❌ Common Errors & Solutions

### 1. **Error: "model: claude-3-5-sonnet-20241022" (500 Internal Server Error)**

**Symptom:**
```
Failed to generate tasks: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-3-5-sonnet-20241022'}}
```

**Root Cause:** Anthropic API key not configured or invalid on Render.

**Solution:**

1. **Check API Key exists:**
   ```bash
   curl https://your-backend.onrender.com/config-check
   ```
   Expected output:
   ```json
   {
     "anthropic_key_exists": true,
     "anthropic_key_length": 108,
     "claude_model": "claude-3-5-sonnet-20241022"
   }
   ```

2. **If `anthropic_key_exists: false`:**
   - Go to Render Dashboard → Your Service → Environment
   - Add environment variable:
     ```
     ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
     ```
   - Click "Save Changes"
   - Wait for automatic redeploy (~2 minutes)

3. **If key exists but still fails:**
   - Verify key is valid: https://console.anthropic.com/settings/keys
   - Check key has sufficient credits
   - Regenerate key if needed and update Render

4. **Verify fix:**
   ```bash
   curl -X POST https://your-backend.onrender.com/api/v1/tasks/generate \
     -H "Content-Type: application/json" \
     -H "X-User-ID: your-user-id" \
     -d '{"module_id": "your-module-id"}'
   ```

---

### 2. **Error: CORS Policy Block**

**Symptom:**
```
Access to fetch at 'https://backend.onrender.com/api/v1/...' from origin 'https://app.vercel.app' has been blocked by CORS policy
```

**Solution:**

1. Update `CORS_ORIGINS` on Render:
   ```
   CORS_ORIGINS=["https://your-app.vercel.app","https://your-app-*.vercel.app"]
   ```

2. Include wildcard for Vercel preview deployments

3. Redeploy backend

---

### 3. **Error: Module Generation Returns Empty**

**Symptom:**
- API call succeeds (200 OK)
- But no modules created
- Or modules missing fields

**Solution:**

1. Check Claude API response in logs:
   ```
   Render Dashboard → Logs → Search for "Claude AI"
   ```

2. Look for JSON parsing errors:
   ```
   ⚠️ Initial parse failed: ...
   🔧 Attempting to fix literal newlines...
   ```

3. If auto-fix fails, update prompt in `utils.py`

---

### 4. **Error: Supabase Connection Refused**

**Symptom:**
```
Failed to connect to Supabase: Connection refused
```

**Solution:**

1. Verify Supabase project is active:
   - https://supabase.com/dashboard

2. Check environment variables on Render:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGc...
   SUPABASE_SERVICE_KEY=eyJhbGc...
   ```

3. Test connection:
   ```bash
   curl https://your-backend.onrender.com/api/v1/projects/ \
     -H "X-User-ID: test-user-id"
   ```

---

### 5. **Error: Frontend Shows "Network Error"**

**Symptom:**
- Frontend can't reach backend
- All API calls fail

**Solution:**

1. Check `VITE_API_URL` on Vercel:
   - Dashboard → Your Project → Settings → Environment Variables
   - Should be: `https://your-backend.onrender.com/api/v1`

2. Verify backend is running:
   ```bash
   curl https://your-backend.onrender.com/health
   # Expected: {"status": "healthy"}
   ```

3. If backend is down:
   - Render free tier sleeps after 15 min inactivity
   - First request wakes it up (~30 seconds)
   - Consider upgrading to paid plan for always-on

---

### 6. **Error: "Reused" Badge Not Showing**

**Symptom:**
- Module was generated with memories
- But shows "AI Generated" instead of "Reused"

**Solution:**

1. Check backend response includes `reused_from_module_id`:
   ```bash
   curl https://your-backend.onrender.com/api/v1/modules/module-id \
     -H "X-User-ID: your-user-id"
   ```

2. If field missing, backend bug:
   - Check `service.py` saves `reused_from_module_id`
   - Verify database column exists in Supabase

3. Frontend TypeScript interface must include:
   ```typescript
   reused_from_module_id?: string;
   reuse_strategy?: 'direct' | 'partial_reuse' | 'logic_reference';
   ```

---

### 7. **Error: Build Fails on Vercel**

**Symptom:**
```
Error: Failed to compile
Module not found: Can't resolve '...'
```

**Solution:**

1. Test build locally:
   ```bash
   cd frontend
   npm run build
   ```

2. If successful locally but fails on Vercel:
   - Clear Vercel cache: Settings → Clear Cache → Redeploy
   - Check Node version matches: `package.json` → `engines`

3. Common issues:
   - Case-sensitive imports (works on Windows, fails on Linux)
   - Missing dependencies in `package.json`

---

### 8. **Error: Slow API Response (>10 seconds)**

**Symptom:**
- API calls take very long
- Frontend shows loading forever

**Solution:**

1. **Cold start on Render:**
   - Free tier spins down after 15 min
   - First request takes ~30 seconds
   - Subsequent requests fast
   - **Fix:** Upgrade to paid plan or use cron job to ping every 10 min

2. **Claude API slow:**
   - Check prompt size (should be <100KB)
   - Reduce `max_tokens` if possible
   - Monitor Anthropic status: https://status.anthropic.com/

3. **Database slow:**
   - Check Supabase performance dashboard
   - Verify indexes on frequently queried columns

---

## 🔍 Debugging Checklist

Before asking for help, check:

- [ ] Backend health: `curl https://backend.onrender.com/health`
- [ ] Config check: `curl https://backend.onrender.com/config-check`
- [ ] Render logs: Dashboard → Logs (last 100 lines)
- [ ] Vercel logs: Dashboard → Deployments → View Logs
- [ ] Browser console: F12 → Console tab
- [ ] Network tab: F12 → Network → Failed requests

---

## 📊 Monitoring Commands

**Check backend health:**
```bash
curl https://your-backend.onrender.com/health
```

**Check configuration:**
```bash
curl https://your-backend.onrender.com/config-check
```

**Test authentication:**
```bash
curl -X POST https://your-backend.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**List projects:**
```bash
curl https://your-backend.onrender.com/api/v1/projects/ \
  -H "X-User-ID: your-user-id"
```

**Generate modules:**
```bash
curl -X POST https://your-backend.onrender.com/api/v1/modules/generate-with-memories \
  -H "Content-Type: application/json" \
  -H "X-User-ID: your-user-id" \
  -d '{
    "project_id": "project-id",
    "requirements_doc": "Test requirements..."
  }'
```

---

## 🆘 Quick Fixes

**Backend not responding:**
```bash
# Trigger Render redeploy
git commit --allow-empty -m "Trigger redeploy"
git push origin main
```

**Frontend not updating:**
```bash
# Trigger Vercel redeploy
cd frontend
vercel --prod
```

**Clear all caches:**
1. Vercel: Settings → Clear Cache
2. Browser: Ctrl+Shift+Delete → Clear all
3. Render: Automatic on redeploy

---

## 📞 Support

**Still stuck?**
1. Check Render logs (most common issues show here)
2. Check browser console for frontend errors
3. Verify all environment variables are set
4. Test with Postman/curl to isolate frontend vs backend

**Render Support:**
- Docs: https://render.com/docs
- Status: https://status.render.com/

**Anthropic Support:**
- Status: https://status.anthropic.com/
- Console: https://console.anthropic.com/
