# 🔑 How to Get Your Railway Token - Step by Step

## The Issue

`b628f30f-1edf-47fb-9432-39c80161bcd1` appears to be a **Project ID** or **Service ID**, not an authentication token.

**Authentication tokens** are much longer (50+ characters) and look like:
```
rtkn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Option A: Get the Correct Token (For CLI Deployment)

### Step 1: Go to Railway Dashboard
Open: **https://railway.app/account/tokens**

### Step 2: Create New Token
1. Click the **"Create Token"** button
2. Give it a name: `quant-deployment`
3. Click **"Create"**

### Step 3: Copy the Token
You'll see a long string starting with `rtkn_`
- Copy the ENTIRE token (50+ characters)
- It should look like: `rtkn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 4: Use It
```bash
cd /mnt/e/projects/quant/quant/backend
export RAILWAY_TOKEN="rtkn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
./deploy_railway.sh
```

---

## Option B: Web Deployment (NO TOKEN NEEDED) ⭐ RECOMMENDED

This is actually easier and faster!

### Step 1: Open Railway
Go to: **https://railway.app/new**

### Step 2: Deploy from GitHub
1. Click **"Deploy from GitHub repo"**
2. You'll see a list of your repositories
3. Find and select: **`ElliottSax/quant`**

### Step 3: Configure (Optional)
Railway will auto-detect:
- ✅ `railway.toml` - deployment settings
- ✅ `nixpacks.toml` - Python 3.12 build
- ✅ Root path: `quant/backend`

Click **"Deploy"** - that's it!

### Step 4: Add Environment Variables (In Railway Dashboard)
After deployment starts, add these:
```
PROJECT_NAME=QuantBacktesting
VERSION=1.0.0
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///./quant.db
```

Railway auto-generates:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `PORT`

### Step 5: Get Your URL
After build completes (2-3 minutes):
1. Click on your service
2. Go to **"Settings"** → **"Domains"**
3. Railway provides: `your-app.up.railway.app`

### Step 6: Test
```bash
curl https://your-app.up.railway.app/health
curl https://your-app.up.railway.app/api/v1/backtesting/demo/strategies
```

**Done!** ✅

---

## Why Your UUID Doesn't Work

`b628f30f-1edf-47fb-9432-39c80161bcd1` is likely:
- ❌ NOT an authentication token
- ✅ Possibly a Project ID
- ✅ Possibly a Service ID
- ✅ Possibly an Environment ID

**But you need an authentication token for CLI deployment.**

---

## Quick Comparison

| Method | Needs Token? | Steps | Time |
|--------|--------------|-------|------|
| **Web Deployment** | ❌ No | 3 clicks | 5 min |
| **CLI Deployment** | ✅ Yes | Get token + 1 command | 5 min |

**Recommendation:** Use Web Deployment - it's faster and easier!

---

## Still Want CLI?

If you need the CLI deployment:

1. Visit: https://railway.app/account/tokens
2. Create token (starts with `rtkn_`)
3. Copy the FULL token (all 50+ characters)
4. Use it:
   ```bash
   export RAILWAY_TOKEN="rtkn_your_actual_token_here"
   ./deploy_railway.sh
   ```

---

## Or Just Use the Web!

**Click here now:** https://railway.app/new

1. Select `ElliottSax/quant`
2. Click "Deploy"
3. Wait 3 minutes
4. Done! ✅

No token needed, no CLI needed, just 2 clicks!

---

**Fastest path to deployment:** Web interface → https://railway.app/new 🚀
