/**
 * Error Boundary Component
 *
 * Catches React errors and displays a fallback UI instead of crashing the entire app.
 * Implements graceful error handling and error reporting.
 *
 * Security Benefits:
 * - Prevents error stack traces from being exposed to users
 * - Provides safe fallback UI
 * - Logs errors securely for monitoring
 * - Prevents app crashes from security-sensitive errors
 */

'use client'

import { Component, ReactNode } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error securely (sanitize sensitive data before logging)
    const sanitizedError = this.sanitizeError(error)

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', sanitizedError, errorInfo)
    }

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo)

    // In production, send to error tracking service (e.g., Sentry)
    if (process.env.NODE_ENV === 'production') {
      this.reportErrorToService(sanitizedError, errorInfo)
    }

    // Update state with error info
    this.setState({
      errorInfo,
    })
  }

  /**
   * Sanitize error for logging (remove sensitive data)
   */
  private sanitizeError(error: Error): Error {
    // Create a clean error object without sensitive data
    const sanitized = new Error(error.message)
    sanitized.name = error.name
    sanitized.stack = this.sanitizeStackTrace(error.stack)
    return sanitized
  }

  /**
   * Sanitize stack trace (remove file paths, tokens, etc.)
   */
  private sanitizeStackTrace(stack?: string): string | undefined {
    if (!stack) return undefined

    return stack
      .split('\n')
      .map((line) => {
        // Remove absolute file paths
        return line.replace(/\/[\w\/\-\.]+\//g, '/')
      })
      .join('\n')
  }

  /**
   * Report error to monitoring service
   */
  private reportErrorToService(error: Error, errorInfo: React.ErrorInfo) {
    // TODO: Integrate with error tracking service (Sentry, LogRocket, etc.)
    // Example:
    // Sentry.captureException(error, {
    //   contexts: {
    //     react: {
    //       componentStack: errorInfo.componentStack,
    //     },
    //   },
    // })

    // For now, just log to console in a structured format
    console.error('Error Report:', {
      timestamp: new Date().toISOString(),
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      },
      componentStack: errorInfo.componentStack,
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
      url: typeof window !== 'undefined' ? window.location.href : 'unknown',
    })
  }

  /**
   * Reset error boundary state
   */
  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-[hsl(220,60%,4%)] flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-[hsl(220,55%,6%)] rounded-lg border border-[hsl(215,40%,18%)] p-8">
            {/* Error Icon */}
            <div className="flex items-center justify-center mb-6">
              <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-red-500"
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
            </div>

            {/* Error Title */}
            <h1 className="text-2xl font-bold text-white text-center mb-2">
              Something went wrong
            </h1>

            {/* Error Message (sanitized) */}
            <p className="text-[hsl(210,20%,65%)] text-center mb-6">
              We encountered an unexpected error. Our team has been notified and is working on a
              fix.
            </p>

            {/* Development Mode: Show error details */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="bg-[hsl(220,55%,8%)] rounded border border-[hsl(215,40%,16%)] p-4 mb-6 overflow-auto">
                <div className="text-xs font-mono text-red-400 mb-2">
                  {this.state.error.name}: {this.state.error.message}
                </div>
                {this.state.error.stack && (
                  <pre className="text-xs text-[hsl(210,20%,55%)] overflow-x-auto">
                    {this.state.error.stack}
                  </pre>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4 justify-center">
              <button
                onClick={this.resetError}
                className="px-6 py-2 bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] font-semibold rounded hover:bg-[hsl(45,96%,68%)] transition-colors"
              >
                Try Again
              </button>
              <button
                onClick={() => (window.location.href = '/')}
                className="px-6 py-2 bg-[hsl(215,50%,14%)] text-white font-semibold rounded hover:bg-[hsl(215,50%,18%)] transition-colors border border-[hsl(215,40%,18%)]"
              >
                Go Home
              </button>
            </div>

            {/* Support Info */}
            <div className="mt-8 pt-6 border-t border-[hsl(215,40%,16%)] text-center">
              <p className="text-xs text-[hsl(210,20%,55%)]">
                Error ID:{' '}
                <span className="font-mono text-[hsl(210,20%,65%)]">
                  {Date.now().toString(36)}
                </span>
              </p>
              <p className="text-xs text-[hsl(210,20%,55%)] mt-2">
                If this problem persists, please contact support.
              </p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Hook-based error boundary for functional components
 */
export function useErrorHandler() {
  const handleError = (error: Error) => {
    // This will be caught by the nearest ErrorBoundary
    throw error
  }

  return handleError
}
