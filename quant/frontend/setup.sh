#!/bin/bash

# QuantEngines Frontend Setup Script
# Automates the setup process for the Next.js frontend

set -e

echo "=================================="
echo "QuantEngines Frontend Setup"
echo "=================================="
echo ""

# Check Node.js version
echo "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please install Node.js 18+."
    exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo ""

# Install dependencies
echo "Installing dependencies..."
if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi
echo ""

# Create .env.local if it doesn't exist
echo "Setting up environment variables..."
if [ ! -f ".env.local" ]; then
    cat > .env.local << EOF
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Optional: Add other environment variables here
# NEXT_PUBLIC_GA_ID=your-google-analytics-id
EOF
    echo "✅ Created .env.local"
else
    echo "✅ .env.local already exists"
fi
echo ""

# Check if backend is running
echo "Checking backend connection..."
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "⚠️  Backend is not running. Start it with:"
    echo "   cd ../backend && uvicorn app.main:app --reload"
fi
echo ""

# Build check
echo "Verifying build..."
if npm run build > /dev/null 2>&1; then
    echo "✅ Build successful"
else
    echo "⚠️  Build failed. Run 'npm run build' to see errors."
fi
echo ""

echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the development server:"
echo "   npm run dev"
echo ""
echo "2. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "3. (Optional) Start the backend if not running:"
echo "   cd ../backend && uvicorn app.main:app --reload"
echo ""
echo "Available pages:"
echo "  - Home: http://localhost:3000/"
echo "  - Landing: http://localhost:3000/landing"
echo "  - Politicians: http://localhost:3000/politicians"
echo "  - Login: http://localhost:3000/auth/login"
echo "  - Register: http://localhost:3000/auth/register"
echo ""
echo "For more info, see QUICKSTART.md"
echo ""
