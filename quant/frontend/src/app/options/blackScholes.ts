/**
 * Black-Scholes-Merton pricing and Greeks for European options on a
 * non-dividend-paying underlying.
 *
 * Formulas as published in Black & Scholes (1973) / Merton (1973), in the
 * standard textbook form (Hull, "Options, Futures, and Other Derivatives"):
 *
 *   d1 = [ ln(S/K) + (r + sigma^2 / 2) * T ] / (sigma * sqrt(T))
 *   d2 = d1 - sigma * sqrt(T)
 *   call = S * N(d1) - K * e^(-rT) * N(d2)
 *   put  = K * e^(-rT) * N(-d2) - S * N(-d1)
 *
 * Every function here is closed-form arithmetic over caller-supplied inputs.
 * There is no market data source behind this module, so nothing it returns
 * may be presented as a quoted or observed price.
 */

/**
 * Standard normal CDF.
 *
 * Hart (1968) rational approximation, in the arrangement given by Graeme West,
 * "Better Approximations to Cumulative Normal Functions" (Wilmott, 2005).
 * Accurate to roughly 1e-14 absolute across the whole real line, versus ~7.5e-8
 * for the commonly used Abramowitz & Stegun 26.2.17 five-term form, which is
 * not enough precision to quote Greeks to four decimal places.
 */
export function normalCDF(x: number): number {
  const z = Math.abs(x)
  let c = 0

  if (z <= 37) {
    const e = Math.exp((-z * z) / 2)
    if (z < 7.07106781186547) {
      let b = 3.52624965998911e-2 * z + 0.700383064443688
      b = b * z + 6.37396220353165
      b = b * z + 33.912866078383
      b = b * z + 112.079291497871
      b = b * z + 221.213596169931
      b = b * z + 220.206867912376
      let d = 8.83883476483184e-2 * z + 1.75566716318264
      d = d * z + 16.064177579207
      d = d * z + 86.7807322029461
      d = d * z + 296.564248779674
      d = d * z + 637.333633378831
      d = d * z + 793.826512519948
      d = d * z + 440.413735824752
      c = (e * b) / d
    } else {
      let f = z + 0.65
      f = z + 4 / f
      f = z + 3 / f
      f = z + 2 / f
      f = z + 1 / f
      c = e / (f * 2.506628274631)
    }
  }

  return x > 0 ? 1 - c : c
}

/** Standard normal PDF: phi(x) = e^(-x^2/2) / sqrt(2*pi). */
export function normalPDF(x: number): number {
  return Math.exp((-x * x) / 2) / Math.sqrt(2 * Math.PI)
}

export type OptionType = 'call' | 'put'

export interface BlackScholesInputs {
  /** Spot price of the underlying. Must be > 0. */
  S: number
  /** Strike price. Must be > 0. */
  K: number
  /** Time to expiry in years. Must be > 0. */
  T: number
  /** Continuously compounded risk-free rate, as a decimal (0.05 = 5%). */
  r: number
  /** Annualised volatility, as a decimal (0.20 = 20%). Must be > 0. */
  sigma: number
  type: OptionType
}

export interface BlackScholesResult {
  d1: number
  d2: number
  /** Theoretical value per share of the underlying. */
  price: number
  /** Change in price per $1 change in spot. */
  delta: number
  /** Change in delta per $1 change in spot. */
  gamma: number
  /** Change in price per 1 percentage point change in volatility. */
  vegaPerPoint: number
  /** Change in price per calendar day of elapsed time. */
  thetaPerDay: number
  /** Change in price per 1 percentage point change in the rate. */
  rhoPerPoint: number
  /** Exercise value if expiry were now: max(S-K, 0) for a call. */
  intrinsic: number
  /** price - intrinsic. */
  timeValue: number
}

/** Inputs outside the domain of the model produce null, never NaN or Infinity. */
export function validateInputs(i: BlackScholesInputs): string | null {
  if (!Number.isFinite(i.S) || i.S <= 0) return 'Spot price must be greater than 0.'
  if (!Number.isFinite(i.K) || i.K <= 0) return 'Strike price must be greater than 0.'
  if (!Number.isFinite(i.T) || i.T <= 0) return 'Time to expiry must be greater than 0 days.'
  if (!Number.isFinite(i.sigma) || i.sigma <= 0) return 'Volatility must be greater than 0%.'
  if (!Number.isFinite(i.r)) return 'Risk-free rate must be a number.'
  // sigma*sqrt(T) is the denominator of d1; below this it is numerically
  // indistinguishable from the zero-volatility limit the model excludes.
  if (i.sigma * Math.sqrt(i.T) < 1e-8) return 'Volatility and time to expiry are too small to price.'
  return null
}

/**
 * Returns null rather than a partially-NaN result when inputs are outside the
 * model's domain, so a failure is never rendered as a number.
 */
export function blackScholes(i: BlackScholesInputs): BlackScholesResult | null {
  if (validateInputs(i) !== null) return null

  const { S, K, T, r, sigma, type } = i
  const sqrtT = Math.sqrt(T)
  const volT = sigma * sqrtT
  const disc = Math.exp(-r * T)

  const d1 = (Math.log(S / K) + (r + (sigma * sigma) / 2) * T) / volT
  const d2 = d1 - volT
  const pdf1 = normalPDF(d1)

  const isCall = type === 'call'

  const price = isCall
    ? S * normalCDF(d1) - K * disc * normalCDF(d2)
    : K * disc * normalCDF(-d2) - S * normalCDF(-d1)

  const delta = isCall ? normalCDF(d1) : normalCDF(d1) - 1

  // Gamma and vega are identical for calls and puts (put-call parity).
  const gamma = pdf1 / (S * volT)
  const vega = S * pdf1 * sqrtT

  // Annualised theta; divided below to express per calendar day.
  const thetaAnnual = isCall
    ? (-S * pdf1 * sigma) / (2 * sqrtT) - r * K * disc * normalCDF(d2)
    : (-S * pdf1 * sigma) / (2 * sqrtT) + r * K * disc * normalCDF(-d2)

  const rho = isCall ? K * T * disc * normalCDF(d2) : -K * T * disc * normalCDF(-d2)

  const intrinsic = isCall ? Math.max(0, S - K) : Math.max(0, K - S)

  const result: BlackScholesResult = {
    d1,
    d2,
    price,
    delta,
    gamma,
    // Vega and rho are quoted per 1 percentage point, the market convention,
    // so the raw per-1.0 derivative is scaled by 1/100.
    vegaPerPoint: vega / 100,
    thetaPerDay: thetaAnnual / 365,
    rhoPerPoint: rho / 100,
    intrinsic,
    timeValue: price - intrinsic,
  }

  // Belt and braces: any non-finite value is a failure, not a result.
  for (const v of Object.values(result)) {
    if (!Number.isFinite(v)) return null
  }
  return result
}

/** True when exercising now would have positive value. */
export function isInTheMoney(S: number, K: number, type: OptionType): boolean {
  return type === 'call' ? S > K : S < K
}

/**
 * Break-even underlying price at expiry for a single long option bought at
 * `premium`: strike + premium for a call, strike - premium for a put.
 */
export function breakEvenAtExpiry(K: number, premium: number, type: OptionType): number {
  return type === 'call' ? K + premium : Math.max(0, K - premium)
}
