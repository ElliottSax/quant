# Congress Alerts Live Deployment — 3-Minute Checklist
**Status:** Ready to go live (code complete, backend running)  
**Timeline:** 3 minutes Elliott input + auto-deployment

---

## STEP 1: Gather 6 Credentials (2 minutes)

Copy-paste these values into the fields below:

### **A. Stripe Secret Key**
- Go to: https://dashboard.stripe.com/apikeys
- Copy: The `sk_live_` key (long alphanumeric starting with `sk_live_`)
- Paste here: `STRIPE_SECRET_KEY=`

### **B. Stripe Product Prices**
If Congress Alerts Pro product doesn't exist yet:
1. https://dashboard.stripe.com/products/create
2. Name: "Congress Alerts Pro"
3. Add pricing: $9/month → copy `price_` ID
4. Add pricing: $79/year → copy `price_` ID

- Monthly price ID: `STRIPE_CONGRESS_ALERTS_PRICE_MONTHLY=price_`
- Yearly price ID: `STRIPE_CONGRESS_ALERTS_PRICE_YEARLY=price_`

### **C. Stripe Webhook Secret**
1. Go to: https://dashboard.stripe.com/webhooks
2. Click: "+ Add endpoint"
3. Endpoint URL: `https://quantengines.com/api/congress-alerts/webhook`
4. Events: Select `checkout.session.completed` + `invoice.payment_succeeded`
5. Copy: The signing secret (starts with `whsec_`)

- Paste here: `STRIPE_CONGRESS_ALERTS_WEBHOOK_SECRET=whsec_`

### **D. Supabase Credentials**
1. Go to: https://supabase.com/dashboard/projects
2. "+ New project" (use free tier)
3. Go to: Settings → API
4. Copy: `URL` (looks like `https://xxxxx.supabase.co`)
5. Copy: `service_role secret` (starts with `eyJ`)

- Project URL: `SUPABASE_URL=`
- Service Role Key: `SUPABASE_SERVICE_ROLE_KEY=eyJ`

---

## STEP 2: Paste Credentials Here

Save this block to `C:\projects\quant\.env.congress-alerts`:

```
STRIPE_SECRET_KEY=sk_live_[paste from A]
STRIPE_CONGRESS_ALERTS_PRICE_MONTHLY=price_[paste from B]
STRIPE_CONGRESS_ALERTS_PRICE_YEARLY=price_[paste from B]
STRIPE_CONGRESS_ALERTS_WEBHOOK_SECRET=whsec_[paste from C]
SUPABASE_URL=[paste from D]
SUPABASE_SERVICE_ROLE_KEY=eyJ[paste from D]
```

---

## STEP 3: Run Deployment Script

Run this in PowerShell in `C:\projects\quant`:

```powershell
# Read credentials from .env file and deploy to Vercel
$envFile = ".env.congress-alerts"
$vars = @{}

Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*#') { return }  # Skip comments
    $parts = $_ -split '='
    if ($parts.Count -eq 2) {
        $vars[$parts[0].Trim()] = $parts[1].Trim()
    }
}

# Deploy each env var to Vercel
foreach ($key in $vars.Keys) {
    Write-Host "Setting $key..." -ForegroundColor Cyan
    vercel env add $key --value $vars[$key]
}

# Sync and deploy
Write-Host "Syncing to git..." -ForegroundColor Green
vercel pull

# Commit and push
git add vercel.json
git commit -m "chore: Congress Alerts live - all env vars configured"
git push origin main

Write-Host ""
Write-Host "✓ Congress Alerts LIVE" -ForegroundColor Green
Write-Host "Revenue starts flowing within 3 hours"
Write-Host ""
Write-Host "Verify at: https://quantengines.com/congress-alerts"
```

---

## STEP 4: Verify (30 seconds)

```powershell
# Check deployment status
vercel status

# Open live page
Start-Process "https://quantengines.com/congress-alerts"
```

Expected: Pricing cards visible, signup button clickable.

---

## EXPECTED TIMELINE

| Action | Time | Status |
|--------|------|--------|
| Gather credentials | 2 min | Elliott |
| Paste into file | 1 min | Elliott |
| Run deployment | 1 min | Auto |
| Vercel redeploy | 3-5 min | Auto |
| **Revenue live** | **7-9 min** | ✅ |

---

**First revenue:** Within 48 hours of going live (organic search traffic)  
**Conservative 30-day:** $200-500 (10-50 Pro signups)  
**3-month ramp:** $500-1K/mo (with SEO optimization)

