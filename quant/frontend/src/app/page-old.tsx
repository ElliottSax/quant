/**
 * Home/Landing Page
 */

import Link from 'next/link'

export default function Home() {
  return (
    <div className="space-y-16">
      {/* Hero section */}
      <div className="text-center py-16">
        <h1 className="text-5xl font-bold mb-6">
          Quant Analytics Platform
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
          Track and analyze Congressional stock trades with advanced statistical models,
          machine learning, and network analysis
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="px-6 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors"
          >
            View Dashboard
          </Link>
          <Link
            href="/politicians"
            className="px-6 py-3 bg-card border border-border font-semibold rounded-lg hover:bg-muted/50 transition-colors"
          >
            Browse Politicians
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <FeatureCard
          title="Ensemble Predictions"
          description="Multi-model predictions combining Fourier analysis, Hidden Markov Models, and Dynamic Time Warping with confidence scoring and automated insights."
          icon="📊"
        />
        <FeatureCard
          title="Pattern Detection"
          description="Identify cyclical trading patterns, regime changes, and historical precedents using advanced statistical methods and machine learning."
          icon="🔍"
        />
        <FeatureCard
          title="Network Analysis"
          description="Discover correlated trading behavior, central figures, and coordinated groups through sophisticated network graph analysis."
          icon="🕸️"
        />
        <FeatureCard
          title="Anomaly Detection"
          description="Automatically flag unusual trading patterns and potential insider trading with multi-model anomaly scoring."
          icon="⚠️"
        />
        <FeatureCard
          title="Correlation Analysis"
          description="Statistical correlation analysis with p-values and significance testing to identify synchronized trading patterns."
          icon="📈"
        />
        <FeatureCard
          title="Automated Insights"
          description="AI-generated insights with severity levels, confidence scores, and actionable recommendations for researchers."
          icon="🤖"
        />
      </div>

      {/* Technology stack */}
      <div className="bg-card border border-border rounded-lg p-8">
        <h2 className="text-2xl font-bold mb-6 text-center">Advanced Analytics & ML</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <TechItem title="Fourier Transform" subtitle="Cyclical Detection" />
          <TechItem title="Hidden Markov Models" subtitle="Regime Analysis" />
          <TechItem title="Dynamic Time Warping" subtitle="Pattern Matching" />
          <TechItem title="Network Graphs" subtitle="Correlation Networks" />
          <TechItem title="Ensemble Methods" subtitle="Meta-Learning" />
          <TechItem title="Statistical Tests" subtitle="Significance Analysis" />
          <TechItem title="Anomaly Detection" subtitle="Outlier Identification" />
          <TechItem title="Time Series" subtitle="Forecasting" />
        </div>
      </div>

      {/* CTA */}
      <div className="text-center bg-primary/5 border border-primary/20 rounded-lg p-12">
        <h2 className="text-3xl font-bold mb-4">Ready to Explore?</h2>
        <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
          Dive into comprehensive analytics, visualizations, and insights on Congressional trading activity
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="px-8 py-4 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors text-lg"
          >
            Get Started →
          </Link>
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  )
}

function TechItem({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="text-center">
      <p className="font-semibold text-sm">{title}</p>
      <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
    </div>
  )
}
