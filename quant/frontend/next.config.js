/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // API configuration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL + '/:path*',
      },
    ]
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Image domains (for external images)
  images: {
    domains: [],
  },

  // Security Headers
  // Implements defense-in-depth strategy against common web vulnerabilities
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN', // Prevent clickjacking attacks
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff', // Prevent MIME type sniffing
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block', // Enable XSS filter in browsers
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin', // Control referrer information
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()', // Disable unnecessary browser features
          },
          {
            key: 'Content-Security-Policy',
            value: [
              // Default: Only allow same-origin content
              "default-src 'self'",
              // Scripts: Allow self and inline scripts (required for Next.js)
              // In production, consider using nonces instead of 'unsafe-inline'
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
              // Styles: Allow self and inline styles (required for styled-components, Tailwind)
              "style-src 'self' 'unsafe-inline'",
              // Images: Allow self, data URLs, and external image CDNs
              "img-src 'self' data: https:",
              // Fonts: Allow self and data URLs
              "font-src 'self' data:",
              // Connect: Allow API calls to backend
              `connect-src 'self' ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'} https:`,
              // Frame: Only allow same-origin iframes
              "frame-src 'self'",
              // Media: Only allow same-origin media
              "media-src 'self'",
              // Object: Block plugins (Flash, etc.)
              "object-src 'none'",
              // Base: Restrict base tag
              "base-uri 'self'",
              // Form actions: Only allow same-origin form submissions
              "form-action 'self'",
              // Frame ancestors: Prevent embedding in iframes (redundant with X-Frame-Options)
              "frame-ancestors 'self'",
              // Upgrade insecure requests in production
              process.env.NODE_ENV === 'production' ? 'upgrade-insecure-requests' : '',
            ]
              .filter(Boolean)
              .join('; '),
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
