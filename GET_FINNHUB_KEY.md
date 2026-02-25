# Get Finnhub API Key - Step by Step

## 🚀 Quick Setup (2 minutes)

### Step 1: Sign Up for Finnhub (Free)

1. **Visit**: https://finnhub.io/register
2. **Fill out the form**:
   - Email address
   - Password
   - First/Last name
3. **Click**: "Create Account"
4. **Verify email**: Check your inbox and click the verification link

### Step 2: Get Your API Key

1. **Log in**: https://finnhub.io/dashboard
2. **Copy your API key** (shown on dashboard)
   - Format: `xxxxxxxxxxxxxxxxxxxxx`
   - Example: `cd5r9qhr01qvbnngqaa0cd5r9qhr01qvbnngqaag`

### Step 3: Add to Backend .env

**Location**: `/mnt/e/projects/quant/quant/backend/.env`

**Add this line**:
```bash
FINNHUB_API_KEY=your_actual_key_here
```

**Full example**:
```bash
# Existing config...
PROJECT_NAME=QuantBacktestingPlatform
VERSION=1.0.0
DATABASE_URL=sqlite+aiosqlite:///./quant.db
SECRET_KEY=ZGV2ZWxvcG1lbnRfa2V5X2Zvcl90ZXN0aW5nX29ubHlfbm90X3Byb2R1Y3Rpb25fdXNl

# ADD THIS:
FINNHUB_API_KEY=cd5r9qhr01qvbnngqaa0cd5r9qhr01qvbnngqaag
```

### Step 4: Verify It Works

**Test the API key**:
```bash
cd /mnt/e/projects/quant/quant/backend

# Test Finnhub status endpoint
curl http://localhost:8000/api/v1/finnhub/demo/status

# Expected response:
{
  "enabled": true,
  "api_key_configured": true,
  "base_url": "https://finnhub.io/api/v1",
  "rate_limit": "60 requests/minute (free tier)"
}
```

**Test a quote**:
```bash
curl http://localhost:8000/api/v1/finnhub/demo/quote/AAPL

# Expected: Real-time AAPL quote data
```

---

## 🎯 Free Tier Limits

- **60 requests per minute**
- **Unlimited API calls per month**
- **Real-time US stock quotes**
- **News & sentiment data**
- **Analyst recommendations**

**More than enough for development and early production!**

---

## ✅ Checklist

- [ ] Visit https://finnhub.io/register
- [ ] Create free account
- [ ] Verify email
- [ ] Copy API key from dashboard
- [ ] Add to `/mnt/e/projects/quant/quant/backend/.env`
- [ ] Test with curl (optional)
- [ ] Ready for deployment! 🚀

---

## 🚨 Important Notes

**DO NOT**:
- ❌ Commit API key to Git
- ❌ Share API key publicly
- ❌ Use in frontend code (keep it in backend only)

**DO**:
- ✅ Keep it in `.env` file (already in .gitignore)
- ✅ Add to Railway environment variables for production
- ✅ Rotate key if exposed

---

## 📝 Next Steps

Once you have your API key configured:

1. **Test locally** (optional)
2. **Add to Railway** (required for deployment)
3. **Deploy backend** → Task #8
4. **Deploy frontend** → Task #9
5. **Launch!** 🎉

---

**Status**: ⏳ Waiting for you to get API key
**Time**: 2 minutes
**Cost**: FREE (forever)
