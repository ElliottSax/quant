'use client'

import { useState } from 'react'
import { createClient } from '@supabase/supabase-js'

// Supabase client (shared with other sites)
const supabase = createClient(
  'https://jznljskfvhlqlshofkvd.supabase.co',
  'sb_publishable_HQPHIEY5M1dnQFbNJEO0nw_1YQjr46l'
)

export function EmailCaptureHero() {
  const [email, setEmail] = useState('')
  const [firstName, setFirstName] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('loading')

    try {
      const { error: insertError } = await supabase
        .from('email_subscribers')
        .insert([
          {
            email: email.toLowerCase(),
            first_name: firstName || null,
            source: 'quant',
          }
        ])

      if (insertError) {
        if (insertError.code === '23505') {
          setStatus('error')
          setMessage('This email is already subscribed!')
        } else {
          throw insertError
        }
      } else {
        setStatus('success')
        setEmail('')
        setFirstName('')
        setMessage('✅ Email saved! Thank you for subscribing.')

        // Track in GA4 if available
        if (typeof window !== 'undefined' && (window as any).gtag) {
          (window as any).gtag('event', 'email_signup', {
            source: 'quant',
            page_url: window.location.href
          })
        }

        setTimeout(() => setStatus('idle'), 3000)
      }
    } catch (error) {
      setStatus('error')
      setMessage('Failed to submit. Please try again.')
      console.error('Email submission error:', error)
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
                className="flex-1 px-4 py-3 rounded font-semibold focus:outline-none focus:ring-2 focus:ring-white transition-all"
                disabled={status === 'loading'}
                maxLength={50}
              />

              <input
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 px-4 py-3 rounded font-semibold focus:outline-none focus:ring-2 focus:ring-white transition-all"
                required
                disabled={status === 'loading'}
              />
            </div>

            <button
              type="submit"
              className="bg-white text-purple-600 px-8 py-3 rounded font-bold hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap transition-colors"
              disabled={status === 'loading' || !email}
            >
              {status === 'loading' ? 'Saving...' : 'Subscribe Free'}
            </button>
          </form>
        )}

        {status === 'error' && <p className="text-red-200 mt-3 text-sm font-medium">{message}</p>}
      </div>
    </div>
  )
}
