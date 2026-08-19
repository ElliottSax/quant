/**
 * Overlay maths for the price chart.
 *
 * Every function here is a pure transform of the closes that actually came out of
 * public/data/prices.json. A window that the history cannot fill returns `null` at that
 * index and the caller draws a gap — no seeding from a shorter window, no forward-fill,
 * no zero. If the whole series is shorter than the window the function returns null and
 * the indicator is not offered at all.
 */

/** Simple moving average. Index i is null until i+1 closes are available. */
export function sma(values: number[], period: number): (number | null)[] | null {
  if (period < 1 || values.length < period) return null

  const out: (number | null)[] = new Array(values.length).fill(null)
  let sum = 0
  for (let i = 0; i < values.length; i++) {
    sum += values[i]
    if (i >= period) sum -= values[i - period]
    if (i >= period - 1) out[i] = sum / period
  }
  return out
}

/**
 * Exponential moving average, seeded with the simple mean of the first full window so
 * the first published value rests on `period` real closes rather than on one.
 */
export function ema(values: number[], period: number): (number | null)[] | null {
  if (period < 1 || values.length < period) return null

  const out: (number | null)[] = new Array(values.length).fill(null)
  const k = 2 / (period + 1)

  let seed = 0
  for (let i = 0; i < period; i++) seed += values[i]
  let prev = seed / period
  out[period - 1] = prev

  for (let i = period; i < values.length; i++) {
    prev = values[i] * k + prev * (1 - k)
    out[i] = prev
  }
  return out
}

export interface BollingerBands {
  middle: (number | null)[]
  upper: (number | null)[]
  lower: (number | null)[]
}

/** Bollinger bands on the population standard deviation of the same window. */
export function bollinger(
  values: number[],
  period = 20,
  multiplier = 2,
): BollingerBands | null {
  const middle = sma(values, period)
  if (!middle) return null

  const upper: (number | null)[] = new Array(values.length).fill(null)
  const lower: (number | null)[] = new Array(values.length).fill(null)

  for (let i = period - 1; i < values.length; i++) {
    const mean = middle[i]
    if (mean === null) continue
    let acc = 0
    for (let j = i - period + 1; j <= i; j++) {
      const d = values[j] - mean
      acc += d * d
    }
    const sd = Math.sqrt(acc / period)
    upper[i] = mean + multiplier * sd
    lower[i] = mean - multiplier * sd
  }

  return { middle, upper, lower }
}
