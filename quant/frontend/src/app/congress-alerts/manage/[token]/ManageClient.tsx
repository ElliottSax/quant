'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import type { AlertFilterInput, Chamber } from '@/lib/congress-alerts'

interface FilterRow {
  ticker: string
  memberName: string
  chamber: Chamber | ''
}

interface ManageData {
  email: string
  tier: 'free' | 'pro'
  status: string
  maxFilters: number
  filters: { id: string; ticker: string | null; member_name: string | null; chamber: Chamber | null }[]
}

function toInput(rows: FilterRow[]): AlertFilterInput[] {
  return rows
    .map((r) => ({ ticker: r.ticker.trim() || undefined, memberName: r.memberName.trim() || undefined, chamber: r.chamber || undefined }))
    .filter((f) => f.ticker || f.memberName || f.chamber)
}

export function ManageClient({ token }: { token: string }) {
  const [data, setData] = useState<ManageData | null>(null)
  const [rows, setRows] = useState<FilterRow[]>([])
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [unsubscribed, setUnsubscribed] = useState(false)

  useEffect(() => {
    fetch(`/api/congress-alerts/manage/${token}`)
      .then(async (res) => {
        if (!res.ok) {
          setNotFound(true)
          return
        }
        const json: ManageData = await res.json()
        setData(json)
        setRows(
          json.filters.length > 0
            ? json.filters.map((f) => ({ ticker: f.ticker || '', memberName: f.member_name || '', chamber: f.chamber || '' }))
            : [{ ticker: '', memberName: '', chamber: '' }]
        )
      })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false))
  }, [token])

  function updateRow(i: number, patch: Partial<FilterRow>) {
    setRows((prev) => prev.map((r, idx) => (idx === i ? { ...r, ...patch } : r)))
  }
  function addRow() {
    if (!data) return
    setRows((prev) => (prev.length >= data.maxFilters ? prev : [...prev, { ticker: '', memberName: '', chamber: '' }]))
  }
  function removeRow(i: number) {
    setRows((prev) => prev.filter((_, idx) => idx !== i))
  }

  async function save() {
    setSaving(true)
    setMessage(null)
    try {
      const res = await fetch(`/api/congress-alerts/manage/${token}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filters: toInput(rows) }),
      })
      const json = await res.json()
      setMessage(res.ok ? 'Saved.' : json.error || 'Could not save.')
    } catch {
      setMessage('Network error.')
    } finally {
      setSaving(false)
    }
  }

  async function openPortal() {
    setSaving(true)
    setMessage(null)
    try {
      const res = await fetch('/api/congress-alerts/portal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      })
      const json = await res.json()
      if (res.ok && json.url) {
        window.location.href = json.url
        return
      }
      setMessage(json.error || 'Could not open billing portal.')
    } catch {
      setMessage('Network error.')
    } finally {
      setSaving(false)
    }
  }

  async function unsubscribe() {
    if (!confirm('Unsubscribe from congress trading alerts? This cancels any paid plan immediately.')) return
    setSaving(true)
    try {
      const res = await fetch(`/api/congress-alerts/manage/${token}`, { method: 'DELETE' })
      if (res.ok) setUnsubscribed(true)
      else setMessage('Could not unsubscribe. Please try again.')
    } catch {
      setMessage('Network error.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <p className="text-slate-400">Loading…</p>

  if (notFound || !data) {
    return (
      <div className="max-w-lg">
        <p className="text-slate-400 mb-4">This manage link is invalid or has expired.</p>
        <Link href="/congress-alerts" className="text-indigo-400 hover:underline">Sign up for alerts →</Link>
      </div>
    )
  }

  if (unsubscribed) {
    return (
      <div className="max-w-lg rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-bold text-white mb-2">You&apos;re unsubscribed</h2>
        <p className="text-sm text-slate-400">
          {data.email} will no longer receive congress trading alert digests. Any paid subscription was canceled immediately.
        </p>
        <Link href="/congress-alerts" className="text-indigo-400 hover:underline text-sm mt-3 inline-block">
          Sign up again →
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-2xl">
      <div className="flex items-center gap-3 mb-6">
        <span className="text-sm text-slate-400">{data.email}</span>
        <span
          className={`text-xs font-semibold uppercase tracking-wide px-2 py-0.5 rounded ${
            data.tier === 'pro' ? 'bg-[hsl(45,96%,58%)]/15 text-[hsl(45,96%,58%)]' : 'bg-slate-700/50 text-slate-400'
          }`}
        >
          {data.tier} · {data.status}
        </span>
      </div>

      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6 mb-4">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-300">Alert filters</h2>
          <span className="text-[11px] text-slate-500">
            {rows.length}/{data.maxFilters}
          </span>
        </div>
        <div className="space-y-2 mb-3">
          {rows.map((row, i) => (
            <div key={i} className="flex flex-wrap gap-2 items-center">
              <input
                value={row.ticker}
                onChange={(e) => updateRow(i, { ticker: e.target.value.toUpperCase() })}
                placeholder="Ticker"
                maxLength={10}
                className="flex-1 min-w-[100px] px-2.5 py-2 text-sm rounded bg-[hsl(220,55%,5%)] border border-[hsl(215,40%,20%)] text-white placeholder:text-slate-600"
              />
              <input
                value={row.memberName}
                onChange={(e) => updateRow(i, { memberName: e.target.value })}
                placeholder="Member name contains…"
                className="flex-[2] min-w-[160px] px-2.5 py-2 text-sm rounded bg-[hsl(220,55%,5%)] border border-[hsl(215,40%,20%)] text-white placeholder:text-slate-600"
              />
              <select
                value={row.chamber}
                onChange={(e) => updateRow(i, { chamber: e.target.value as Chamber | '' })}
                className="px-2.5 py-2 text-sm rounded bg-[hsl(220,55%,5%)] border border-[hsl(215,40%,20%)] text-white"
              >
                <option value="">Any chamber</option>
                <option value="House">House</option>
                <option value="Senate">Senate</option>
              </select>
              {rows.length > 1 && (
                <button type="button" onClick={() => removeRow(i)} className="text-slate-500 hover:text-red-400 px-1">
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>
        {rows.length < data.maxFilters && (
          <button type="button" onClick={addRow} className="text-xs text-indigo-400 hover:underline">
            + Add filter
          </button>
        )}
        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={save}
            disabled={saving}
            className="bg-gradient-to-r from-[hsl(45,96%,58%)] to-[hsl(38,92%,45%)] text-[hsl(220,60%,8%)] font-semibold px-4 py-2 rounded-lg text-sm disabled:opacity-50"
          >
            Save filters
          </button>
          {message && <span className="text-xs text-slate-400">{message}</span>}
        </div>
      </div>

      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-300 mb-1">Billing &amp; subscription</h2>
          <p className="text-xs text-slate-500">
            {data.tier === 'pro' ? 'Update your card or view invoices via Stripe.' : "You're on the free plan — nothing to bill."}
          </p>
        </div>
        <div className="flex gap-2">
          {data.tier === 'pro' && (
            <button onClick={openPortal} disabled={saving} className="text-sm px-3 py-1.5 rounded border border-[hsl(215,40%,20%)] text-slate-300 hover:bg-[hsl(215,50%,14%)]">
              Manage billing
            </button>
          )}
          <button onClick={unsubscribe} disabled={saving} className="text-sm px-3 py-1.5 rounded border border-red-900/50 text-red-400 hover:bg-red-950/30">
            Unsubscribe
          </button>
        </div>
      </div>
    </div>
  )
}
