'use client'

import { useState, useEffect, useCallback } from 'react'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://jznljskfvhlqlshofkvd.supabase.co',
  'sb_publishable_HQPHIEY5M1dnQFbNJEO0nw_1YQjr46l'
)

function getPageContent() {
  if (typeof window === 'undefined') return null
  const path = window.location.pathname

  if (path.startsWith('/politicians') || path.startsWith('/congressional') || path.startsWith('/dashboard')) {
    return {
      headline: 'Get Congressional Trade Alerts',
      subtitle: 'Be the first to know when Congress members buy or sell stocks. Free email alerts with full trade details.',
      benefits: [
        'Real-time alerts when politicians file trades',
        'Performance tracking vs. S&P 500',
        'Unusual activity flags & pattern detection',
      ],
      buttonText: 'Get Free Trade Alerts',
      successMessage: 'your congressional trade alerts',
      source: 'exit_intent_congressional',
    }
  }
  if (path.startsWith('/backtesting') || path.startsWith('/strategies')) {
    return {
      headline: 'Save Your Backtest Results',
      subtitle: 'Get your backtest results emailed to you, plus weekly strategy updates and new template alerts.',
      benefits: [
        'Backtest results summary emailed to you',
        'New strategy template notifications',
        'Weekly performance updates on popular strategies',
      ],
      buttonText: 'Save & Get Updates',
      successMessage: 'your backtest results and strategy updates',
      source: 'exit_intent_backtesting',
    }
  }
  if (path.startsWith('/blog') || path.startsWith('/resources') || path.startsWith('/learn')) {
    return {
      headline: 'Weekly Quant Trading Insights',
      subtitle: 'Get data-driven trading analysis, strategy breakdowns, and market signals delivered every week.',
      benefits: [
        'Quantitative market analysis every Monday',
        'Strategy deep-dives with real backtest data',
        'Anomaly detection alerts & trade ideas',
      ],
      buttonText: 'Get Weekly Insights',
      successMessage: 'your weekly quant insights',
      source: 'exit_intent_blog',
    }
  }
  return null
}

const defaultContent = {
  headline: 'Free Quant Trading Alerts',
  subtitle: 'Congressional trade alerts, strategy updates, and weekly quant insights. No spam, unsubscribe anytime.',
  benefits: [
    'Congressional stock trade alerts',
    'New backtesting strategies & templates',
    'Weekly data-driven market analysis',
  ],
  buttonText: 'Get Free Alerts',
  successMessage: 'your trading alerts setup',
  source: 'exit_intent_default',
}

export function ExitIntentPopup() {
  const [isVisible, setIsVisible] = useState(false)
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const content = getPageContent() || defaultContent

  useEffect(() => {
    const shown = sessionStorage.getItem('qe_exit_intent_shown')
    if (shown) return

    let triggered = false

    const handleMouseLeave = (e: MouseEvent) => {
      if (e.clientY <= 0 && !triggered) {
        triggered = true
        setIsVisible(true)
        sessionStorage.setItem('qe_exit_intent_shown', 'true')
      }
    }

    // Delay activation to avoid false positives on page load
    const timer = setTimeout(() => {
      document.addEventListener('mouseleave', handleMouseLeave)
    }, 5000)

    return () => {
      clearTimeout(timer)
      document.removeEventListener('mouseleave', handleMouseLeave)
    }
  }, [])

  const handleClose = useCallback(() => {
    setIsVisible(false)
  }, [])

  // Escape key handler
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isVisible) handleClose()
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isVisible, handleClose])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const { error: insertError } = await supabase
        .from('email_subscribers')
        .insert([{
          email: email.toLowerCase(),
          source: content.source,
        }])

      if (insertError) {
        if (insertError.code === '23505') {
          setError('This email is already subscribed!')
        } else {
          throw insertError
        }
      } else {
        setSuccess(true)

        if (typeof window !== 'undefined' && (window as any).gtag) {
          (window as any).gtag('event', 'email_signup', {
            source: content.source,
            page_url: window.location.href,
          })
        }

        setTimeout(() => setIsVisible(false), 3000)
      }
    } catch {
      setError('Failed to subscribe. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (!isVisible) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/70 backdrop-blur-sm z-[100]"
        onClick={handleClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-[101] w-full max-w-md mx-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="exit-popup-title"
      >
        <div className="bg-[hsl(220,55%,7%)] border border-[hsl(215,40%,18%)] rounded-xl shadow-2xl shadow-black/50 p-8 relative">
          {/* Close button */}
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 p-2 text-[hsl(210,20%,50%)] hover:text-white transition-colors"
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {success ? (
            <div className="text-center py-4">
              <div className="w-16 h-16 bg-[hsl(142,71%,55%)]/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-[hsl(142,71%,55%)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">You're In!</h3>
              <p className="text-[hsl(210,20%,60%)]">
                Check your inbox for {content.successMessage}.
              </p>
            </div>
          ) : (
            <>
              {/* Terminal-style accent */}
              <div className="flex items-center gap-1.5 mb-6">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
                <span className="ml-2 text-xs font-mono text-[hsl(210,20%,45%)]">quantengines.com</span>
              </div>

              {/* Heading */}
              <h3 id="exit-popup-title" className="text-2xl font-bold text-white mb-2">
                {content.headline}
              </h3>
              <p className="text-[hsl(210,20%,60%)] mb-6">
                {content.subtitle}
              </p>

              {/* Benefits */}
              <div className="space-y-2 mb-6">
                {content.benefits.map((benefit, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-[hsl(45,96%,58%)] font-mono mt-0.5">$</span>
                    <span className="text-[hsl(210,20%,75%)]">{benefit}</span>
                  </div>
                ))}
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-3">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  required
                  className="w-full px-4 py-3 bg-[hsl(220,55%,5%)] border border-[hsl(215,40%,20%)] rounded-lg text-white placeholder:text-[hsl(215,20%,40%)] font-mono text-sm focus:outline-none focus:border-[hsl(45,96%,58%)]/50 transition-colors"
                />

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full px-6 py-3 bg-gradient-to-r from-[hsl(45,96%,58%)] to-[hsl(38,92%,45%)] text-[hsl(220,60%,8%)] font-bold rounded-lg hover:from-[hsl(45,96%,65%)] hover:to-[hsl(38,92%,52%)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Subscribing...' : content.buttonText}
                </button>
              </form>

              {error && (
                <p className="text-red-400 text-sm text-center mt-2">{error}</p>
              )}

              {/* Trust signals */}
              <div className="mt-4 pt-4 border-t border-[hsl(215,40%,14%)]">
                <div className="flex items-center justify-center gap-4 text-xs text-[hsl(215,20%,45%)] font-mono">
                  <span>no spam</span>
                  <span className="text-[hsl(215,40%,25%)]">|</span>
                  <span>unsubscribe anytime</span>
                  <span className="text-[hsl(215,40%,25%)]">|</span>
                  <span>free forever</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}
