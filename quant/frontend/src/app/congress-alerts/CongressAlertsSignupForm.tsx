'use client'

import { useState } from 'react'
import type { AlertFilterInput, AlertTier, BillingCycle, Chamber } from '@/lib/congress-alerts'
import { PRO_MAX_FILTERS, FREE_MAX_FILTERS, PRO_PRICE_MONTHLY_USD, PRO_PRICE_YEARLY_USD } from '@/lib/congress-alerts'

interface FilterRow {
  ticker: string
  memberName: string
  chamber: Chamber | ''
}

const EMPTY_ROW: FilterRow = { ticker: '', memberName: '', chamber: '' }

function toInput(rows: FilterRow[]): AlertFilterInput[] {
  return rows
    .map((r) => ({
      ticker: r.ticker.trim() || undefined,
      memberName: r.memberName.trim() || undefined,
      chamber: r.chamber || undefined,
    }))
    .filter((f) => f.ticker || f.memberName || f.chamber)
}

export function CongressAlertsSignupForm({ initialTier = 'free' }: { initialTier?: AlertTier }) {
  const [tier, setTier] = useState<AlertTier>(initialTier)
  const [billingCycle, setBillingCycle] = useState<BillingCycle>('monthly')
  const [email, setEmail] = useState('')
  const [rows, setRows] = useState<FilterRow[]>([{ ...EMPTY_ROW }])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<{ manageUrl: string } | null>(null)

  const maxRows = tier === 'pro' ? Math.min(PRO_MAX_FILTERS, 10) : FREE_MAX_FILTERS

  function updateRow(i: number, patch: Partial<FilterRow>) {
    setRows((prev) => prev.map((r, idx) => (idx === i ? { ...r, ...patch } : r)))
  }

  function addRow() {
    setRows((prev) => (prev.length >= maxRows ? prev : [...prev, { ...EMPTY_ROW }]))
  }

  function removeRow(i: number) {
    setRows((prev) => prev.filter((_, idx) => idx !== i))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setSubmitting(true)
    try {
      const res = await fetch('/api/congress-alerts/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          tier,
          billingCycle,
          filters: toInput(rows).slice(0, maxRows),
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Something went wrong. Please try again.')
        return
      }
      if (data.checkoutUrl) {
        window.location.href = data.checkoutUrl
        return
      }
      setSuccess({ manageUrl: data.manageUrl })
    } catch {
      setError('Network error. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (success) {
    return (
      <div className="rounded-xl border border-emerald-800/50 bg-emerald-950/30 p-6">
        <h3 className="text-lg font-bold text-white mb-2">You&apos;re on the list</h3>
        <p className="text-sm text-slate-300 mb-3">
          {tier === 'pro'
            ? "You're subscribed. Your first daily digest goes out the next time new trades matching your filters are disclosed."
            : "You'll get a weekly digest of new congressional trade disclosures."}
        </p>
        <a href={success.manageUrl} className="text-sm text-indigo-400 hover:underline">
          Manage your filters or unsubscribe any time →
        </a>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
      {/* Plan toggle */}
      <div className="flex gap-2 mb-5">
        {(['free', 'pro'] as const).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTier(t)}
            className={`flex-1 rounded-lg border px-4 py-3 text-left transition-colors ${
              tier === t
                ? 'border-[hsl(45,96%,58%)] bg-[hsl(45,96%,58%)]/10'
                : 'border-[hsl(215,40%,18%)] hover:border-[hsl(215,40%,28%)]'
            }`}
          >
            <div className="text-sm font-bold text-white">{t === 'free' ? 'Free' : 'Pro'}</div>
            <div className="text-xs text-slate-400">
              {t === 'free' ? 'Weekly digest, 1 filter' : `$${PRO_PRICE_MONTHLY_USD}/mo · daily digest`}
            </div>
          </button>
        ))}
      </div>

      {tier === 'pro' && (
        <div className="flex gap-2 mb-5 text-sm">
          <button
            type="button"
            onClick={() => setBillingCycle('monthly')}
            className={`px-3 py-1.5 rounded ${billingCycle === 'monthly' ? 'bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] font-semibold' : 'text-slate-400 border border-[hsl(215,40%,18%)]'}`}
          >
            ${PRO_PRICE_MONTHLY_USD}/mo
          </button>
          <button
            type="button"
            onClick={() => setBillingCycle('yearly')}
            className={`px-3 py-1.5 rounded ${billingCycle === 'yearly' ? 'bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] font-semibold' : 'text-slate-400 border border-[hsl(215,40%,18%)]'}`}
          >
            ${PRO_PRICE_YEARLY_USD}/yr <span className="opacity-70">(save ~27%)</span>
          </button>
        </div>
      )}

      {/* Email */}
      <label className="block text-xs font-semibold text-slate-400 mb-1.5">Email address</label>
      <input
        type="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
        className="w-full mb-5 px-3 py-2.5 rounded-lg bg-[hsl(220,55%,5%)] border border-[hsl(215,40%,20%)] text-white placeholder:text-slate-600 focus:outline-none focus:border-[hsl(45,96%,58%)]/50"
      />

      {/* Filters */}
      <div className="mb-2 flex items-center justify-between">
        <label className="text-xs font-semibold text-slate-400">
          Alert filters (optional — leave blank for every new disclosure)
        </label>
        <span className="text-[11px] text-slate-500">
          {rows.length}/{maxRows}
        </span>
      </div>
      <div className="space-y-2 mb-3">
        {rows.map((row, i) => (
          <div key={i} className="flex flex-wrap gap-2 items-center">
            <input
              value={row.ticker}
              onChange={(e) => updateRow(i, { ticker: e.target.value.toUpperCase() })}
              placeholder="Ticker (e.g. NVDA)"
              maxLength={10}
              className="flex-1 min-w-[110px] px-2.5 py-2 text-sm rounded bg-[hsl(220,55%,5%)] border border-[hsl(215,40%,20%)] text-white placeholder:text-slate-600 focus:outline-none focus:border-[hsl(45,96%,58%)]/50"
            />
            <input
              value={row.memberName}
              onChange={(e) => updateRow(i, { memberName: e.target.value })}
              placeholder="Member name contains…"
              className="flex-[2] min-w-[160px] px-2.5 py-2 text-sm rounded bg-[hsl(220,55%,5%)] border border-[hsl(215,40%,20%)] text-white placeholder:text-slate-600 focus:outline-none focus:border-[hsl(45,96%,58%)]/50"
            />
            <select
              value={row.chamber}
              onChange={(e) => updateRow(i, { chamber: e.target.value as Chamber | '' })}
              className="px-2.5 py-2 text-sm rounded bg-[hsl(220,55%,5%)] border border-[hsl(215,40%,20%)] text-white focus:outline-none focus:border-[hsl(45,96%,58%)]/50"
            >
              <option value="">Any chamber</option>
              <option value="House">House</option>
              <option value="Senate">Senate</option>
            </select>
            {rows.length > 1 && (
              <button
                type="button"
                onClick={() => removeRow(i)}
                aria-label="Remove filter"
                className="text-slate-500 hover:text-red-400 px-1"
              >
                ✕
              </button>
            )}
          </div>
        ))}
      </div>
      {rows.length < maxRows && (
        <button type="button" onClick={addRow} className="text-xs text-indigo-400 hover:underline mb-5">
          + Add another filter{tier === 'free' ? ' (upgrade to Pro for more)' : ''}
        </button>
      )}
      {rows.length >= maxRows && <div className="mb-5" />}

      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="w-full bg-gradient-to-r from-[hsl(45,96%,58%)] to-[hsl(38,92%,45%)] text-[hsl(220,60%,8%)] font-semibold py-3 rounded-lg disabled:opacity-50"
      >
        {submitting ? 'Please wait…' : tier === 'pro' ? `Continue to checkout — $${billingCycle === 'monthly' ? PRO_PRICE_MONTHLY_USD + '/mo' : PRO_PRICE_YEARLY_USD + '/yr'}` : 'Get the free weekly digest'}
      </button>
      <p className="text-[11px] text-slate-500 mt-3 text-center">
        Cancel any time from your manage link. No credit card required for the free plan.
      </p>
    </form>
  )
}
