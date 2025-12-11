# 🔧 URGENT FIX: Update Anthropic API Key on Render

## Problem
Render is using a different/invalid ANTHROPIC_API_KEY than your local environment.

## Solution

### Step 1: Get your working API key
Your local `.env` has a working key. Use that one OR generate a new one from Anthropic Console.

**Option A - Use local key:**
```
Check your local .env file for ANTHROPIC_API_KEY
```

**Option B - Generate new key:**
1. Go to: https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Copy the new key (starts with `sk-ant-api03-...`)

### Step 2: Update Render Environment Variables

1. Go to: https://dashboard.render.com/
2. Select your service: `rockship-backend`
3. Go to: **Environment** tab
4. Find `ANTHROPIC_API_KEY`
5. Click **Edit** (pencil icon)
6. Paste your working API key
7. Click **Save Changes**
8. Render will automatically redeploy (~3-5 minutes)

### Step 3: Verify Fix

After Render redeploys, test:

```bash
# Check config
curl https://your-backend.onrender.com/config-check

# Expected:
{
  "anthropic_key_exists": true,
  "anthropic_key_length": 108  # Should be ~100-120 chars
}

# Test task generation
curl -X POST https://your-backend.onrender.com/api/v1/tasks/generate \
  -H "Content-Type: application/json" \
  -H "X-User-ID: your-user-id" \
  -d '{"module_id": "module-id"}'
```

### Step 4: Security Note

⚠️ **DO NOT commit your `.env` file to Git!**

Your `.env` file contains secrets. Make sure it's in `.gitignore`:

```bash
# Check if .env is ignored
git status
# Should NOT show .env as "Changes to be committed"
```

If `.env` is tracked by git:
```bash
git rm --cached backend/.env
echo "backend/.env" >> .gitignore
git add .gitignore
git commit -m "Remove .env from git tracking"
git push
```

Then:
1. Regenerate API keys (old ones are exposed in git history)
2. Update both local `.env` and Render environment variables

---

## Quick Commands

**Test local API key:**
```bash
cd backend
python test_anthropic.py
```

**Check what's in your local .env (safe to run):**
```bash
# This will show length and prefix only (not full key)
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); key = os.getenv('ANTHROPIC_API_KEY', ''); print(f'Key: {key[:20]}...{key[-10:]}' if key else 'Not found'); print(f'Length: {len(key)}')"
```

**After updating Render, verify:**
```bash
curl https://your-backend.onrender.com/config-check | python -m json.tool
```

---

## Expected Timeline

- Update Render env var: **1 minute**
- Render redeploy: **3-5 minutes**  
- Test & verify: **1 minute**

**Total: ~5-7 minutes to fix**

---

## If Still Fails After Update

1. **Check Anthropic account status:**
   - https://console.anthropic.com/
   - Verify you have credits remaining
   - Check if account is active

2. **Try different model:**
   - Change `CLAUDE_MODEL` to: `claude-3-5-sonnet-latest`
   - Or: `claude-3-sonnet-20240229`

3. **Check Render logs:**
   - Dashboard → Logs
   - Look for detailed error message
   - Share full error if still stuck
