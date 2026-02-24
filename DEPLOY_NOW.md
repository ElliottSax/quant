# 🚀 Deploy to Railway - Quick Start

Your stock prediction platform is **production-ready** and configured for Railway deployment!

---

## ⚡ Option 1: Automated Deployment (Recommended)

Run the deployment script:

```bash
cd /mnt/e/projects/quant
./deploy_to_railway.sh
```

The script will:
- ✅ Login to Railway
- ✅ Create/link project
- ✅ Add PostgreSQL database
- ✅ Generate secure keys
- ✅ Set environment variables
- ✅ Deploy your application
- ✅ Provide deployment URL

**Time**: ~5 minutes

---

## 📋 Option 2: Manual Deployment (Step-by-Step)

### 1. Login to Railway

```bash
cd /mnt/e/projects/quant/quant/backend
railway login
```

Your browser will open for authentication.

### 2. Create Project

```bash
railway init
```

- Project name: `quant-stock-prediction`
- Select: Create new project

### 3. Add PostgreSQL

```bash
railway add --database postgresql
```

### 4. Set Environment Variables

```bash
# Generate keys
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set JWT_SECRET_KEY=$(openssl rand -hex 32)

# Basic config
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set PROJECT_NAME="Quant Analytics Platform"
railway variables set API_V1_STR=/api/v1
railway variables set VERSION=1.0.0
railway variables set BACKEND_CORS_ORIGINS="http://localhost:3000"
```

### 5. Deploy

```bash
railway up
```

### 6. Run Migrations

```bash
railway run alembic upgrade head
```

### 7. Get Your URL

```bash
railway domain
```

---

## 🌐 After Deployment

Your API will be live at: `https://your-project.railway.app`

### Test It:

```bash
# Health check
curl https://your-project.railway.app/health

# API docs (open in browser)
https://your-project.railway.app/docs

# Register a user
curl -X POST https://your-project.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

---

## 💰 Cost

**Estimated**: $5-20/month
- Backend: ~$5/month
- PostgreSQL: ~$5-10/month
- Free tier: $5 credit/month included

---

## 📚 Resources

- **Full Guide**: `RAILWAY_DEPLOYMENT_STEPS.md`
- **Railway Docs**: https://docs.railway.app
- **Dashboard**: https://railway.app/dashboard

---

## 🐛 Troubleshooting

**Build fails?**
```bash
railway logs --build
```

**Server won't start?**
```bash
railway logs --tail
```

**Database issues?**
```bash
railway variables | grep DATABASE_URL
```

---

## ✅ Deployment Checklist

- [ ] Railway CLI installed (`railway --version`)
- [ ] Logged in to Railway (`railway whoami`)
- [ ] Project created/linked
- [ ] PostgreSQL database added
- [ ] Environment variables set
- [ ] Application deployed (`railway up`)
- [ ] Migrations run (`railway run alembic upgrade head`)
- [ ] Health check passing
- [ ] API docs accessible
- [ ] Authentication tested

---

## 🎯 Next Steps

1. **Test all endpoints** via `/docs`
2. **Add API keys** for market data providers
3. **Deploy frontend** to Vercel
4. **Update CORS** with frontend URL
5. **Set up monitoring** (Sentry)
6. **Add custom domain** (optional)

---

**Ready to deploy?** Run `./deploy_to_railway.sh` now! 🚀
