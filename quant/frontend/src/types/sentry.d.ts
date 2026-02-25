/**
 * Type declarations for @sentry/nextjs
 *
 * This module is optionally used in the ErrorBoundary for production error reporting.
 * When @sentry/nextjs is not installed, the dynamic import gracefully falls back.
 */
declare module '@sentry/nextjs' {
  export function captureException(
    exception: unknown,
    captureContext?: {
      contexts?: Record<string, Record<string, unknown>>
      [key: string]: unknown
    }
  ): string
  export function init(options: Record<string, unknown>): void
}
