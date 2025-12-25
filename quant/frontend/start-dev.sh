#!/bin/bash

# Frontend Development Server Startup Script
# This script starts the Next.js development server with proper error handling

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Quant Analytics Platform - Frontend Dev Server         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found"
    echo "Please run this script from the frontend directory:"
    echo "  cd /mnt/e/projects/quant/quant/frontend"
    echo "  ./start-dev.sh"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

echo "🚀 Starting Next.js development server..."
echo ""
echo "⏳ First-time compilation takes 5-7 minutes"
echo "   Subsequent starts will be much faster (~30 seconds)"
echo ""
echo "📍 Server will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the development server
npx next dev
