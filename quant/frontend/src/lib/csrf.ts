/**
 * CSRF Protection Utilities
 *
 * Implements Cross-Site Request Forgery (CSRF) protection for forms and API requests.
 *
 * Security Strategy:
 * - Double Submit Cookie pattern
 * - Token stored in httpOnly cookie (backend sets this)
 * - Token also included in request headers
 * - Backend validates both match
 *
 * Usage:
 * - Call getCSRFToken() to get current token
 * - Use withCSRFToken() to add token to fetch requests
 * - Use CSRFProtectedForm component for forms
 */

'use client'

const CSRF_COOKIE_NAME = 'csrftoken'
const CSRF_HEADER_NAME = 'X-CSRF-Token'

/**
 * Get CSRF token from cookie
 */
export function getCSRFToken(): string | null {
  if (typeof document === 'undefined') return null

  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === CSRF_COOKIE_NAME) {
      return decodeURIComponent(value)
    }
  }
  return null
}

/**
 * Generate a random CSRF token
 * Used when backend hasn't set one yet
 */
export function generateCSRFToken(): string {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, (byte) => byte.toString(16).padStart(2, '0')).join('')
}

/**
 * Set CSRF token in cookie (client-side fallback)
 * Note: Backend should set httpOnly cookie for production
 */
export function setCSRFToken(token: string) {
  if (typeof document === 'undefined') return

  // Set cookie with secure flags
  const isProduction = process.env.NODE_ENV === 'production'
  const cookieOptions = [
    `${CSRF_COOKIE_NAME}=${encodeURIComponent(token)}`,
    'path=/',
    'SameSite=Strict',
    isProduction ? 'Secure' : '',
  ]
    .filter(Boolean)
    .join('; ')

  document.cookie = cookieOptions
}

/**
 * Ensure CSRF token exists, generate if needed
 */
export function ensureCSRFToken(): string {
  let token = getCSRFToken()

  if (!token) {
    token = generateCSRFToken()
    setCSRFToken(token)
  }

  return token
}

/**
 * Add CSRF token to fetch request options
 */
export function withCSRFToken(options: RequestInit = {}): RequestInit {
  const token = ensureCSRFToken()

  return {
    ...options,
    headers: {
      ...options.headers,
      [CSRF_HEADER_NAME]: token,
    },
    credentials: 'include', // Include cookies in request
  }
}

/**
 * CSRF-protected fetch wrapper
 */
export async function csrfFetch(url: string, options: RequestInit = {}): Promise<Response> {
  // Only add CSRF token for state-changing methods
  const method = options.method?.toUpperCase() || 'GET'
  const needsCSRF = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)

  const requestOptions = needsCSRF ? withCSRFToken(options) : options

  return fetch(url, requestOptions)
}

/**
 * React hook for CSRF token
 */
export function useCSRFToken() {
  const token = ensureCSRFToken()

  return {
    token,
    headers: {
      [CSRF_HEADER_NAME]: token,
    },
  }
}

/**
 * CSRF-protected form component
 */
import { FormEvent, ReactNode } from 'react'

interface CSRFProtectedFormProps {
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
  children: ReactNode
  className?: string
  method?: 'POST' | 'PUT' | 'PATCH' | 'DELETE'
}

export function CSRFProtectedForm({
  onSubmit,
  children,
  className,
  method = 'POST',
}: CSRFProtectedFormProps) {
  const token = ensureCSRFToken()

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    // Ensure token is fresh
    ensureCSRFToken()
    onSubmit(event)
  }

  return (
    <form onSubmit={handleSubmit} className={className} method={method}>
      {/* Hidden CSRF token field for non-AJAX submissions */}
      <input type="hidden" name="csrf_token" value={token} />
      {children}
    </form>
  )
}

/**
 * Validate CSRF token format (client-side validation)
 */
export function isValidCSRFToken(token: string): boolean {
  // Token should be 64 hex characters
  return /^[0-9a-f]{64}$/i.test(token)
}

/**
 * Clear CSRF token (for logout, etc.)
 */
export function clearCSRFToken() {
  if (typeof document === 'undefined') return

  document.cookie = `${CSRF_COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`
}
