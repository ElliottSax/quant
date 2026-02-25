/**
 * Educational Resources & Lead Magnets Page
 * Free guides, tutorials, and downloadable content
 */

'use client'

import { useState } from 'react'
import { AnimatedCard } from '@/components/ui/AnimatedCard'

export default function ResourcesPage() {
  const [email, setEmail] = useState('')

  const freeGuides = [
    {
      title: 'Complete Guide to Congressional Trading Analysis',
      description: '50-page comprehensive guide on analyzing politician stock trades',
      downloadSize: '2.5 MB PDF',
      icon: '📚',
      gradient: 'from-blue-500 to-cyan-500',
      popular: true,
    },
    {
      title: 'Technical Indicators Cheat Sheet',
      description: 'Visual guide to 20+ technical indicators with setup instructions',
      downloadSize: '1.8 MB PDF',
      icon: '📊',
      gradient: 'from-purple-500 to-pink-500',
      popular: true,
    },
    {
      title: 'Backtesting Best Practices',
      description: 'Avoid common pitfalls and build robust trading strategies',
      downloadSize: '1.2 MB PDF',
      icon: '🔬',
      gradient: 'from-green-500 to-emerald-500',
      popular: false,
    },
    {
      title: 'Risk Management Framework',
      description: 'Professional risk management strategies used by institutions',
      downloadSize: '3.1 MB PDF',
      icon: '🛡️',
      gradient: 'from-orange-500 to-red-500',
      popular: true,
    },
  ]

  const tutorials = [
    {
      title: 'Building Your First Trading Strategy',
      duration: '15 min',
      level: 'Beginner',
      topics: ['Strategy design', 'Backtesting', 'Optimization'],
    },
    {
      title: 'Advanced Pattern Recognition',
      duration: '25 min',
      level: 'Advanced',
      topics: ['Chart patterns', 'Machine learning', 'Signal generation'],
    },
    {
      title: 'Portfolio Optimization Techniques',
      duration: '20 min',
      level: 'Intermediate',
      topics: ['Modern Portfolio Theory', 'Risk metrics', 'Efficient frontier'],
    },
  ]

  const templates = [
    {
      name: 'Mean Reversion Strategy Template',
      description: 'Pre-built mean reversion strategy with customizable parameters',
      icon: '🔄',
    },
    {
      name: 'Momentum Trading System',
      description: 'Follow trending stocks with built-in risk management',
      icon: '🚀',
    },
    {
      name: 'Pairs Trading Framework',
      description: 'Statistical arbitrage template for correlated assets',
      icon: '⚖️',
    },
  ]

  return (
    <div className="space-y-12">
      {/* Header */}
      <div className="animate-fade-in">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-4">
          <svg className="w-4 h-4 text-primary" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
          </svg>
          <span className="text-sm font-medium text-primary">Free Learning Resources</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Educational Resources
        </h1>
        <p className="text-lg text-muted-foreground max-w-3xl">
          Master quantitative trading with our free guides, video tutorials, and strategy templates.
          Everything you need to start analyzing stocks like a professional.
        </p>
      </div>

      {/* Lead Magnet - Free Report */}
      <div className="relative overflow-hidden">
        <div className="glass-strong rounded-2xl border border-primary/30 p-8 md:p-12 relative">
          {/* Background Gradient */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-primary/20 to-purple-500/20 rounded-full blur-3xl -z-10" />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-sm font-bold mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                FREE DOWNLOAD
              </div>
              <h2 className="text-3xl font-bold mb-4">2024 Congressional Trading Report</h2>
              <p className="text-lg text-muted-foreground mb-6">
                Get our exclusive 30-page report analyzing the most profitable Congressional trades of 2024.
                Includes sector analysis, timing patterns, and actionable insights.
              </p>
              <ul className="space-y-3 mb-8">
                {['Top 50 most profitable trades', 'Sector performance breakdown', 'Timing and seasonality analysis', 'Strategy recommendations'].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-sm">
                    <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
              <form onSubmit={(e) => { e.preventDefault(); alert('Report sent to ' + email); }} className="space-y-3">
                <div className="flex gap-3">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="input-field flex-1"
                    required
                  />
                  <button type="submit" className="btn-primary whitespace-nowrap">
                    <span className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Download Free
                    </span>
                  </button>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Instant download • No spam • 15,000+ downloads</span>
                </div>
              </form>
            </div>
            <div className="hidden md:flex items-center justify-center">
              <div className="relative">
                <div className="w-64 h-80 glass-strong rounded-2xl border border-border/50 p-6 rotate-6 hover:rotate-0 transition-transform duration-300">
                  <div className="text-6xl mb-4">📊</div>
                  <div className="space-y-2">
                    <div className="h-3 bg-primary/20 rounded"></div>
                    <div className="h-3 bg-primary/30 rounded w-3/4"></div>
                    <div className="h-3 bg-primary/20 rounded w-1/2"></div>
                  </div>
                </div>
                <div className="absolute -bottom-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center text-white font-bold shadow-lg">
                  FREE
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Free Guides */}
      <div>
        <h2 className="text-3xl font-bold mb-6">Free Guides & Ebooks</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {freeGuides.map((guide, idx) => (
            <div
              key={idx}
              className="glass-strong rounded-xl p-6 border border-border/50 hover:shadow-2xl hover:border-primary/30 transition-all duration-300 group animate-fade-in"
              style={{ animationDelay: `${idx * 100}ms`, animationFillMode: 'backwards' }}
            >
              {guide.popular && (
                <div className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold mb-4">
                  🔥 POPULAR
                </div>
              )}
              <div className="flex items-start gap-4">
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${guide.gradient} flex items-center justify-center text-3xl flex-shrink-0 group-hover:scale-110 transition-transform`}>
                  {guide.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold mb-2 group-hover:text-primary transition-colors">
                    {guide.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    {guide.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">{guide.downloadSize}</span>
                    <button className="text-sm font-semibold text-primary hover:underline flex items-center gap-1">
                      Download
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Video Tutorials */}
      <div>
        <h2 className="text-3xl font-bold mb-6">Video Tutorials</h2>
        <div className="space-y-4">
          {tutorials.map((tutorial, idx) => (
            <div
              key={idx}
              className="glass-strong rounded-xl p-6 border border-border/50 hover:shadow-xl hover:border-primary/30 transition-all duration-300 group"
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-4 flex-1">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                    <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold mb-1 group-hover:text-primary transition-colors">
                      {tutorial.title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {tutorial.duration}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                        tutorial.level === 'Beginner' ? 'bg-green-500/10 text-green-500' :
                        tutorial.level === 'Intermediate' ? 'bg-yellow-500/10 text-yellow-500' :
                        'bg-red-500/10 text-red-500'
                      }`}>
                        {tutorial.level}
                      </span>
                    </div>
                  </div>
                </div>
                <button className="btn-secondary whitespace-nowrap">
                  Watch Now
                </button>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {tutorial.topics.map((topic, i) => (
                  <span key={i} className="text-xs px-2 py-1 rounded-md bg-muted/30 text-muted-foreground">
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strategy Templates */}
      <div>
        <h2 className="text-3xl font-bold mb-6">Free Strategy Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {templates.map((template, idx) => (
            <div
              key={idx}
              className="glass-strong rounded-xl p-6 border border-border/50 hover:shadow-xl hover:border-primary/30 transition-all duration-300 text-center group"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-4xl mb-4 group-hover:scale-110 transition-transform">
                {template.icon}
              </div>
              <h3 className="text-lg font-bold mb-2 group-hover:text-primary transition-colors">
                {template.name}
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                {template.description}
              </p>
              <button className="btn-ghost w-full">
                Download Template
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Bonus Resources */}
      <div className="glass-strong rounded-xl p-8 border border-border/50">
        <h2 className="text-2xl font-bold mb-6 text-center">🎁 Bonus Resources</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <BonusCard
            title="Congressional Trade Alerts"
            description="Get email notifications when politicians make large trades"
            icon="🔔"
            cta="Enable Alerts"
          />
          <BonusCard
            title="Weekly Market Summary"
            description="Curated insights and top opportunities every Sunday"
            icon="📧"
            cta="Subscribe"
          />
          <BonusCard
            title="Strategy Database"
            description="Access 100+ tested trading strategies with performance data"
            icon="💾"
            cta="Browse Strategies"
          />
          <BonusCard
            title="Trading Checklist"
            description="Never miss a step with our pre-trade validation checklist"
            icon="✅"
            cta="Get Checklist"
          />
        </div>
      </div>

      {/* Community CTA */}
      <div className="glass-strong rounded-2xl border border-border/50 p-12 text-center relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-primary/20 to-purple-500/20 rounded-full blur-3xl -z-10" />

        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-4">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          <span className="text-sm font-medium text-primary">10,000+ Active Members</span>
        </div>

        <h2 className="text-3xl font-bold mb-4">Join Our Trading Community</h2>
        <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
          Get exclusive access to strategy discussions, weekly market analysis, and direct support from experienced traders.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8 max-w-2xl mx-auto">
          <CommunityFeature icon="💬" text="Active Discord" />
          <CommunityFeature icon="📊" text="Live Trading Sessions" />
          <CommunityFeature icon="🎓" text="Expert Mentorship" />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button className="btn-primary">
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
              </svg>
              Join Discord
            </span>
          </button>
          <button className="btn-secondary">
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              Get Newsletter
            </span>
          </button>
        </div>
      </div>
    </div>
  )
}

function BonusCard({ title, description, icon, cta }: { title: string; description: string; icon: string; cta: string }) {
  return (
    <div className="bg-card border border-border rounded-lg p-4 hover:border-primary/30 hover:shadow-lg transition-all group">
      <div className="flex items-start gap-3">
        <div className="text-3xl">{icon}</div>
        <div className="flex-1">
          <h4 className="font-bold mb-1 group-hover:text-primary transition-colors">{title}</h4>
          <p className="text-sm text-muted-foreground mb-3">{description}</p>
          <button className="text-sm font-semibold text-primary hover:underline">
            {cta} →
          </button>
        </div>
      </div>
    </div>
  )
}

function CommunityFeature({ icon, text }: { icon: string; text: string }) {
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="text-3xl">{icon}</div>
      <p className="text-sm font-medium">{text}</p>
    </div>
  )
}
