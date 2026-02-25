#!/bin/bash
# Quick authentication script for Railway and Vercel
# Run this ONCE before using deploy.sh

echo "🔐 Authentication Setup"
echo "======================="
echo ""
echo "This will open your browser to authenticate with:"
echo "  1. Railway (backend hosting)"
echo "  2. Vercel (frontend hosting)"
echo ""
read -p "Press Enter to continue..."

# Railway login
echo ""
echo "📦 Step 1: Railway Login"
echo "------------------------"
echo "A browser window will open. Log in with your Railway account."
echo ""
railway login

if railway whoami &>/dev/null; then
    echo "✅ Railway authentication successful!"
else
    echo "❌ Railway authentication failed. Please try again."
    exit 1
fi

# Vercel login
echo ""
echo "🌐 Step 2: Vercel Login"
echo "----------------------"
echo "A browser window will open. Log in with your Vercel account."
echo ""
vercel login

if vercel whoami &>/dev/null; then
    echo "✅ Vercel authentication successful!"
else
    echo "❌ Vercel authentication failed. Please try again."
    exit 1
fi

echo ""
echo "✅ Authentication Complete!"
echo ""
echo "You can now run: ./deploy.sh"
echo ""
