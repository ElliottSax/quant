'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function LandingPage() {
  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[hsl(45,96%,58%)]/10 via-transparent to-[hsl(210,100%,56%)]/10"></div>
        <div className="relative max-w-4xl mx-auto text-center space-y-8">
          <Badge className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] text-xs">
            Track Congressional Trading
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold text-white leading-tight">
            Follow the Money,
            <br />
            <span className="text-[hsl(45,96%,58%)]">Make Smarter Trades</span>
          </h1>
          <p className="text-xl text-[hsl(215,20%,65%)] max-w-2xl mx-auto">
            Track real-time congressional stock trades with institutional-grade analytics.
            Discover patterns, analyze performance, and gain insights from the market&apos;s most influential traders.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/dashboard">
              <Button size="lg" className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)] font-semibold text-lg px-8">
                Get Started Free
              </Button>
            </Link>
            <Link href="/politicians">
              <Button size="lg" variant="outline" className="border-[hsl(215,40%,20%)] text-white hover:bg-[hsl(215,50%,14%)]">
                View Politicians
              </Button>
            </Link>
          </div>
          <p className="text-sm text-[hsl(215,20%,55%)]">
            No credit card required • Free tier forever
          </p>
        </div>
      </section>

      {/* Features Grid */}
      <section className="space-y-12">
        <div className="text-center space-y-4">
          <h2 className="text-3xl md:text-4xl font-bold text-white">
            Powerful Features
          </h2>
          <p className="text-[hsl(215,20%,60%)] max-w-2xl mx-auto">
            Everything you need to track and analyze congressional trading patterns
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard
            icon="📊"
            title="Real-Time Trade Tracking"
            description="Get instant notifications when politicians make trades. Never miss important market movements."
          />
          <FeatureCard
            icon="🏛️"
            title="Politician Leaderboards"
            description="See top performers ranked by returns, trade frequency, and portfolio value."
          />
          <FeatureCard
            icon="📈"
            title="Advanced Analytics"
            description="Deep dive into trading patterns with ML-powered analysis and statistical insights."
          />
          <FeatureCard
            icon="🔔"
            title="Custom Alerts"
            description="Set up personalized alerts for specific politicians, stocks, or trading patterns."
          />
          <FeatureCard
            icon="🕸️"
            title="Network Analysis"
            description="Visualize trading correlations and discover hidden connections between politicians."
          />
          <FeatureCard
            icon="📱"
            title="Mobile-First Design"
            description="Access your dashboard anywhere with our responsive, mobile-optimized interface."
          />
        </div>
      </section>

      {/* Backtesting Platform Section */}
      <section className="space-y-12">
        <div className="text-center space-y-4">
          <Badge className="bg-[hsl(210,100%,56%)] text-white text-xs">
            No-Code Backtesting
          </Badge>
          <h2 className="text-3xl md:text-4xl font-bold text-white">
            Professional Backtesting Platform
          </h2>
          <p className="text-[hsl(215,20%,60%)] max-w-2xl mx-auto">
            Test trading strategies with real historical data. No coding required.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard icon="📋" title="10 Pre-Built Strategies" description="MA Crossover, RSI, MACD, Bollinger Bands, Momentum, and more ready to backtest." />
          <FeatureCard icon="📈" title="Real Market Data" description="Powered by Yahoo Finance with up to 10 years of historical price data." />
          <FeatureCard icon="💼" title="Portfolio Optimization" description="5 optimization methods including Max Sharpe, Min Variance, and Risk Parity." />
          <FeatureCard icon="📊" title="Risk Analytics" description="Sharpe ratio, drawdown analysis, rolling metrics, and trade distribution charts." />
          <FeatureCard icon="🔧" title="Strategy Builder" description="Create custom strategies with visual configuration - no coding needed." />
          <FeatureCard icon="🔄" title="Compare & Optimize" description="Save results, compare strategies side-by-side, and find the best approach." />
        </div>

        <div className="text-center">
          <Link href="/backtesting">
            <Button size="lg" className="bg-[hsl(210,100%,56%)] text-white hover:bg-[hsl(210,100%,65%)] font-semibold text-lg px-8">
              Try Backtesting Free
            </Button>
          </Link>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 border-y border-[hsl(215,40%,14%)]">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
          <StatCard value="500+" label="Politicians Tracked" />
          <StatCard value="10K+" label="Trades Monitored" />
          <StatCard value="$2.5B+" label="Total Trade Value" />
          <StatCard value="10" label="Trading Strategies" />
          <StatCard value="99.9%" label="Data Accuracy" />
        </div>
      </section>

      {/* Pricing Section */}
      <section className="space-y-12">
        <div className="text-center space-y-4">
          <h2 className="text-3xl md:text-4xl font-bold text-white">
            Simple, Transparent Pricing
          </h2>
          <p className="text-[hsl(215,20%,60%)] max-w-2xl mx-auto">
            Start free, upgrade when you need more
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <PricingCard
            name="Free"
            price="$0"
            description="Perfect for getting started"
            features={[
              '30 API calls/minute',
              'Basic statistics',
              '30-day historical data',
              'Public trade data',
              'Community support',
            ]}
            cta="Get Started"
            ctaLink="/auth/register"
          />
          <PricingCard
            name="Pro"
            price="$29"
            description="For serious traders"
            features={[
              '500 API calls/minute',
              'Advanced analytics',
              '5-year historical data',
              'ML predictions',
              'Email alerts',
              'Priority support',
            ]}
            cta="Start Free Trial"
            ctaLink="/auth/register"
            popular
          />
          <PricingCard
            name="Enterprise"
            price="Custom"
            description="For institutions"
            features={[
              'Unlimited API calls',
              'Custom integrations',
              'Full historical data',
              'Dedicated support',
              'SLA guarantee',
              'Custom features',
            ]}
            cta="Contact Sales"
            ctaLink="/contact"
          />
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 text-center space-y-8 bg-gradient-to-r from-[hsl(220,55%,7%)] to-[hsl(220,60%,5%)] rounded-lg border border-[hsl(215,40%,14%)]">
        <h2 className="text-3xl md:text-4xl font-bold text-white">
          Ready to Start Tracking?
        </h2>
        <p className="text-xl text-[hsl(215,20%,65%)] max-w-2xl mx-auto">
          Join thousands of traders who use QuantEngines to stay ahead of the market
        </p>
        <Link href="/auth/register">
          <Button size="lg" className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)] font-semibold text-lg px-8">
            Get Started Free
          </Button>
        </Link>
      </section>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] hover:border-[hsl(45,96%,58%)]/30 transition-colors">
      <CardHeader>
        <div className="text-4xl mb-2">{icon}</div>
        <CardTitle className="text-white">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-[hsl(215,20%,60%)] text-sm">{description}</p>
      </CardContent>
    </Card>
  )
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <p className="text-3xl md:text-4xl font-bold text-[hsl(45,96%,58%)] mb-2">{value}</p>
      <p className="text-sm text-[hsl(215,20%,60%)]">{label}</p>
    </div>
  )
}

