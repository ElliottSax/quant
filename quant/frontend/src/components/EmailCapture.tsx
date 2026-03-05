'use client'

import { useState } from 'react'

interface EmailCaptureProps {
  site: 'credit' | 'calc' | 'affiliate' | 'quant'
  supabaseUrl: string
  headline: string
  subheading: string
  bgGradient: string
  theme: 'blue' | 'green' | 'orange' | 'purple'
}

export function EmailCapture({
  site,
  supabaseUrl,
  headline,
  subheading,
  bgGradient,
  theme,
}: EmailCaptureProps) {
  const [email, setEmail] = useState('')
  const [firstName, setFirstName] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('loading')

    try {
      const response = await fetch(`${supabaseUrl}/functions/v1/email-collection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.toLowerCase(),
          firstName: firstName || '',
          site,
        }),
      })

      const data = await response.json()

      if (response.ok || data.success) {
        setStatus('success')
        setEmail('')
        setFirstName('')
        setMessage('✅ Email saved! Thank you for subscribing.')
        setTimeout(() => setStatus('idle'), 3000)
      } else {
        setStatus('error')
        setMessage(data.error || 'Something went wrong')
      }
    } catch (error) {
      setStatus('error')
      setMessage('Failed to submit. Please try again.')
      console.error('Email submission error:', error)
    }
  }

  const colorMap = {
    blue: 'from-blue-600 to-blue-800',
    green: 'from-green-600 to-green-800',
    orange: 'from-orange-600 to-orange-800',
    purple: 'from-purple-600 to-purple-800',
  }

  const textColorMap = {
    blue: 'text-blue-100',
    green: 'text-green-100',
    orange: 'text-orange-100',
    purple: 'text-purple-100',
  }

  const buttonColorMap = {
    blue: 'hover:bg-blue-50 text-blue-600',
    green: 'hover:bg-green-50 text-green-600',
    orange: 'hover:bg-orange-50 text-orange-600',
    purple: 'hover:bg-purple-50 text-purple-600',
  }

  return (
    <div className={`bg-gradient-to-r ${colorMap[theme]} py-12 px-6 rounded-lg shadow-lg`}>
      <div className="max-w-2xl mx-auto">
        <h3 className="text-white text-3xl font-bold mb-3">{headline}</h3>

        <p className={`${textColorMap[theme]} mb-6 text-lg`}>{subheading}</p>

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
              className={`bg-white ${buttonColorMap[theme]} px-8 py-3 rounded font-bold disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap transition-colors`}
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
