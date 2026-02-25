/**
 * Error Page
 * Displays when an error occurs in the application
 */

'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <div className="text-center max-w-2xl mx-auto px-4">
        {/* Error Icon */}
        <div className="mb-8 relative">
          <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-red-500/10 border-4 border-red-500/20 animate-pulse">
            <svg
              className="w-16 h-16 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <div className="absolute inset-0 -z-10">
            <div className="w-full h-full rounded-full bg-gradient-to-br from-red-500/20 to-orange-500/20 blur-3xl" />
          </div>
        </div>

        {/* Content */}
        <div className="glass-strong rounded-2xl p-12 border border-border/50 animate-fade-in">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Something Went Wrong</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-lg mx-auto">
            We encountered an unexpected error. Our team has been notified and is working on a fix.
          </p>

          {/* Error Details (Development Only) */}
          {process.env.NODE_ENV === 'development' && error.message && (
            <div className="mb-8 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-left">
              <p className="text-sm font-mono text-red-500 break-all">
                {error.message}
              </p>
              {error.digest && (
                <p className="text-xs text-muted-foreground mt-2">
                  Error ID: {error.digest}
                </p>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => reset()}
              className="btn-primary"
            >
              <span className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Try Again
              </span>
            </button>

            <button
              onClick={() => window.location.href = '/'}
              className="btn-secondary"
            >
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
            </button>
          </div>

          {/* Help Text */}
          <div className="mt-12 pt-8 border-t border-border/50">
            <p className="text-sm text-muted-foreground">
              If this problem persists, please{' '}
              <button
                onClick={() => window.location.reload()}
                className="text-primary hover:underline font-medium"
              >
                refresh the page
              </button>{' '}
              or contact support.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
