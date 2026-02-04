# Frontend Quick Start Guide

Get the QuantEngines frontend up and running in 5 minutes.

## Prerequisites

- Node.js 18+ installed
- Backend API running at `http://localhost:8000`

## Installation

```bash
# Navigate to frontend directory
cd /mnt/e/projects/quant/quant/frontend

# Install dependencies (if not already done)
npm install

# Create environment file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Available Pages

### Public Pages
- `http://localhost:3000/` - Home/Dashboard
- `http://localhost:3000/landing` - Landing page
- `http://localhost:3000/politicians` - Politicians list
- `http://localhost:3000/politicians/[id]` - Politician profile
- `http://localhost:3000/trades/[id]` - Trade details
- `http://localhost:3000/dashboard` - Main dashboard
- `http://localhost:3000/charts` - Charts
- `http://localhost:3000/discoveries` - ML discoveries

### Auth Pages
- `http://localhost:3000/auth/login` - Login
- `http://localhost:3000/auth/register` - Sign up
- `http://localhost:3000/auth/profile` - User profile (requires login)

## Quick Test

1. **Start the backend** (in another terminal):
   ```bash
   cd /mnt/e/projects/quant/quant/backend
   uvicorn app.main:app --reload
   ```

2. **Start the frontend**:
   ```bash
   cd /mnt/e/projects/quant/quant/frontend
   npm run dev
   ```

3. **Open browser**: `http://localhost:3000`

4. **Test features**:
   - View home page with ML predictions
   - Click "Politicians" to see list
   - Click on a politician to view profile
   - Try "Sign Up" to create an account
   - Login and view your profile

## Common Commands

```bash
# Development with hot reload
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

## Troubleshooting

### Port 3000 already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### API connection errors
1. Check backend is running: `http://localhost:8000/api/v1/docs`
2. Verify `.env.local` has correct API URL
3. Check browser console for CORS errors

### Module not found errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build errors
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

## Environment Variables

Create `.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Optional: Analytics
NEXT_PUBLIC_GA_ID=your-ga-id
```

## Production Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variable in Vercel dashboard
# NEXT_PUBLIC_API_URL=https://your-api.com/api/v1
```

### Docker

```bash
# Build
docker build -t quant-frontend .

# Run
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://your-api:8000/api/v1 quant-frontend
```

## Features Overview

### 🎨 Design
- Dark mode optimized
- Responsive (mobile-first)
- Modern UI with Tailwind CSS
- shadcn/ui components

### 🔐 Authentication
- JWT-based auth
- Login/Register pages
- Profile management
- Protected routes

### 📊 Data Visualization
- ECharts for complex charts
- Recharts for simple visualizations
- Interactive tooltips
- Real-time updates

### 🚀 Performance
- Server-side rendering
- Code splitting
- Image optimization
- Fast page loads

## Support

For issues or questions:
1. Check the main README.md
2. Review API documentation at `/api/v1/docs`
3. Check browser console for errors
4. Ensure backend is running

## What's Next?

1. Explore all pages
2. Test authentication
3. Try different data visualizations
4. Customize the styling
5. Add your own features

Happy coding!
