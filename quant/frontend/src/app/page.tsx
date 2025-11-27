/**
 * Enhanced Home/Landing Page with modern design and animations
 */

'use client'

import Link from 'next/link'
import { AnimatedCard } from '@/components/ui/AnimatedCard'
import { GradientBackground } from '@/components/ui/GradientBackground'
import { useState, useEffect } from 'react'

export default function Home() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <>
      <GradientBackground />

      <div className="relative space-y-24 pb-16">
        {/* Hero section */}
        <section className="text-center py-20 px-4 animate-fade-in">
          <div className="max-w-5xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8 animate-scale-in">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              <span className="text-sm font-medium text-primary">Advanced ML Analytics Platform</span>
            </div>

            {/* Main heading with gradient */}
            <h1 className="text-6xl md:text-7xl font-bold mb-6 tracking-tight">
              <span className="gradient-text">Quant Analytics</span>
              <br />
              <span className="text-foreground">Platform</span>
            </h1>

            {/* Subheading */}
            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto mb-12 leading-relaxed">
              Track and analyze Congressional stock trades with{' '}
              <span className="text-foreground font-semibold">advanced statistical models</span>,{' '}
              <span className="text-foreground font-semibold">machine learning</span>, and{' '}
              <span className="text-foreground font-semibold">network analysis</span>
            </p>

            {/* CTA buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
              <Link href="/dashboard" className="btn-primary group">
                <span className="flex items-center gap-2">
                  View Dashboard
                  <svg
                    className="w-5 h-5 transition-transform group-hover:translate-x-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                </span>
              </Link>
              <Link href="/politicians" className="btn-secondary">
                Browse Politicians
              </Link>
            </div>

            {/* Stats banner */}
            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto pt-12 border-t border-border/50">
              <StatItem value="247+" label="Politicians" />
              <StatItem value="15K+" label="Trades Analyzed" />
              <StatItem value="99.9%" label="Accuracy" />
            </div>
          </div>
        </section>

        {/* Features grid */}
        <section className="px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Research-grade analytics tools powered by state-of-the-art machine learning
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <FeatureCard
                title="Trading Signals"
                description="AI-powered trading signals with 10+ technical indicators including RSI, MACD, Bollinger Bands, and real-time confidence scoring."
                icon="📊"
                gradient="from-blue-500 to-cyan-500"
                delay={0}
                href="/signals"
              />
              <FeatureCard
                title="Backtesting Engine"
                description="Test trading strategies on historical data with realistic market simulation, slippage modeling, and comprehensive performance metrics."
                icon="🔍"
                gradient="from-purple-500 to-pink-500"
                delay={100}
                href="/backtesting"
              />
              <FeatureCard
                title="Portfolio Optimization"
                description="Modern Portfolio Theory implementation with efficient frontier generation, risk metrics, and 6 optimization strategies."
                icon="💼"
                gradient="from-green-500 to-emerald-500"
                delay={200}
              />
              <FeatureCard
                title="Sentiment Analysis"
                description="Multi-source sentiment analysis powered by AI with keyword fallback, historical tracking, and confidence scoring."
                icon="⚠️"
                gradient="from-orange-500 to-red-500"
                delay={300}
              />
              <FeatureCard
                title="Market Data Integration"
                description="Real-time and historical market data from Yahoo Finance, Alpha Vantage, Polygon.io, and IEX Cloud with live quotes."
                icon="📈"
                gradient="from-teal-500 to-blue-500"
                delay={400}
              />
              <FeatureCard
                title="Automated Reporting"
                description="Scheduled reports in JSON, HTML, Markdown, and Text formats with email delivery and custom alert notifications."
                icon="🤖"
                gradient="from-indigo-500 to-purple-500"
                delay={500}
              />
            </div>
          </div>
        </section>

        {/* Technology stack showcase */}
        <section className="px-4">
          <div className="max-w-7xl mx-auto">
            <AnimatedCard variant="gradient" className="p-12">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold mb-4 text-white">Comprehensive Trading Analytics</h2>
                <p className="text-white/80">
                  Professional-grade algorithms and proven quantitative methods
                </p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                <TechItem title="Technical Indicators" subtitle="RSI, MACD, Bollinger" icon="📊" />
                <TechItem title="Modern Portfolio Theory" subtitle="Efficient Frontier" icon="💼" />
                <TechItem title="Backtesting Engine" subtitle="Strategy Validation" icon="🔄" />
                <TechItem title="Sentiment Analysis" subtitle="Market Psychology" icon="🧠" />
                <TechItem title="Risk Metrics" subtitle="Sharpe & Sortino" icon="⚖️" />
                <TechItem title="Real-time Data" subtitle="Live Market Feed" icon="⚡" />
                <TechItem title="WebSocket Streaming" subtitle="Real-time Signals" icon="📡" />
                <TechItem title="ML Predictions" subtitle="AI-Powered Insights" icon="🤖" />
              </div>
            </AnimatedCard>
          </div>
        </section>

        {/* Final CTA */}
        <section className="px-4">
          <div className="max-w-4xl mx-auto">
            <AnimatedCard variant="glass" className="text-center p-16 relative overflow-hidden">
              {/* Decorative elements */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full filter blur-3xl -z-10" />
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full filter blur-3xl -z-10" />

              <h2 className="text-4xl font-bold mb-6">Ready to Explore?</h2>
              <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
                Dive into comprehensive analytics, visualizations, and insights on Congressional trading activity
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/dashboard" className="btn-primary text-lg">
                  <span className="flex items-center gap-2">
                    Get Started
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 7l5 5m0 0l-5 5m5-5H6"
                      />
                    </svg>
                  </span>
                </Link>
                <Link href="/politicians" className="btn-ghost text-lg">
                  View Demo
                </Link>
              </div>
            </AnimatedCard>
          </div>
        </section>
      </div>
    </>
  )
}

interface FeatureCardProps {
  title: string
  description: string
  icon: string
  gradient: string
  delay: number
  href?: string
}

function FeatureCard({ title, description, icon, gradient, delay, href }: FeatureCardProps) {
  const content = (
    <>
      <div
        className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${gradient} text-white text-3xl mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300`}
      >
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-3 group-hover:text-primary transition-colors">
        {title}
      </h3>
      <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
      {href && (
        <div className="mt-4 text-primary text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          Explore <span>→</span>
        </div>
      )}
    </>
  );

  if (href) {
    return (
      <Link href={href}>
        <AnimatedCard variant="glass" className="group cursor-pointer h-full" delay={delay}>
          {content}
        </AnimatedCard>
      </Link>
    );
  }

  return (
    <AnimatedCard variant="glass" className="group" delay={delay}>
      {content}
    </AnimatedCard>
  );
}

interface TechItemProps {
  title: string
  subtitle: string
  icon: string
}

function TechItem({ title, subtitle, icon }: TechItemProps) {
  return (
    <div className="text-center p-4 rounded-lg hover:bg-white/10 transition-all duration-200 group">
      <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">{icon}</div>
      <p className="font-semibold text-sm mb-1 text-white group-hover:text-white/80 transition-colors">
        {title}
      </p>
      <p className="text-xs text-white/60">{subtitle}</p>
    </div>
  )
}

interface StatItemProps {
  value: string
  label: string
}

function StatItem({ value, label }: StatItemProps) {
  return (
    <div className="text-center">
      <p className="text-3xl font-bold mb-1 bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-500">
        {value}
      </p>
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  )
}
