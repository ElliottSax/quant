/**
 * Two server-rendered SVG charts. No charting library and no client JavaScript: the marks
 * are computed at build time from the artefact, so the shape of the curve is in the HTML
 * and is visible to a crawler, a reader with JS disabled, and a screen reader reading the
 * accompanying table.
 */

export interface Tenor {
  tenor: string
  months: number
  yield: number
}

const W = 760
const H = 300
const PAD = { top: 24, right: 28, bottom: 40, left: 48 }

const niceTicks = (lo: number, hi: number, count = 5) => {
  const span = hi - lo || 1
  const raw = span / count
  const mag = Math.pow(10, Math.floor(Math.log10(raw)))
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? mag * 10
  const first = Math.ceil(lo / step) * step
  const out: number[] = []
  for (let v = first; v <= hi + 1e-9; v += step) out.push(Number(v.toFixed(6)))
  return out
}

/** Today's par curve. Tenors are placed on a log scale in months, because otherwise the
 *  eleven maturities under two years pile into the left inch of the axis and the shape of
 *  the short end — the part that actually inverts — becomes unreadable. */
export function CurveChart({ curve, asOf }: { curve: Tenor[]; asOf: string }) {
  if (curve.length < 2) return null
  const xs = curve.map((t) => Math.log(t.months))
  const ys = curve.map((t) => t.yield)
  const x0 = Math.min(...xs)
  const x1 = Math.max(...xs)
  const lo = Math.min(...ys)
  const hi = Math.max(...ys)
  const pad = (hi - lo) * 0.25 || 0.5
  const yLo = lo - pad
  const yHi = hi + pad

  const px = (m: number) =>
    PAD.left + ((Math.log(m) - x0) / (x1 - x0)) * (W - PAD.left - PAD.right)
  const py = (v: number) =>
    PAD.top + (1 - (v - yLo) / (yHi - yLo)) * (H - PAD.top - PAD.bottom)

  const pts = curve.map((t) => [px(t.months), py(t.yield)] as const)
  const path = pts.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join('')
  const labelled = new Set(['3 Mo', '2 Yr', '10 Yr', '30 Yr'])

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img"
         aria-label={`US Treasury par yield curve on ${asOf}, from ${curve[0].tenor} at ${curve[0].yield}% to ${curve[curve.length - 1].tenor} at ${curve[curve.length - 1].yield}%. The full figures are in the table below.`}>
      {niceTicks(yLo, yHi).map((v) => (
        <g key={v}>
          <line x1={PAD.left} x2={W - PAD.right} y1={py(v)} y2={py(v)}
                stroke="hsl(215,40%,18%)" strokeWidth="1" />
          <text x={PAD.left - 8} y={py(v) + 4} textAnchor="end"
                fill="hsl(215,20%,45%)" fontSize="11" fontFamily="ui-monospace, monospace">
            {v.toFixed(1)}%
          </text>
        </g>
      ))}
      <path d={path} fill="none" stroke="hsl(239,84%,67%)" strokeWidth="2"
            strokeLinejoin="round" strokeLinecap="round" />
      {curve.map((t, i) => (
        <g key={t.tenor}>
          <circle cx={pts[i][0]} cy={pts[i][1]} r="3.5"
                  fill="hsl(220,55%,9%)" stroke="hsl(239,84%,67%)" strokeWidth="2" />
          {labelled.has(t.tenor) && (
            <>
              <text x={pts[i][0]} y={pts[i][1] - 12} textAnchor="middle"
                    fill="hsl(215,20%,85%)" fontSize="11" fontWeight="600"
                    fontFamily="ui-monospace, monospace">
                {t.yield.toFixed(2)}
              </text>
              <text x={pts[i][0]} y={H - PAD.bottom + 18} textAnchor="middle"
                    fill="hsl(215,20%,55%)" fontSize="11">
                {t.tenor}
              </text>
            </>
          )}
        </g>
      ))}
    </svg>
  )
}

