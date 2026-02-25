#!/bin/bash
# Programmatic deployment - Opens deployment pages automatically

echo "🚀 Opening Deployment Pages..."
echo "================================"
echo ""

# Deploy URLs
RAILWAY_URL="https://railway.app/new?template=https://github.com/ElliottSax/quant&plugins=postgresql&envs=PROJECT_NAME,VERSION,API_V1_STR,ENVIRONMENT,DATABASE_URL,FINNHUB_API_KEY,SECRET_KEY,JWT_SECRET_KEY,BACKEND_CORS_ORIGINS&PROJECT_NAMEDefault=QuantBacktestingPlatform&VERSIONDefault=1.0.0&API_V1_STRDefault=/api/v1&ENVIRONMENTDefault=production&DATABASE_URLDefault=sqlite+aiosqlite:///./quant.db&FINNHUB_API_KEYDefault=d6fl2j9r01qqnmbp36ogd6fl2j9r01qqnmbp36p0&BACKEND_CORS_ORIGINSDefault=[\"*\"]"

VERCEL_URL="https://vercel.com/new/clone?repository-url=https://github.com/ElliottSax/quant&project-name=quant-frontend&root-directory=quant/frontend&env=NEXT_PUBLIC_API_URL&envDescription=Backend%20API%20URL&envLink=https://github.com/ElliottSax/quant"

echo "📦 Step 1: Deploy Backend to Railway"
echo "URL: ${RAILWAY_URL:0:80}..."
echo ""

# Open Railway in browser
if command -v xdg-open &> /dev/null; then
    xdg-open "$RAILWAY_URL" &
elif command -v open &> /dev/null; then
    open "$RAILWAY_URL" &
elif command -v wslview &> /dev/null; then
    wslview "$RAILWAY_URL" &
else
    echo "⚠️  Could not auto-open browser. Please visit:"
    echo "$RAILWAY_URL"
fi

echo "✅ Railway deployment page opened in browser"
echo ""
echo "Instructions:"
echo "  1. Click 'Deploy Now'"
echo "  2. Wait 3-5 minutes for build"
echo "  3. Copy your Railway backend URL"
echo ""
read -p "Press Enter after Railway backend is deployed..."

echo ""
echo "🌐 Step 2: Deploy Frontend to Vercel"
echo "URL: ${VERCEL_URL:0:80}..."
echo ""

# Open Vercel in browser
if command -v xdg-open &> /dev/null; then
    xdg-open "$VERCEL_URL" &
elif command -v open &> /dev/null; then
    open "$VERCEL_URL" &
elif command -v wslview &> /dev/null; then
    wslview "$VERCEL_URL" &
else
    echo "⚠️  Could not auto-open browser. Please visit:"
    echo "$VERCEL_URL"
fi

echo "✅ Vercel deployment page opened in browser"
echo ""
echo "Instructions:"
echo "  1. Update NEXT_PUBLIC_API_URL with your Railway URL"
echo "  2. Click 'Deploy'"
echo "  3. Wait 2-3 minutes for build"
echo ""
read -p "Press Enter after Vercel frontend is deployed..."

echo ""
echo "================================"
echo "🎉 Deployment Complete!"
echo "================================"
echo ""
echo "Your app should now be live at:"
echo "  📊 Backend: https://your-project.railway.app"
echo "  🌐 Frontend: https://your-project.vercel.app"
echo "  📖 API Docs: https://your-project.railway.app/docs"
echo ""
echo "Next steps:"
echo "  1. Test your deployment"
echo "  2. Update CORS in Railway if needed"
echo "  3. Launch on Product Hunt!"
echo ""
