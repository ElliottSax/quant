'use client'

import Link from 'next/link'
import { AlertCircle, Mail, CheckCircle, Clock } from 'lucide-react'

export default function CorrectionsPolicyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Corrections
            <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent"> Policy</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            We're committed to accuracy and transparency. This page explains how we handle errors, corrections, and maintain quality standards.
          </p>
        </div>

        {/* Commitment Section */}
        <div className="bg-slate-800/30 border border-slate-700 rounded-xl p-8 mb-12">
          <div className="flex items-start gap-4">
            <CheckCircle className="w-8 h-8 text-green-400 flex-shrink-0 mt-1" />
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Our Commitment to Accuracy</h2>
              <p className="text-gray-300 mb-4">
                QuantEngines is built on the principle that accurate, reliable information is essential for informed trading decisions. We employ multiple verification processes to ensure our strategies, backtests, and supporting research are accurate and properly disclosed.
              </p>
              <p className="text-gray-300">
                However, we recognize that errors can occur. This policy outlines how we identify, correct, and communicate such errors.
              </p>
            </div>
          </div>
        </div>

        {/* Error Types */}
        <div className="bg-slate-800/20 border border-slate-700 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Types of Errors We Track</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/30 rounded-lg p-5 border border-slate-600">
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Data Errors</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>Incorrect historical OHLC data</li>
                <li>Incorrect dividend/split adjustments</li>
                <li>Missing trading days</li>
                <li>Data quality issues affecting backtests</li>
              </ul>
            </div>
            <div className="bg-slate-800/30 rounded-lg p-5 border border-slate-600">
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Calculation Errors</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>Incorrect Sharpe ratio computation</li>
                <li>Wrong win rate calculation</li>
                <li>Maximum drawdown miscalculation</li>
                <li>Incorrect average return reporting</li>
              </ul>
            </div>
            <div className="bg-slate-800/30 rounded-lg p-5 border border-slate-600">
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Parameter Errors</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>Incorrect default strategy parameters</li>
                <li>Parameter range mistakes</li>
                <li>Implementation inconsistencies</li>
                <li>Formula mismatches with academic sources</li>
              </ul>
            </div>
            <div className="bg-slate-800/30 rounded-lg p-5 border border-slate-600">
              <h3 className="text-lg font-semibold text-blue-400 mb-3">Content Errors</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>Incorrect research citations</li>
                <li>Typos or confusing language</li>
                <li>Broken links to academic sources</li>
                <li>Misleading descriptions</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Correction Process */}
        <div className="bg-slate-800/30 border border-slate-700 rounded-xl overflow-hidden mb-12">
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-600/10 px-6 py-4 border-b border-slate-700">
            <h2 className="text-2xl font-bold text-white">Correction Process</h2>
          </div>

          <div className="p-8">
            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-500/20 text-blue-400 font-bold">
                    1
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Error Detection & Verification</h3>
                  <p className="text-gray-300">
                    Errors are identified either through our internal validation processes or external reports. We immediately verify the error by:
                  </p>
                  <ul className="mt-2 ml-4 space-y-1 text-gray-300 text-sm">
                    <li>• Re-running backtests with current data</li>
                    <li>• Cross-checking calculations independently</li>
                    <li>• Consulting original research papers</li>
                    <li>• Testing edge cases and parameter ranges</li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-500/20 text-blue-400 font-bold">
                    2
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Assessment & Severity Rating</h3>
                  <p className="text-gray-300">
                    Errors are classified by severity:
                  </p>
                  <ul className="mt-2 ml-4 space-y-2 text-gray-300 text-sm">
                    <li><strong>Critical:</strong> Affects trading decisions or safety (corrected immediately, public notice issued)</li>
                    <li><strong>Major:</strong> Materially affects strategy performance (corrected within 24 hours)</li>
                    <li><strong>Minor:</strong> Typo or non-essential information (corrected within 1 week)</li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-500/20 text-blue-400 font-bold">
                    3
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Correction Implementation</h3>
                  <p className="text-gray-300">
                    Once verified, the error is corrected in the system. All affected data, strategies, and pages are updated. Updated backtests are re-run to ensure consistency.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-500/20 text-blue-400 font-bold">
                    4
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Transparent Communication</h3>
                  <p className="text-gray-300">
                    For critical and major errors, we issue a public correction notice explaining:
                  </p>
                  <ul className="mt-2 ml-4 space-y-1 text-gray-300 text-sm">
                    <li>• What the error was</li>
                    <li>• Why it occurred</li>
                    <li>• How it's been corrected</li>
                    <li>• What changed as a result</li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-500/20 text-blue-400 font-bold">
                    5
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Post-Correction Review</h3>
                  <p className="text-gray-300">
                    We review our processes to prevent similar errors. Documentation is updated, and team knowledge bases reflect lessons learned.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Reporting Errors */}
        <div className="bg-slate-800/30 border border-slate-700 rounded-xl p-8 mb-12">
          <div className="flex items-start gap-4">
            <Mail className="w-8 h-8 text-purple-400 flex-shrink-0 mt-1" />
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Found an Error? Report It</h2>
              <p className="text-gray-300 mb-6">
                We welcome error reports from our users. If you find something that seems incorrect, please report it to us immediately.
              </p>
              <div className="bg-slate-800/40 rounded-lg p-4 mb-6 border border-slate-600">
                <p className="text-gray-300 text-sm mb-3">
                  <strong>Email:</strong> <code className="bg-slate-900/50 px-2 py-1 rounded text-blue-300">errors@quantengines.com</code>
                </p>
                <p className="text-gray-300 text-sm">
                  Please include: what error you found, where you found it, what the correct information should be, and any relevant sources.
                </p>
              </div>
              <p className="text-gray-400 text-sm">
                We will acknowledge receipt of your report within 24 hours and keep you updated on our investigation.
              </p>
            </div>
          </div>
        </div>

        {/* Transparency Commits */}
        <div className="bg-slate-800/20 border border-slate-700 rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Our Transparency Commitments</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
              <span className="text-gray-300">
                <strong>No hiding errors.</strong> We maintain a public corrections log of all critical and major errors with their resolution.
              </span>
            </div>
            <div className="flex items-start gap-4">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
              <span className="text-gray-300">
                <strong>Clear methodology.</strong> All backtesting parameters, assumptions, and limitations are disclosed openly.
              </span>
            </div>
            <div className="flex items-start gap-4">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
              <span className="text-gray-300">
                <strong>Academic rigor.</strong> We cite peer-reviewed research and can be challenged on our methodologies.
              </span>
            </div>
            <div className="flex items-start gap-4">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
              <span className="text-gray-300">
                <strong>Continuous improvement.</strong> We actively seek feedback and update our processes based on identified gaps.
              </span>
            </div>
            <div className="flex items-start gap-4">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
              <span className="text-gray-300">
                <strong>Disclosure first.</strong> All limitations, edge cases, and risk factors are explained upfront, not hidden in small print.
              </span>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8">
          <div className="flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
            <div>
              <h2 className="text-xl font-bold text-white mb-3">Important Disclaimer</h2>
              <p className="text-gray-300">
                While we strive for accuracy, this corrections policy does not eliminate the inherent risks of trading. Historical performance, even when accurately reported, does not guarantee future results. Always use independent verification, proper risk management, and consult financial advisors before trading with real capital.
              </p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-12">
          <Link href="/strategy-validation">
            <button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold px-8 py-3 rounded-lg shadow-lg inline-flex items-center gap-2">
              Learn About Our Methodology
            </button>
          </Link>
        </div>
      </div>
    </div>
  )
}
