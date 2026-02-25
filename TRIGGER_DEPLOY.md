# 🚀 Trigger Render Deployment Programmatically

Your code is already pushed to GitHub (commit `3bc7333`).

---

## Method 1: Auto-Sync (Easiest) ⭐

Render should auto-detect the new commit. If not:

### Via Dashboard:
1. Go to: https://dashboard.render.com/blueprint/exs-d6fllop5pdvs738rgc90
2. Click "Manual Sync" tab
3. Click "Sync Now"

### Via URL (Opens in browser):
```bash
# Open Render blueprint in browser
open "https://dashboard.render.com/blueprint/exs-d6fllop5pdvs738rgc90"
# Or on WSL:
wslview "https://dashboard.render.com/blueprint/exs-d6fllop5pdvs738rgc90"
```

---

## Method 2: Deploy Hook (Most Programmatic)

Get your Deploy Hook URL from Render, then:

```bash
# Trigger deploy with a simple curl
curl -X POST "https://api.render.com/deploy/srv-XXXXX?key=YYYYY"
```

### How to Get Your Deploy Hook:

1. **Via Dashboard**:
   - Go to: https://dashboard.render.com/
   - Click on "quant-backend" service
   - Settings → Deploy Hook
   - Copy the URL
   
2. **Then trigger programmatically**:
   ```bash
   # Save your deploy hook
   DEPLOY_HOOK="https://api.render.com/deploy/srv-XXXXX?key=YYYYY"
   
   # Trigger deploy
   curl -X POST "$DEPLOY_HOOK"
   ```

---

## Method 3: Render API (Most Control)

### Get API Key:
1. Go to: https://dashboard.render.com/account/api-keys
2. Click "Create API Key"
3. Copy the key

### Deploy via API:
```bash
# Set your API key
export RENDER_API_KEY='rnd_XXXXXXXXXXXXX'

# Run deployment script
./deploy_render.sh
```

---

## Method 4: Force Re-Deploy via Git

Trigger a new deploy by pushing an empty commit:

```bash
cd /mnt/e/projects/quant
git commit --allow-empty -m "chore: trigger Render redeploy"
git push origin main
```

Render will detect the new commit and redeploy automatically.

---

## Method 5: GitHub Actions (Auto-Deploy)

Already configured! Just push to main:

```bash
git push origin main
```

And GitHub Actions will auto-deploy to Render (if secrets are configured).

---

## Quick Fix NOW

Since your code is already pushed, the **fastest way** is:

```bash
# Force trigger via empty commit
cd /mnt/e/projects/quant
git commit --allow-empty -m "chore: trigger Render rebuild with fixed dependencies"
git push origin main
```

This will make Render detect a new commit and rebuild with the fixed `requirements.render.txt`.

---

## Check Build Status

After triggering:
- Dashboard: https://dashboard.render.com/
- Logs: Click "quant-backend" → "Logs" tab
- Events: Click "Events" to see deploy history

---

**Recommended**: Use Method 4 (empty commit) to trigger rebuild NOW! 🚀
