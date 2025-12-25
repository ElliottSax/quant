/**
 * Enhanced Home/Landing Page with modern design and animations
 */

'use client'

import Link from 'next/link'
import { AnimatedCard } from '@/components/ui/AnimatedCard'
import { GradientBackground } from '@/components/ui/GradientBackground'
import { QuickTickerLookup } from '@/components/widgets/QuickTickerLookup'
import { MarketOverview } from '@/components/widgets/MarketOverview'
import { TopMovers } from '@/components/widgets/TopMovers'
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
              <Link href="/tools" className="btn-primary group">
                <span className="flex items-center gap-2">
                  Try Free Tools
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
              <Link href="/resources" className="btn-secondary">
                Get Free Reports
              </Link>
            </div>

            {/* Stats banner */}
            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto pt-12 border-t border-border/50">
              <StatItem value="15K+" label="Trades Tracked" />
              <StatItem value="50+" label="Free Tools" />
              <StatItem value="10K+" label="Active Users" />
            </div>
          </div>
        </section>

        {/* Interactive Widgets Section */}
        <section className="px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-12 animate-fade-in" style={{ animationDelay: '300ms', animationFillMode: 'backwards' }}>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20 mb-4">
                <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="text-sm font-medium text-green-500">Try It Now - No Signup Required</span>
              </div>
              <h2 className="text-4xl font-bold mb-4">Get Started Immediately</h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Start analyzing stocks right away with our free interactive tools
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-16">
              <div className="animate-fade-in" style={{ animationDelay: '400ms', animationFillMode: 'backwards' }}>
                <QuickTickerLookup />
              </div>
              <div className="animate-fade-in" style={{ animationDelay: '500ms', animationFillMode: 'backwards' }}>
                <MarketOverview />
              </div>
              <div className="animate-fade-in" style={{ animationDelay: '600ms', animationFillMode: 'backwards' }}>
                <TopMovers />
              </div>
            </div>
          </div>
        </section>

        {/* What You Get Section */}
        <section className="px-4">
          <div className="max-w-7xl mx-auto">
            <AnimatedCard variant="gradient" className="p-12 mb-16">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold mb-4 text-white">Everything You Need to Analyze Stocks</h2>
                <p className="text-white/80 text-lg">
                  100% Free Access • No Credit Card Required • Start Immediately
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <ValueProp icon="🔍" title="Stock Screener" description="Filter 10K+ stocks by any criteria" />
                <ValueProp icon="📊" title="Live Charts" description="Real-time price data with 20+ indicators" />
                <ValueProp icon="🧮" title="Calculators" description="Risk, position size, and P&L tools" />
                <ValueProp icon="📈" title="Pattern Scanner" description="Auto-detect chart patterns" />
                <ValueProp icon="🔄" title="Backtester" description="Test strategies on historical data" />
                <ValueProp icon="📚" title="Free Guides" description="50+ educational resources" />
                <ValueProp icon="🎯" title="Trading Signals" description="AI-powered buy/sell alerts" />
                <ValueProp icon="👥" title="Community" description="Join 10K+ active traders" />
              </div>
            </AnimatedCard>
          </div>
        </section>

        {/* Features grid */}
        <section className="px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">Professional Trading Tools</h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Access the same analytics tools used by hedge funds and institutional traders
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

        {/* Social Proof */}
        <section className="px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-4">Trusted by Traders Worldwide</h2>
              <p className="text-xl text-muted-foreground">
                Join thousands of traders using our platform daily
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <TestimonialCard
                quote="The stock screener is incredibly powerful. Found several opportunities I would have missed."
                author="Sarah M."
                role="Day Trader"
                rating={5}
              />
              <TestimonialCard
                quote="Best free backtesting tool I've found. Saved me thousands by validating strategies before risking real money."
                author="Michael R."
                role="Swing Trader"
                rating={5}
              />
              <TestimonialCard
                quote="The Congressional trading data is fascinating. Great for finding unusual market activity."
                author="Jennifer K."
                role="Analyst"
                rating={5}
              />
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="px-4">
          <div className="max-w-4xl mx-auto">
            <AnimatedCard variant="glass" className="text-center p-16 relative overflow-hidden">
              {/* Decorative elements */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full filter blur-3xl -z-10" />
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full filter blur-3xl -z-10" />

              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20 mb-6">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                <span className="text-sm font-medium text-green-500">100% Free Forever</span>
              </div>

              <h2 className="text-4xl font-bold mb-6">Start Analyzing Stocks Today</h2>
              <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
                Get instant access to professional-grade trading tools, real-time data, and comprehensive analytics.
                No signup required for basic tools.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
                <Link href="/tools" className="btn-primary text-lg">
                  <span className="flex items-center gap-2">
                    Try Tools Now
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
                <Link href="/resources" className="btn-secondary text-lg">
                  Download Free Guides
                </Link>
              </div>

              <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground">
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  No credit card
                </span>
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Instant access
                </span>
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Cancel anytime
                </span>
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

interface ValuePropProps {
  icon: string
  title: string
  description: string
}

function ValueProp({ icon, title, description }: ValuePropProps) {
  return (
    <div className="text-center p-4 rounded-lg hover:bg-white/10 transition-all duration-200 group">
      <div className="text-4xl mb-3 group-hover:scale-110 transition-transform">{icon}</div>
      <p className="font-bold text-sm mb-1 text-white">{title}</p>
      <p className="text-xs text-white/70">{description}</p>
    </div>
  )
}

interface TestimonialCardProps {
  quote: string
  author: string
  role: string
  rating: number
}

function TestimonialCard({ quote, author, role, rating }: TestimonialCardProps) {
  return (
    <AnimatedCard variant="glass" className="p-6 h-full">
      <div className="flex mb-3">
        {Array.from({ length: rating }).map((_, i) => (
          <svg key={i} className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
      <p className="text-sm mb-4 italic">"{quote}"</p>
      <div className="text-sm">
        <p className="font-semibold">{author}</p>
        <p className="text-muted-foreground text-xs">{role}</p>
      </div>
    </AnimatedCard>
  )
}
