# QuantEngines Frontend

Modern Next.js 14+ frontend for the QuantEngines congressional trading analytics platform.

## Features

- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- shadcn/ui components
- React Query for data fetching
- Zustand for state management
- Recharts & ECharts for visualizations
- Responsive mobile-first design
- Authentication system
- Dark mode optimized

## Pages

### Public Pages
- `/` - Home page with ML predictions and discoveries
- `/landing` - Marketing landing page with features and pricing
- `/politicians` - Browse all politicians
- `/politicians/[id]` - Individual politician profile
- `/trades/[id]` - Trade detail page
- `/dashboard` - Main analytics dashboard
- `/charts` - Technical analysis charts
- `/discoveries` - ML pattern discoveries
- `/network` - Correlation network visualization

### Auth Pages
- `/auth/login` - User login
- `/auth/register` - User registration
- `/auth/profile` - User profile management

## Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── auth/              # Authentication pages
│   ├── politicians/       # Politician pages
│   ├── trades/            # Trade pages
│   ├── dashboard/         # Dashboard
│   ├── landing/           # Landing page
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── charts/           # Chart components
│   └── Navigation.tsx    # Main navigation
└── lib/                  # Utilities and helpers
    ├── api.ts           # API client
    ├── utils.ts         # Utility functions
    ├── hooks.ts         # Custom React hooks
    └── providers.tsx    # Context providers
```

## Key Technologies

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality UI components
- **React Query**: Data fetching and caching
- **Zustand**: Lightweight state management
- **Recharts**: Composable charting library
- **ECharts**: Advanced data visualization

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000/api/v1`.

Key API endpoints:
- `GET /politicians` - List politicians
- `GET /politicians/{id}` - Get politician details
- `GET /trades` - List trades
- `GET /trades/{id}` - Get trade details
- `GET /stats/leaderboard` - Get performance leaderboard
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

## Features

### Authentication
- User registration and login
- JWT token-based auth
- Protected routes
- Profile management

### Dashboard
- Real-time politician trading data
- ML prediction insights
- Performance metrics
- Interactive charts

### Politician Profiles
- Detailed trading history
- Performance statistics
- Trade distribution charts
- Top holdings

### Trade Details
- Complete transaction information
- Related trades
- Timeline visualization

### Responsive Design
- Mobile-first approach
- Optimized for all screen sizes
- Touch-friendly interfaces
- Progressive enhancement

## Development

```bash
# Run dev server with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build
docker build -t quant-frontend .

# Run
docker run -p 3000:3000 quant-frontend
```

## Performance Optimizations

- Server-side rendering (SSR)
- Static generation where possible
- Image optimization
- Code splitting
- Lazy loading
- CDN for static assets

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

Proprietary - All rights reserved
