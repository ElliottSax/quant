# Deploy Frontend to Vercel - Step by Step

## 🚀 Vercel Deployment (5 minutes)

Vercel is the best platform for Next.js apps. Free tier includes:
- ✅ Unlimited deployments
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Preview deployments
- ✅ Custom domains

---

## Prerequisites

- [ ] GitHub account
- [ ] Vercel account (sign up at vercel.com)
- [ ] Backend deployed to Railway (Task #8)
- [ ] Railway backend URL (e.g., `https://quant-backend.railway.app`)

---

## Method 1: Vercel CLI (Fastest)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

Enter your email and verify.

### Step 3: Deploy

```bash
cd /mnt/e/projects/quant/quant/frontend

# Deploy to Vercel
vercel

# Answer prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? quant-frontend
# - Directory? ./
# - Override settings? No

# Deploy to production
vercel --prod
```

### Step 4: Add Environment Variables

```bash
# Add backend API URL
vercel env add NEXT_PUBLIC_API_URL

# Enter value: https://your-backend.railway.app/api/v1
# Environment: Production

# Redeploy with new env var
vercel --prod
```

### Step 5: Get Your URL

```bash
# Your app is live at:
https://quant-frontend.vercel.app
```

---

## Method 2: Vercel Web Interface (Recommended)

### Step 1: Push Frontend to GitHub

```bash
cd /mnt/e/projects/quant/quant/frontend

# If separate repo
git init
git add .
git commit -m "feat: Add portfolio backtesting UI"
gh repo create quant-frontend --public --source=. --push

# Or if monorepo, ensure frontend is in quant/frontend/
```

### Step 2: Import to Vercel

1. **Visit**: https://vercel.com/new
2. **Click**: "Import Git Repository"
3. **Select**: Your `quant` repository
4. **Configure**:
   - **Root Directory**: `quant/frontend`
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Step 3: Add Environment Variables

Click "Environment Variables" and add:

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
```

**Important**: Replace `your-backend.railway.app` with your actual Railway URL!

### Step 4: Deploy

1. **Click**: "Deploy"
2. **Wait**: 2-3 minutes for build
3. **Done**: Your app is live!

### Step 5: Get Your URL

Vercel assigns a URL like:
- **Production**: `https://quant-frontend.vercel.app`
- **Preview** (per commit): `https://quant-frontend-git-main.vercel.app`

---

## Method 3: One-Click Deploy

**Add this button to your GitHub README**:

```markdown
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/quant&project-name=quant-frontend&root-directory=quant/frontend)
```

---

## 🔧 Configuration

### vercel.json

Already exists at `/mnt/e/projects/quant/vercel.json`:

```json
{
  "buildCommand": "cd quant/frontend && npm run build",
  "devCommand": "cd quant/frontend && npm run dev",
  "installCommand": "cd quant/frontend && npm install",
  "framework": "nextjs",
  "outputDirectory": "quant/frontend/.next"
}
```

**No changes needed!**

### next.config.js

Located at `/mnt/e/projects/quant/quant/frontend/next.config.js`

Should have:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // For optimized builds
  reactStrictMode: true,
  swcMinify: true,
}

module.exports = nextConfig
```

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain

1. **Vercel Dashboard** → Your Project → "Settings" → "Domains"
2. **Add Domain**: `quant.yourdomain.com`
3. **Configure DNS**:

**If using Cloudflare/other DNS**:
```
Type: CNAME
Name: quant
Value: cname.vercel-dns.com
```

**If using Vercel DNS**:
Vercel will manage it automatically

4. **Wait**: 1-2 minutes for DNS propagation
5. **Done**: Your app is live at `https://quant.yourdomain.com`

---

## 🔗 Connect Frontend to Backend

### Update CORS in Railway Backend

```bash
# In Railway dashboard, update BACKEND_CORS_ORIGINS:
BACKEND_CORS_ORIGINS=["https://quant-frontend.vercel.app","https://quant.yourdomain.com"]

# Or via CLI:
railway variables set BACKEND_CORS_ORIGINS='["https://quant-frontend.vercel.app"]'
```

### Test Connection

1. **Visit**: `https://quant-frontend.vercel.app`
2. **Navigate**: Portfolio Backtesting page
3. **Add symbols**: AAPL, MSFT, GOOGL
4. **Run backtest**: Should fetch from Railway backend
5. **Check**: Network tab shows API calls to Railway

---

## 🎨 Preview Deployments

Every Git push creates a preview deployment:

1. **Push to branch**:
   ```bash
   git checkout -b feature/new-visualization
   git add .
   git commit -m "Add correlation heatmap"
   git push origin feature/new-visualization
   ```

2. **Vercel auto-deploys**:
   - Preview URL: `https://quant-frontend-git-feature-new-viz.vercel.app`
   - Comment on PR with preview link

