/**
 * Tangency (maximum-Sharpe) portfolio weights.
 *
 *   w ∝ Σ⁻¹ (μ − r_f · 1),  then normalised so the weights sum to 1.
 *
 * This is the closed-form solution to  max_w (wᵀμ − r_f) / sqrt(wᵀΣw), which is the
 * query people are searching ("maximize w^t mu / sqrt(w^t sigma w) solution w
 * proportional to sigma inverse"). It is unconstrained apart from the budget constraint:
 * short weights are permitted and DO occur, which the UI states rather than hiding by
 * silently clipping — a clipped result is no longer the solution to this problem.
 *
 * Verified against numpy for the documented example: expected returns 10/12/8%,
 * volatilities 15/20/10%, correlations 0.30/0.10/0.20, risk-free 2% gives weights
 * 0.292376 / 0.153539 / 0.554085 and Sharpe 0.809373 — and that Sharpe beats the best
 * of 200,000 random long-only portfolios (0.809371), as the optimum must.
 */

export interface Inputs {
  /** Expected annual returns, as decimals (0.10 = 10%). */
  mu: number[]
  /** Annual volatilities, as decimals. */
  vol: number[]
  /** Correlation matrix, symmetric with unit diagonal. */
  corr: number[][]
  /** Risk-free rate, as a decimal. */
  rf: number
}

export interface Result {
  weights: number[]
  covariance: number[][]
  expectedReturn: number
  volatility: number
  sharpe: number
  hasShorts: boolean
}

/** Gaussian elimination with partial pivoting. Returns null for a singular system. */
export function solve(A: number[][], b: number[]): number[] | null {
  const n = b.length
  const M = A.map((row, i) => [...row, b[i]])

  for (let col = 0; col < n; col++) {
    let piv = col
    for (let r = col + 1; r < n; r++) {
      if (Math.abs(M[r][col]) > Math.abs(M[piv][col])) piv = r
    }
    // A singular (or near-singular) covariance matrix has no unique solution. Returning
    // null makes the caller say so; a pseudo-inverse would silently invent one answer
    // out of infinitely many.
    if (Math.abs(M[piv][col]) < 1e-12) return null
    ;[M[col], M[piv]] = [M[piv], M[col]]

    for (let r = 0; r < n; r++) {
      if (r === col) continue
      const f = M[r][col] / M[col][col]
      for (let c = col; c <= n; c++) M[r][c] -= f * M[col][c]
    }
  }
  // Fully reduced: each row is now [0 ... d ... 0 | rhs], so x_i = rhs / d.
  return M.map((row, i) => row[n] / row[i])
}

export function covarianceFrom(vol: number[], corr: number[][]): number[][] {
  return vol.map((vi, i) => vol.map((vj, j) => vi * vj * corr[i][j]))
}

export function maxSharpe(inp: Inputs): Result | null {
  const { mu, vol, corr, rf } = inp
  const n = mu.length
  if (n < 2 || vol.length !== n || corr.length !== n) return null
  if (vol.some(v => !(v > 0))) return null

  const S = covarianceFrom(vol, corr)
  const excess = mu.map(m => m - rf)
  const raw = solve(S, excess)
  if (!raw) return null

  const total = raw.reduce((a, b) => a + b, 0)
  // When the excess-return vector is orthogonal to the budget direction the weights sum
  // to ~0 and normalising explodes. There is no tangency portfolio to report there.
  if (!Number.isFinite(total) || Math.abs(total) < 1e-12) return null
  const w = raw.map(x => x / total)

  const expectedReturn = w.reduce((acc, wi, i) => acc + wi * mu[i], 0)
  let variance = 0
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) variance += w[i] * w[j] * S[i][j]
  if (!(variance > 0)) return null
  const volatility = Math.sqrt(variance)

  return {
    weights: w,
    covariance: S,
    expectedReturn,
    volatility,
    sharpe: (expectedReturn - rf) / volatility,
    hasShorts: w.some(x => x < 0),
  }
}
