/**
 * 404 Not Found Page
 */

import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <div className="text-center max-w-2xl mx-auto px-4">
        {/* Animated 404 */}
        <div className="relative mb-8">
          <h1 className="text-[150px] md:text-[200px] font-bold leading-none text-gradient-blue opacity-20 select-none">
            404
          </h1>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full bg-gradient-to-br from-primary/20 to-purple-500/20 blur-3xl animate-pulse" />
          </div>
        </div>

        {/* Content */}
        <div className="glass-strong rounded-2xl p-12 border border-border/50 animate-fade-in">
          <div className="mb-6">
            <svg
              className="w-20 h-20 mx-auto text-primary mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          <h2 className="text-3xl md:text-4xl font-bold mb-4">Page Not Found</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-lg mx-auto">
            The page you're looking for doesn't exist or has been moved.
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/" className="btn-primary">
              <span className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                  />
                </svg>
                Go Home
              </span>
            </Link>

            <Link href="/dashboard" className="btn-secondary">
              <span className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
                View Dashboard
              </span>
            </Link>
          </div>

          {/* Popular Links */}
          <div className="mt-12 pt-8 border-t border-border/50">
            <p className="text-sm font-semibold text-muted-foreground mb-4">
              Popular Pages
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link
                href="/politicians"
                className="text-sm text-primary hover:underline"
              >
                Politicians
              </Link>
              <span className="text-muted-foreground">•</span>
              <Link
                href="/signals"
                className="text-sm text-primary hover:underline"
              >
                Trading Signals
              </Link>
              <span className="text-muted-foreground">•</span>
              <Link
                href="/backtesting"
                className="text-sm text-primary hover:underline"
              >
                Backtesting
              </Link>
              <span className="text-muted-foreground">•</span>
              <Link
                href="/discoveries"
                className="text-sm text-primary hover:underline"
              >
                Discoveries
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