function PricingCard({
  name,
  price,
  description,
  features,
  cta,
  ctaLink,
  popular,
}: {
  name: string
  price: string
  description: string
  features: string[]
  cta: string
  ctaLink: string
  popular?: boolean
}) {
  return (
    <Card className={`border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] ${popular ? 'ring-2 ring-[hsl(45,96%,58%)]' : ''}`}>
      <CardHeader>
        {popular && (
          <Badge className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] w-fit mb-2">
            Most Popular
          </Badge>
        )}
        <CardTitle className="text-white text-2xl">{name}</CardTitle>
        <CardDescription className="text-[hsl(215,20%,55%)]">{description}</CardDescription>
        <div className="mt-4">
          <span className="text-4xl font-bold text-white">{price}</span>
          {price !== 'Custom' && <span className="text-[hsl(215,20%,55%)]">/month</span>}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <ul className="space-y-2">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start gap-2 text-sm text-[hsl(215,20%,65%)]">
              <span className="text-green-500 mt-0.5">✓</span>
              {feature}
            </li>
          ))}
        </ul>
        <Link href={ctaLink}>
          <Button
            className={`w-full ${
              popular
                ? 'bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)]'
                : 'bg-[hsl(215,50%,14%)] text-white hover:bg-[hsl(215,50%,18%)]'
            }`}
          >
            {cta}
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}
