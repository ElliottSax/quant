'use client';

import { useMemo, useState } from 'react';
import {
  ALL_QUESTIONS,
  CHECKLIST_GROUPS,
  computeSanityCheck,
  type PeriodsPerYear,
} from './strategyDiligence';

// ---------------------------------------------------------------------------
// Small helpers — inputs never produce NaN
// ---------------------------------------------------------------------------

function parseNum(value: string, fallback: number): number {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function parseOptionalNum(value: string): number | null {
  const t = value.trim();
  if (t === '') return null;
  const n = Number(t);
  return Number.isFinite(n) ? n : null;
}

function fmt(n: number | null | undefined, dp = 2): string {
  if (n === null || n === undefined || !Number.isFinite(n)) return '—';
  return n.toFixed(dp);
}

function fmtPct(n: number | null | undefined, dp = 1): string {
  if (n === null || n === undefined || !Number.isFinite(n)) return '—';
  return `${(n * 100).toFixed(dp)}%`;
}

type Answer = 'yes' | 'no' | 'unknown';

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function StrategyDiligenceTool() {
  // Checklist state — default Unknown for all 18
  const [answers, setAnswers] = useState<Record<string, Answer>>(() => {
    const init: Record<string, Answer> = {};
    for (const q of ALL_QUESTIONS) init[q.id] = 'unknown';
    return init;
  });

  // Panel 2 inputs — strings to avoid NaN on empty
  const [sharpeAnnual, setSharpeAnnual] = useState('1.5');
  const [periodsPerYear, setPeriodsPerYear] = useState<PeriodsPerYear>(252);
  const [years, setYears] = useState('3');
  const [skewness, setSkewness] = useState('0');
  const [kurtosis, setKurtosis] = useState('3');
  const [trials, setTrials] = useState('1');
  const [trialStd, setTrialStd] = useState(''); // blank = estimate

  // Checklist derived
  const checklistSummary = useMemo(() => {
    let yes = 0;
    let no = 0;
    let unknown = 0;
    const perGroup: Record<string, { yes: number; no: number; unknown: number }> = {};
    for (const g of CHECKLIST_GROUPS) perGroup[g.id] = { yes: 0, no: 0, unknown: 0 };

    for (const q of ALL_QUESTIONS) {
      const a = answers[q.id] ?? 'unknown';
      if (a === 'yes') yes++;
      else if (a === 'no') no++;
      else unknown++;
      const pg = perGroup[q.group];
      if (pg) {
        if (a === 'yes') pg.yes++;
        else if (a === 'no') pg.no++;
        else pg.unknown++;
      }
    }

    const openQuestions = ALL_QUESTIONS.filter((q) => {
      const a = answers[q.id] ?? 'unknown';
      return a === 'no' || a === 'unknown';
    });

    return { yes, no, unknown, perGroup, openQuestions };
  }, [answers]);

  // Panel 2 derived
  const sanity = useMemo(() => {
    return computeSanityCheck({
      annualizedSharpe: parseNum(sharpeAnnual, 1.5),
      periodsPerYear,
      years: parseNum(years, 3),
      skewness: parseNum(skewness, 0),
      kurtosis: parseNum(kurtosis, 3),
      trials: parseNum(trials, 1),
      trialSharpeStdDevAnnual: parseOptionalNum(trialStd),
    });
  }, [sharpeAnnual, periodsPerYear, years, skewness, kurtosis, trials, trialStd]);

  const setAnswer = (id: string, v: Answer) => {
    setAnswers((prev) => ({ ...prev, [id]: v }));
  };

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      {/* Panel 1 */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white">Evidence checklist</h2>
        <p className="mt-1 text-sm text-slate-400 leading-relaxed">
          Answer each question from the evidence available. Yes is the reassuring answer. Unknown means you do not have the information.
        </p>

        <div className="mt-6 space-y-8">
          {CHECKLIST_GROUPS.map((g) => (
            <div key={g.id}>
              <h3 className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)] mb-3">
                {g.id}. {g.title}
              </h3>
              <div className="space-y-4">
                {g.questions.map((q) => {
                  const v = answers[q.id] ?? 'unknown';
                  return (
                    <fieldset key={q.id} className="rounded-lg border border-[hsl(215,40%,14%)] bg-[hsl(220,60%,7%)] p-4">
                      <legend className="sr-only">{q.id}</legend>
                      <p className="text-sm text-white leading-relaxed">{q.id}. {q.text}</p>
                      <p className="mt-1 text-xs text-slate-400">{q.why}</p>
                      <div className="mt-3 flex gap-2" role="radiogroup" aria-label={q.id}>
                        {(['yes', 'no', 'unknown'] as const).map((opt) => (
                          <label
                            key={opt}
                            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium cursor-pointer transition-colors ${
                              v === opt
                                ? 'border-indigo-500 bg-indigo-500/20 text-indigo-200'
                                : 'border-[hsl(215,40%,18%)] bg-transparent text-slate-400 hover:border-[hsl(215,40%,24%)] hover:text-slate-300'
                            }`}
                          >
                            <input
                              type="radio"
                              name={q.id}
                              value={opt}
                              checked={v === opt}
                              onChange={() => setAnswer(q.id, opt)}
                              className="sr-only"
                              aria-label={`${q.id} ${opt}`}
                            />
                            {opt === 'yes' ? 'Yes' : opt === 'no' ? 'No' : 'Unknown'}
                          </label>
                        ))}
                      </div>
                    </fieldset>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="mt-8 rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,60%,7%)] p-5">
          <h3 className="text-sm font-semibold text-white">Summary</h3>
          <p className="mt-1 text-xs text-[hsl(215,20%,60%)]">No overall numeric score and no letter grade. Counts only.</p>
          <dl className="mt-4 grid grid-cols-3 gap-3 text-center">
            <div className="rounded-lg bg-[hsl(220,55%,9%)] border border-[hsl(215,40%,14%)] py-3">
              <dt className="text-xs text-[hsl(215,20%,60%)]">Yes</dt>
              <dd className="mt-1 text-xl font-semibold text-emerald-400 font-mono">{checklistSummary.yes}</dd>
            </div>
            <div className="rounded-lg bg-[hsl(220,55%,9%)] border border-[hsl(215,40%,14%)] py-3">
              <dt className="text-xs text-[hsl(215,20%,60%)]">No</dt>
              <dd className="mt-1 text-xl font-semibold text-red-400 font-mono">{checklistSummary.no}</dd>
            </div>
            <div className="rounded-lg bg-[hsl(220,55%,9%)] border border-[hsl(215,40%,14%)] py-3">
              <dt className="text-xs text-[hsl(215,20%,60%)]">Unknown</dt>
              <dd className="mt-1 text-xl font-semibold text-amber-300 font-mono">{checklistSummary.unknown}</dd>
            </div>
          </dl>

          <div className="mt-5 space-y-2">
            <h4 className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)]">Per group</h4>
            {CHECKLIST_GROUPS.map((g) => {
              const c = checklistSummary.perGroup[g.id];
              return (
                <div key={g.id} className="flex items-center justify-between text-xs text-slate-400 border-b border-[hsl(215,40%,14%)] py-1.5">
                  <span>{g.id}. {g.title}</span>
                  <span className="font-mono text-[hsl(215,20%,70%)]">{c.yes} yes / {c.no} no / {c.unknown} unknown</span>
                </div>
              );
            })}
          </div>

          <p className="mt-5 text-xs font-medium text-amber-200 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-2">
            Unknown counts as unresolved, not as a pass.
          </p>

          <div className="mt-5">
            <h4 className="text-sm font-semibold text-white">Questions to put to the manager or author</h4>
            {checklistSummary.openQuestions.length === 0 ? (
              <p className="mt-2 text-sm text-slate-400">All questions are answered Yes. There are no outstanding questions from this checklist.</p>
            ) : (
              <ul className="mt-2 space-y-2">
                {checklistSummary.openQuestions.map((q) => (
                  <li key={q.id} className="text-sm text-slate-300 leading-relaxed border-l-2 border-indigo-500/50 pl-3">
                    <span className="font-semibold text-slate-200">{q.id}.</span> {q.ask}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <p className="mt-5 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
            A checklist can help you ask better questions. It cannot by itself establish that a strategy works or will work in the future.
          </p>
        </div>
      </div>

      {/* Panel 2 */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white">Statistical sanity check</h2>
        <p className="mt-1 text-sm text-slate-400 leading-relaxed">Is this Sharpe ratio believable given the track length and distribution?</p>

        <div className="mt-5 grid gap-4">
          <div>
            <label htmlFor="sr-annual" className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)] mb-1.5 block">
              Annualised Sharpe ratio
            </label>
            <input
              id="sr-annual"
              type="number"
              step={0.1}
              value={sharpeAnnual}
              onChange={(e) => setSharpeAnnual(e.target.value)}
              className="w-full rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,60%,7%)] px-3 py-2 text-sm text-white placeholder:text-[hsl(215,20%,45%)] focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="ppy" className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)] mb-1.5 block">
                Periods per year
              </label>
              <select
                id="ppy"
                value={periodsPerYear}
                onChange={(e) => setPeriodsPerYear(Number(e.target.value) as PeriodsPerYear)}
                className="w-full rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,60%,7%)] px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
              >
                <option value={252}>252 daily</option>
                <option value={52}>52 weekly</option>
                <option value={12}>12 monthly</option>
              </select>
            </div>
            <div>
              <label htmlFor="years" className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)] mb-1.5 block">
                Years of history
              </label>
              <input
                id="years"
                type="number"
                step={0.5}
                min={0.5}
                value={years}
                onChange={(e) => setYears(e.target.value)}
                className="w-full rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,60%,7%)] px-3 py-2 text-sm text-white placeholder:text-[hsl(215,20%,45%)] focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
              />
              <p className="mt-1 text-xs text-[hsl(215,20%,45%)]">Minimum 0.5 years.</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="skew" className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)] mb-1.5 block">
                Skewness
              </label>
              <input
                id="skew"
                type="number"
                step={0.1}
                value={skewness}
                onChange={(e) => setSkewness(e.target.value)}
                className="w-full rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,60%,7%)] px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
              />
            </div>
            <div>
              <label htmlFor="kurt" className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)] mb-1.5 block">
                Kurtosis (non-excess)
              </label>
              <input
                id="kurt"
                type="number"
                step={0.1}
                value={kurtosis}
                onChange={(e) => setKurtosis(e.target.value)}
                className="w-full rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,60%,7%)] px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
              />
              <p className="mt-1 text-xs text-[hsl(215,20%,45%)]">3 is normal.</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="trials" className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)] mb-1.5 block">
                Variants tried (N)
              </label>
              <input
                id="trials"
                type="number"
                step={1}
                min={1}
                max={100000}
                value={trials}
                onChange={(e) => setTrials(e.target.value)}
                className="w-full rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,60%,7%)] px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
              />
            </div>
            <div>
              <label htmlFor="trial-std" className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)] mb-1.5 block">
                Std dev of trial Sharpes (annual, optional)
              </label>
              <input
                id="trial-std"
                type="number"
                step={0.1}
                value={trialStd}
                placeholder="blank = estimated"
                onChange={(e) => setTrialStd(e.target.value)}
                className="w-full rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,60%,7%)] px-3 py-2 text-sm text-white placeholder:text-[hsl(215,20%,45%)] focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {sanity.usedEstimatedVariance && (
          <p className="mt-4 text-xs text-amber-200/80 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-2">
            Using estimated variance 1/(T minus 1) for the trial Sharpes because no cross-trial standard deviation was supplied. This assumes the true Sharpe is zero and returns are normal.
          </p>
        )}

        <div className="mt-6 space-y-3">
          <h3 className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)]">Outputs</h3>

          <OutputRow label="Per-period Sharpe" value={fmt(sanity.perPeriodSharpe, 4)} interpretation={sanity.interpretations.perPeriodSharpe} />
          <OutputRow label="Standard error" value={fmt(sanity.standardError, 4)} sub="per period" interpretation={sanity.interpretations.standardError} />
          <OutputRow
            label="95% confidence interval (annual)"
            value={
              sanity.ciLowAnnual === null || sanity.ciHighAnnual === null
                ? '—'
                : `${fmt(sanity.ciLowAnnual, 2)} to ${fmt(sanity.ciHighAnnual, 2)}`
            }
            interpretation={sanity.interpretations.ci95}
          />
          <OutputRow label="Probabilistic Sharpe Ratio vs 0" value={fmtPct(sanity.psrVsZero)} interpretation={sanity.interpretations.psr} />
          <OutputRow
            label="Expected maximum Sharpe (SR0, annual)"
            value={fmt(sanity.expectedMaxSharpeAnnual, 2)}
            interpretation={sanity.interpretations.expectedMax}
          />
          <OutputRow label="Deflated Sharpe Ratio" value={fmtPct(sanity.deflatedSharpe)} interpretation={sanity.interpretations.dsr} />
          <OutputRow
            label="Minimum track record for 95% confidence"
            value={
              sanity.minTRLYears === null
                ? 'not attainable (Sharpe is not positive)'
                : `${fmt(sanity.minTRLYears, 1)} years (${sanity.minTRLObservations !== null ? Math.round(sanity.minTRLObservations) : '—'} obs.)`
            }
            interpretation={sanity.interpretations.minTRL}
          />
        </div>

        <div className="mt-6 border-t border-[hsl(215,40%,14%)] pt-4">
          <h4 className="text-xs font-semibold tracking-wide uppercase text-[hsl(215,20%,60%)] mb-2">Formulas</h4>
          <div className="font-mono text-xs text-slate-300 space-y-1">
            <p>SR_per = SR_annual / sqrt(periodsPerYear)</p>
            <p>D = 1 minus g3·SR_per + ((g4 minus 1)/4)·SR_per^2</p>
            <p>SE = sqrt(D / (T minus 1)), T = years × periodsPerYear</p>
            <p>CI95_annual = (SR_per -/+ 1.96·SE) × sqrt(periodsPerYear)</p>
            <p>PSR(SR*) = Phi((SR_per minus SR*) × sqrt(T minus 1) / sqrt(D))</p>
            <p>MinTRL = 1 + D × (PhiInv(0.95)/SR_per)^2 obs.</p>
            <p>SR0 via Bailey and Lopez de Prado (2014) Deflated Sharpe.</p>
          </div>
          <p className="mt-3 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
            Phi is the standard normal CDF and PhiInv its inverse. D must be positive; if not, the affected outputs show as unavailable.
          </p>
        </div>
      </div>
    </div>
  );
}

function OutputRow({
  label,
  value,
  sub,
  interpretation,
}: {
  label: string;
  value: string;
  sub?: string;
  interpretation: string;
}) {
  return (
    <div className="rounded-lg border border-[hsl(215,40%,14%)] bg-[hsl(220,60%,7%)] px-4 py-3">
      <div className="flex items-start justify-between gap-4">
        <dt className="text-sm text-[hsl(215,20%,60%)]">{label}</dt>
        <dd className="text-right shrink-0">
          <div className="text-sm font-semibold text-white font-mono">{value}</div>
          {sub && <div className="text-xs text-[hsl(215,20%,45%)] font-mono">{sub}</div>}
        </dd>
      </div>
      <p className="mt-2 text-xs text-slate-400 leading-relaxed">{interpretation}</p>
    </div>
  );
}