/** The 10y−2y spread through time, with the zero line and every inverted stretch shaded.
 *  Shading below zero is the whole point of the chart: it makes the episode table visible
 *  as geometry rather than as a list of dates. */
export function SpreadChart({
  history,
  label,
}: {
  history: Array<[string, number | null, number | null]>
  label: string
}) {
  const pts = history
    .map(([d, s]) => [d, s] as const)
    .filter((p): p is readonly [string, number] => p[1] !== null)
  if (pts.length < 2) return null

  // One point per week is plenty at this width and keeps the path a few KB rather than
  // a hundred. The last observation is always kept so the chart ends where the data does.
  const step = Math.max(1, Math.floor(pts.length / 900))
  const sampled = pts.filter((_, i) => i % step === 0)
  if (sampled[sampled.length - 1][0] !== pts[pts.length - 1][0]) sampled.push(pts[pts.length - 1])

  const t0 = Date.parse(sampled[0][0])
  const t1 = Date.parse(sampled[sampled.length - 1][0])
  const vals = sampled.map((p) => p[1])
  const yLo = Math.min(...vals, 0) - 0.15
  const yHi = Math.max(...vals, 0) + 0.15

  const px = (d: string) => PAD.left + ((Date.parse(d) - t0) / (t1 - t0)) * (W - PAD.left - PAD.right)
  const py = (v: number) => PAD.top + (1 - (v - yLo) / (yHi - yLo)) * (H - PAD.top - PAD.bottom)
  const zero = py(0)

  const path = sampled.map(([d, v], i) => `${i ? 'L' : 'M'}${px(d).toFixed(1)},${py(v).toFixed(1)}`).join('')

  // Contiguous negative stretches, from the sampled series, as shaded bands.
  const bands: Array<[number, number]> = []
  let start: string | null = null
  for (const [d, v] of sampled) {
    if (v < 0 && start === null) start = d
    else if (v >= 0 && start !== null) {
      bands.push([px(start), px(d)])
      start = null
    }
  }
  if (start !== null) bands.push([px(start), px(sampled[sampled.length - 1][0])])

  const years = []
  for (let y = new Date(t0).getUTCFullYear(); y <= new Date(t1).getUTCFullYear(); y += 5) {
    years.push(y)
  }

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img"
         aria-label={`${label} from ${sampled[0][0]} to ${sampled[sampled.length - 1][0]}. Shaded regions mark periods when the spread was negative. The episode table below lists each one with its dates and depth.`}>
      {bands.map(([a, b], i) => (
        <rect key={i} x={a} y={PAD.top} width={Math.max(b - a, 1)} height={H - PAD.top - PAD.bottom}
              fill="hsl(350,80%,60%)" opacity="0.13" />
      ))}
      {niceTicks(yLo, yHi).map((v) => (
        <g key={v}>
          <line x1={PAD.left} x2={W - PAD.right} y1={py(v)} y2={py(v)}
                stroke="hsl(215,40%,16%)" strokeWidth="1" />
          <text x={PAD.left - 8} y={py(v) + 4} textAnchor="end"
                fill="hsl(215,20%,45%)" fontSize="11" fontFamily="ui-monospace, monospace">
            {v.toFixed(1)}
          </text>
        </g>
      ))}
      <line x1={PAD.left} x2={W - PAD.right} y1={zero} y2={zero}
            stroke="hsl(215,20%,55%)" strokeWidth="1.5" strokeDasharray="4 3" />
      <path d={path} fill="none" stroke="hsl(239,84%,67%)" strokeWidth="1.5"
            strokeLinejoin="round" />
      {years.map((y) => {
        const x = px(`${y}-01-01`)
        if (x < PAD.left || x > W - PAD.right) return null
        return (
          <text key={y} x={x} y={H - PAD.bottom + 18} textAnchor="middle"
                fill="hsl(215,20%,45%)" fontSize="11">
            {y}
          </text>
        )
      })}
      <text x={W - PAD.right} y={zero - 6} textAnchor="end" fill="hsl(215,20%,55%)" fontSize="10">
        0 — inverted below this line
      </text>
    </svg>
  )
}