3. **Merge to main**:
   - Auto-deploys to production
   - Updates `https://quant-frontend.vercel.app`

---

## 🚨 Troubleshooting

### Issue: Build fails with "Module not found"

**Solution**: Check dependencies
```bash
cd quant/frontend
npm install
npm run build  # Test locally first
```

### Issue: API calls fail (404/CORS)

**Solution 1**: Check `NEXT_PUBLIC_API_URL`
```bash
# Vercel dashboard → Settings → Environment Variables
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
```

**Solution 2**: Update CORS in backend
```bash
railway variables set BACKEND_CORS_ORIGINS='["https://your-frontend.vercel.app"]'
```

### Issue: Environment variables not updating

**Solution**: Redeploy after changing env vars
```bash
vercel --prod

# Or in Vercel dashboard:
# Deployments → Latest → Redeploy
```

### Issue: Page 404 on refresh

**Solution**: Already handled by Next.js routing, but verify `next.config.js`:
```javascript
{
  output: 'standalone',
  trailingSlash: false,
}
```

### Issue: Slow page loads

**Solution**: Enable static optimization
```bash
# In package.json:
"scripts": {
  "build": "next build && next export"  # For static pages
}
```

---

## ✅ Deployment Checklist

**Pre-deployment**:
- [ ] Backend deployed and URL noted
- [ ] Code pushed to GitHub
- [ ] Vercel account created

**Deployment**:
- [ ] Imported repo to Vercel
- [ ] Root directory set: `quant/frontend`
- [ ] Framework: Next.js selected
- [ ] Environment variables added:
  - [ ] `NEXT_PUBLIC_API_URL`
- [ ] First deployment successful

**Post-deployment**:
- [ ] Frontend URL noted
- [ ] Backend CORS updated with frontend URL
- [ ] Test: Portfolio backtesting page works
- [ ] Test: API calls to backend succeed
- [ ] Custom domain added (optional)
- [ ] Preview deployments working

---

## 📊 Vercel Free Tier Limits

**Generous limits**:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth per month
- ✅ 100 serverless function invocations/day
- ✅ Automatic SSL
- ✅ Global CDN

**Estimated usage**:
- Small traffic: FREE
- Medium traffic (10K visits/month): FREE
- High traffic (100K+ visits/month): May need Pro ($20/month)

**Upgrade when needed**:
- **Pro**: $20/month (unlimited everything)

---

## 🎯 Performance Optimization

### Enable Static Generation

For pages that don't change often:

```typescript
// app/page.tsx
export const dynamic = 'force-static'
```

### Enable Image Optimization

Already configured via Next.js Image component.

### Enable Edge Functions (Optional)

For ultra-fast API routes:

```typescript
// app/api/route.ts
export const runtime = 'edge'
```

### Monitor Performance

Vercel automatically provides:
- **Analytics**: Dashboard → Analytics
- **Speed Insights**: Real user metrics
- **Web Vitals**: Core performance metrics

---

## 🔗 Useful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Vercel Docs**: https://vercel.com/docs
- **Next.js Deployment**: https://nextjs.org/docs/deployment
- **Environment Variables**: Dashboard → Settings → Environment Variables
- **Domain Settings**: Dashboard → Settings → Domains
- **Analytics**: Dashboard → Analytics

---

## 🎉 Post-Deployment

After successful deployment:

1. **Test all pages**:
   - Landing page: `/`
   - Single backtest: `/backtesting`
   - Portfolio backtest: `/backtesting/portfolio`
   - Dashboard: `/dashboard`

2. **Test all features**:
   - Symbol selection
   - Portfolio optimization
   - Backtest execution
   - Results visualization
   - Finnhub integration (if key added)

3. **Share URLs**:
   - Frontend: `https://quant-frontend.vercel.app`
   - API: `https://quant-backend.railway.app`
   - API Docs: `https://quant-backend.railway.app/docs`

4. **Update README** with live links

5. **Create marketing materials** (Task #10)

---

## 📱 Mobile Testing

Vercel provides automatic mobile optimization, but test:

1. **Responsive design**: Open DevTools → Device toolbar
2. **Touch interactions**: Test on actual phone
3. **Performance**: Check load times on mobile
4. **PWA** (optional): Add manifest.json for installable app

---

## 🚀 Continuous Deployment

**Automatic deployments**:
- Push to `main` → Production deploy
- Push to any branch → Preview deploy
- PR created → Preview deploy with comment

**Manual deployments**:
```bash
vercel --prod  # Deploy to production
vercel         # Deploy to preview
```

---

**Status**: ⏳ Ready to deploy
**Time**: 5 minutes
**Cost**: FREE (Vercel free tier)
**Next**: Create marketing materials (Task #10)
