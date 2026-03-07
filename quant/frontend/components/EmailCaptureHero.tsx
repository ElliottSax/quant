'use client'

import { useState } from 'react'

/**
 * EmailCaptureHero Component - Quant Site (Purple Theme)
 * Integrated with Mautic at https://mautic-prod.onrender.com
 */

const MAUTIC_INSTANCE_URL = 'https://mautic-prod.onrender.com'
const FORM_ID = '4' // Quant form in Mautic

export function EmailCaptureHero() {
  const [email, setEmail] = useState('')
  const [firstName, setFirstName] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('loading')

    try {
      // Create FormData for Mautic
      const formData = new FormData()

      // Mautic field naming convention: mauticform[fieldName]
      formData.append('mauticform[email]', email)
      if (firstName) {
        formData.append('mauticform[firstName]', firstName)
      }
      formData.append('mauticform[formId]', FORM_ID)
      formData.append('mauticform[source]', 'quant')

      // Submit to Mautic form endpoint
      const response = await fetch(`${MAUTIC_INSTANCE_URL}/form/submit`, {
        method: 'POST',
        body: formData,
        credentials: 'omit',
      })

      // Mautic returns 200 even on duplicate emails
      if (response.ok || response.status === 200) {
        setStatus('success')
        setEmail('')
        setFirstName('')
        setMessage('✅ Check your email to confirm subscription!')

        // Track in GA4 if available
        if (typeof window !== 'undefined' && (window as any).gtag) {
          (window as any).gtag('event', 'email_signup', {
            source: 'quant',
            page_url: window.location.href
          })
        }

        // Reset form after 4 seconds
        setTimeout(() => {
          setStatus('idle')
          setMessage('')
        }, 4000)
      } else {
        setStatus('error')
        setMessage('Something went wrong. Please try again.')
        console.error('Mautic form submission error:', response.status)
      }
    } catch (error) {
      setStatus('error')
      setMessage('Failed to subscribe. Please check your connection and try again.')
      console.error('Form submission error:', error)
    }
  }

  return (
    <div className="bg-gradient-to-r from-purple-600 to-purple-800 py-12 px-6 rounded-lg shadow-lg">
      <div className="max-w-2xl mx-auto">
        <h3 className="text-white text-3xl font-bold mb-3">
          Get Weekly Trading Strategies
        </h3>

        <p className="text-purple-100 mb-6 text-lg">
          Join 5,000+ quant traders. Weekly strategies, backtesting insights, and market analysis.
        </p>

        {status === 'success' ? (
          <div className="bg-green-100 text-green-800 p-4 rounded-lg font-semibold">
            {message}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                placeholder="First name (optional)"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="flex-1 px-4 py-3 rounded font-semibold focus:outline-none focus:ring-2 focus:ring-purple-400 transition-all"
                disabled={status === 'loading'}
                maxLength={100}
              />

              <input
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 px-4 py-3 rounded font-semibold focus:outline-none focus:ring-2 focus:ring-purple-400 transition-all"
                required
                disabled={status === 'loading'}
              />
            </div>

            <button
              type="submit"
              className="bg-white text-purple-600 px-8 py-3 rounded font-bold hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap transition-colors"
              disabled={status === 'loading' || !email}
            >
              {status === 'loading' ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></span>
                  Subscribing...
                </span>
              ) : (
                'Subscribe Free'
              )}
            </button>
          </form>
        )}

        {status === 'error' && (
          <p className="text-red-200 mt-3 text-sm font-medium">{message}</p>
        )}
      </div>
    </div>
  )
}
