import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Free Congressional Trading Data API | QuantEngines',
  description: 'Free REST API for congressional stock trades, politician portfolios, and real-time market data. No API key required. Python, JavaScript, and cURL examples included.',
  keywords: [
    'congressional trading API',
    'free stock API',
    'politician trades API',
    'congress stock trades data',
    'free market data API',
    'stock quote API free',
    'congressional trading data',
    'STOCK Act API',
  ],
  openGraph: {
    title: 'Free Congressional Trading Data API | QuantEngines',
    description: 'Free REST API for congressional stock trades, politician portfolios, and real-time market data. No API key required.',
    url: 'https://quantengines.com/api-docs',
    type: 'website',
    images: [
      {
        url: 'https://quantengines.com/api/og?title=Free+Congressional+Trading+API',
        width: 1200,
        height: 630,
        alt: 'QuantEngines Free Congressional Trading API',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Free Congressional Trading Data API | QuantEngines',
    description: 'Free REST API for congressional stock trades. No API key required. Python, JS, and cURL examples.',
  },
  alternates: {
    canonical: '/api-docs',
  },
}

const BASE_URL = 'https://quantengines.com'

function CodeBlock({ language, code, label }: { language: string; code: string; label?: string }) {
  return (
    <div className="rounded-lg border border-[hsl(215,40%,16%)] overflow-hidden">
      {label && (
        <div className="flex items-center justify-between px-4 py-2 bg-[hsl(215,50%,10%)] border-b border-[hsl(215,40%,16%)]">
          <span className="text-[11px] font-mono text-[hsl(215,20%,55%)] uppercase tracking-wider">{label}</span>
        </div>
      )}
      <pre className="p-4 bg-[hsl(220,60%,3%)] overflow-x-auto text-sm font-mono leading-relaxed">
        <code className="text-[hsl(215,20%,75%)]">{code}</code>
      </pre>
    </div>
  )
}

function EndpointCard({
  method,
  path,
  description,
  parameters,
  response,
}: {
  method: string
  path: string
  description: string
  parameters: { name: string; type: string; required?: boolean; description: string }[]
  response: string
}) {
  return (
    <div id={path.replace(/[^a-zA-Z0-9]/g, '-').replace(/-+/g, '-')} className="terminal-panel scroll-mt-24">
      <div className="terminal-panel-header">
        <div className="flex items-center gap-3">
          <span className="px-2 py-0.5 rounded text-[11px] font-bold font-mono bg-green-500/20 text-green-400 border border-green-500/30">
            {method}
          </span>
          <code className="text-sm text-white font-mono">{path}</code>
        </div>
      </div>
      <div className="p-5 bg-[hsl(220,60%,4%)] space-y-5">
        <p className="text-sm text-[hsl(215,20%,70%)]">{description}</p>

        {parameters.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-3">Parameters</h4>
            <div className="rounded-lg border border-[hsl(215,40%,16%)] overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-[hsl(215,50%,10%)] text-[hsl(215,20%,60%)]">
                    <th className="text-left px-4 py-2 font-medium text-xs uppercase tracking-wider">Name</th>
                    <th className="text-left px-4 py-2 font-medium text-xs uppercase tracking-wider">Type</th>
                    <th className="text-left px-4 py-2 font-medium text-xs uppercase tracking-wider">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {parameters.map((param) => (
                    <tr key={param.name} className="border-t border-[hsl(215,40%,14%)]">
                      <td className="px-4 py-2.5">
                        <code className="text-[hsl(210,100%,70%)] font-mono text-xs">{param.name}</code>
                        {param.required && (
                          <span className="ml-2 text-[10px] text-red-400 font-semibold">REQUIRED</span>
                        )}
                      </td>
                      <td className="px-4 py-2.5">
                        <span className="text-xs text-[hsl(215,20%,55%)] font-mono">{param.type}</span>
                      </td>
                      <td className="px-4 py-2.5 text-xs text-[hsl(215,20%,65%)]">{param.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-3">Example Response</h4>
          <CodeBlock language="json" code={response} />
        </div>
      </div>
    </div>
  )
}

function SidebarLink({ href, children, indent }: { href: string; children: React.ReactNode; indent?: boolean }) {
  return (
    <a
      href={href}
      className={`block py-1.5 text-xs text-[hsl(215,20%,55%)] hover:text-[hsl(45,96%,58%)] transition-colors ${indent ? 'pl-4' : ''}`}
    >
      {children}
    </a>
  )
}

export default function ApiDocsPage() {
  return (
    <>
      {/* JSON-LD structured data for API documentation */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'TechArticle',
            headline: 'Free Congressional Trading Data API Documentation',
            description:
              'Complete API reference for accessing congressional stock trading data, politician portfolios, and real-time market quotes. Free, no authentication required.',
            url: `${BASE_URL}/api-docs`,
            author: {
              '@type': 'Organization',
              name: 'QuantEngines',
              url: BASE_URL,
            },
            publisher: {
              '@type': 'Organization',
              name: 'QuantEngines',
            },
            mainEntityOfPage: `${BASE_URL}/api-docs`,
            about: {
              '@type': 'WebAPI',
              name: 'QuantEngines Congressional Trading API',
              url: `${BASE_URL}/api/v1`,
              documentation: `${BASE_URL}/api-docs`,
              termsOfService: `${BASE_URL}/terms`,
              provider: {
                '@type': 'Organization',
                name: 'QuantEngines',
              },
            },
          }),
        }}
      />

      <div className="flex gap-8">
        {/* Sidebar Navigation */}
        <aside className="hidden lg:block w-56 flex-shrink-0 sticky top-20 self-start max-h-[calc(100vh-6rem)] overflow-y-auto">
          <div className="space-y-4">
            <div>
              <h3 className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-2">Getting Started</h3>
              <SidebarLink href="#overview">Overview</SidebarLink>
              <SidebarLink href="#base-url">Base URL</SidebarLink>
              <SidebarLink href="#authentication">Authentication</SidebarLink>
              <SidebarLink href="#rate-limits">Rate Limits</SidebarLink>
            </div>
            <div>
              <h3 className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-2">Endpoints</h3>
              <SidebarLink href="#-api-v1-trades-recent-list">Recent Trades</SidebarLink>
              <SidebarLink href="#-api-v1-politicians-">Politicians</SidebarLink>
              <SidebarLink href="#-api-v1-market-data-public-quote--symbol-">Stock Quote</SidebarLink>
              <SidebarLink href="#-api-v1-market-data-public-historical--symbol-">Historical Data</SidebarLink>
            </div>
            <div>
              <h3 className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-2">Examples</h3>
              <SidebarLink href="#code-examples">Code Examples</SidebarLink>
              <SidebarLink href="#python" indent>Python</SidebarLink>
              <SidebarLink href="#javascript" indent>JavaScript</SidebarLink>
              <SidebarLink href="#curl" indent>cURL</SidebarLink>
            </div>
            <div>
              <h3 className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-2">More</h3>
              <SidebarLink href="#premium">Premium Access</SidebarLink>
              <SidebarLink href="#support">Support</SidebarLink>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex-1 min-w-0 space-y-8">
          {/* Hero */}
          <div className="terminal-panel overflow-hidden">
            <div className="terminal-panel-header">
              <div className="flex items-center gap-3">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
                </span>
                <span>API DOCUMENTATION</span>
              </div>
              <span className="text-[10px] font-mono text-[hsl(215,20%,50%)]">v1.0</span>
            </div>
            <div className="p-8 bg-gradient-to-br from-[hsl(220,60%,4%)] via-[hsl(220,55%,6%)] to-[hsl(220,60%,4%)]">
              <h1 className="text-3xl md:text-4xl font-bold mb-4">
                <span className="text-white">Free Congressional</span>{' '}
                <span className="text-[hsl(45,96%,58%)]">Trading Data API</span>
              </h1>
              <p className="text-[hsl(215,20%,65%)] text-base md:text-lg max-w-2xl mb-6 leading-relaxed">
                Access real-time congressional stock trades, politician portfolios, and market data
                through our free REST API. Built for developers, researchers, and journalists.
              </p>
              <div className="flex flex-wrap gap-3">
                <span className="px-3 py-1.5 rounded-md text-xs font-semibold bg-green-500/15 text-green-400 border border-green-500/30">
                  No API Key Required
                </span>
                <span className="px-3 py-1.5 rounded-md text-xs font-semibold bg-blue-500/15 text-blue-400 border border-blue-500/30">
                  REST + JSON
                </span>
                <span className="px-3 py-1.5 rounded-md text-xs font-semibold bg-purple-500/15 text-purple-400 border border-purple-500/30">
                  20 req/min Free
                </span>
                <span className="px-3 py-1.5 rounded-md text-xs font-semibold bg-yellow-500/15 text-yellow-400 border border-yellow-500/30">
                  CORS Enabled
                </span>
              </div>
            </div>
          </div>

          {/* Overview */}
          <section id="overview" className="scroll-mt-20">
            <div className="terminal-panel">
              <div className="terminal-panel-header">
                <span>OVERVIEW</span>
              </div>
              <div className="p-5 bg-[hsl(220,60%,4%)] space-y-4 text-sm text-[hsl(215,20%,70%)] leading-relaxed">
                <p>
                  The QuantEngines API provides free, programmatic access to congressional stock trading
                  disclosures filed under the STOCK Act. Every trade reported by members of the U.S. Senate
                  and House of Representatives is parsed, normalized, and made available through simple REST endpoints.
                </p>
                <p>
                  Use this data to build trading tools, conduct academic research, create dashboards, or power
                  journalism investigations. No registration required for public endpoints.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                  <div className="p-4 rounded-lg bg-[hsl(215,50%,8%)] border border-[hsl(215,40%,16%)]">
                    <div className="text-2xl font-bold text-[hsl(45,96%,58%)] font-mono mb-1">500+</div>
                    <div className="text-xs text-[hsl(215,20%,55%)]">Politicians Tracked</div>
                  </div>
                  <div className="p-4 rounded-lg bg-[hsl(215,50%,8%)] border border-[hsl(215,40%,16%)]">
                    <div className="text-2xl font-bold text-green-400 font-mono mb-1">Daily</div>
                    <div className="text-xs text-[hsl(215,20%,55%)]">Data Updates</div>
                  </div>
                  <div className="p-4 rounded-lg bg-[hsl(215,50%,8%)] border border-[hsl(215,40%,16%)]">
                    <div className="text-2xl font-bold text-blue-400 font-mono mb-1">4</div>
                    <div className="text-xs text-[hsl(215,20%,55%)]">Public Endpoints</div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Base URL */}
          <section id="base-url" className="scroll-mt-20">
            <h2 className="text-lg font-bold text-white mb-3">Base URL</h2>
            <CodeBlock
              language="text"
              label="All requests"
              code={`${BASE_URL}/api/v1`}
            />
          </section>

          {/* Authentication */}
          <section id="authentication" className="scroll-mt-20">
            <div className="terminal-panel">
              <div className="terminal-panel-header">
                <div className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                  <span>AUTHENTICATION</span>
                </div>
              </div>
              <div className="p-5 bg-[hsl(220,60%,4%)] space-y-3 text-sm text-[hsl(215,20%,70%)]">
                <p>
                  <strong className="text-green-400">No API key required</strong> for public endpoints.
                  Simply make HTTP requests to any endpoint listed below.
                </p>
                <p>
                  Premium endpoints (webhooks, alerts, bulk export) require a Bearer token obtained
                  after signing up for a paid plan.
                </p>
                <CodeBlock
                  language="bash"
                  label="Premium authentication (optional)"
                  code={`# Only needed for premium endpoints
curl -H "Authorization: Bearer YOUR_API_KEY" \\
  ${BASE_URL}/api/v1/premium/alerts`}
                />
              </div>
            </div>
          </section>

          {/* Rate Limits */}
          <section id="rate-limits" className="scroll-mt-20">
            <div className="terminal-panel">
              <div className="terminal-panel-header">
                <span>RATE LIMITS</span>
              </div>
              <div className="p-5 bg-[hsl(220,60%,4%)]">
                <div className="rounded-lg border border-[hsl(215,40%,16%)] overflow-hidden">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-[hsl(215,50%,10%)] text-[hsl(215,20%,60%)]">
                        <th className="text-left px-4 py-2.5 font-medium text-xs uppercase tracking-wider">Plan</th>
                        <th className="text-left px-4 py-2.5 font-medium text-xs uppercase tracking-wider">Rate Limit</th>
                        <th className="text-left px-4 py-2.5 font-medium text-xs uppercase tracking-wider">Features</th>
                        <th className="text-left px-4 py-2.5 font-medium text-xs uppercase tracking-wider">Price</th>
                      </tr>
                    </thead>
                    <tbody className="text-[hsl(215,20%,70%)]">
                      <tr className="border-t border-[hsl(215,40%,14%)]">
                        <td className="px-4 py-3">
                          <span className="font-semibold text-green-400">Free</span>
                        </td>
                        <td className="px-4 py-3 font-mono text-xs">20 req/min</td>
                        <td className="px-4 py-3 text-xs">All public endpoints, JSON responses</td>
                        <td className="px-4 py-3 font-semibold text-green-400">$0</td>
                      </tr>
                      <tr className="border-t border-[hsl(215,40%,14%)]">
                        <td className="px-4 py-3">
                          <span className="font-semibold text-[hsl(45,96%,58%)]">Premium</span>
                        </td>
                        <td className="px-4 py-3 font-mono text-xs">200 req/min</td>
                        <td className="px-4 py-3 text-xs">Webhooks, alerts, bulk CSV export, historical archive</td>
                        <td className="px-4 py-3">
                          <Link href="/pricing" className="text-[hsl(45,96%,58%)] hover:underline">
                            See pricing
                          </Link>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-[hsl(215,20%,50%)] mt-3">
                  Rate limit headers are included in every response:{' '}
                  <code className="text-[hsl(210,100%,70%)]">X-RateLimit-Remaining</code>,{' '}
                  <code className="text-[hsl(210,100%,70%)]">X-RateLimit-Reset</code>
                </p>
              </div>
            </div>
          </section>

          {/* Endpoints */}
          <h2 className="text-xl font-bold text-white pt-4">Endpoints</h2>

          {/* Recent Trades */}
          <EndpointCard
            method="GET"
            path="/api/v1/trades/recent/list"
            description="Returns the most recent congressional stock trades, sorted by disclosure date. Includes transaction type, estimated amounts, and the filing politician."
            parameters={[
              { name: 'limit', type: 'integer', description: 'Number of trades to return. Default: 10, Max: 100' },
              { name: 'skip', type: 'integer', description: 'Offset for pagination. Default: 0' },
            ]}
            response={`{
  "trades": [
    {
      "id": "txn_2024_0918_pelosi_nvda",
      "politician": "Nancy Pelosi",
      "politician_id": "P000197",
      "chamber": "house",
      "party": "Democrat",
      "ticker": "NVDA",
      "company": "NVIDIA Corporation",
      "transaction_type": "purchase",
      "amount_range": "$1,000,001 - $5,000,000",
      "disclosure_date": "2024-09-18",
      "transaction_date": "2024-09-12",
      "asset_type": "Stock",
      "comment": null
    },
    {
      "id": "txn_2024_0917_tuberville_ba",
      "politician": "Tommy Tuberville",
      "politician_id": "T000278",
      "chamber": "senate",
      "party": "Republican",
      "ticker": "BA",
      "company": "The Boeing Company",
      "transaction_type": "sale_full",
      "amount_range": "$100,001 - $250,000",
      "disclosure_date": "2024-09-17",
      "transaction_date": "2024-09-10",
      "asset_type": "Stock",
      "comment": null
    }
  ],
  "total": 14832,
  "limit": 10,
  "skip": 0
}`}
          />

          {/* Politicians */}
          <EndpointCard
            method="GET"
            path="/api/v1/politicians/"
            description="List all tracked politicians with their chamber, party, and trading activity summary. Filter by chamber or party affiliation."
            parameters={[
              { name: 'chamber', type: 'string', description: 'Filter by chamber: "senate" or "house"' },
              { name: 'party', type: 'string', description: 'Filter by party: "Democrat", "Republican", or "Independent"' },
              { name: 'limit', type: 'integer', description: 'Number of results to return. Default: 50, Max: 200' },
              { name: 'skip', type: 'integer', description: 'Offset for pagination. Default: 0' },
            ]}
            response={`{
  "politicians": [
    {
      "id": "P000197",
      "name": "Nancy Pelosi",
      "chamber": "house",
      "party": "Democrat",
      "state": "CA",
      "district": 11,
      "total_trades": 237,
      "total_volume_estimate": "$15,000,000+",
      "last_trade_date": "2024-09-12",
      "top_tickers": ["NVDA", "AAPL", "MSFT", "GOOGL", "RBLX"]
    },
    {
      "id": "T000278",
      "name": "Tommy Tuberville",
      "chamber": "senate",
      "party": "Republican",
      "state": "AL",
      "district": null,
      "total_trades": 482,
      "total_volume_estimate": "$8,200,000+",
      "last_trade_date": "2024-09-10",
      "top_tickers": ["BA", "GE", "TSLA", "META", "AMZN"]
    }
  ],
  "total": 538,
  "limit": 50,
  "skip": 0
}`}
          />

          {/* Stock Quote */}
          <EndpointCard
            method="GET"
            path="/api/v1/market-data/public/quote/{symbol}"
            description="Get a real-time stock quote for any US-listed equity. Returns the latest price, volume, change, and basic company info."
            parameters={[
              { name: 'symbol', type: 'string', required: true, description: 'Stock ticker symbol, e.g. "AAPL", "NVDA"' },
            ]}
            response={`{
  "symbol": "NVDA",
  "company_name": "NVIDIA Corporation",
  "price": 138.27,
  "change": 4.52,
  "change_percent": 3.38,
  "volume": 312849100,
  "market_cap": 3400000000000,
  "pe_ratio": 67.4,
  "week_52_high": 152.89,
  "week_52_low": 39.23,
  "timestamp": "2024-09-18T16:00:00Z"
}`}
          />

          {/* Historical Data */}
          <EndpointCard
            method="GET"
            path="/api/v1/market-data/public/historical/{symbol}"
            description="Retrieve historical OHLCV price data for a given stock symbol. Perfect for charting, backtesting, or correlating with congressional trade timing."
            parameters={[
              { name: 'symbol', type: 'string', required: true, description: 'Stock ticker symbol, e.g. "AAPL"' },
              { name: 'period', type: 'string', description: 'Time period: "1mo", "3mo", "6mo", "1y", "5y". Default: "3mo"' },
              { name: 'interval', type: 'string', description: 'Data interval: "1d", "1wk", "1mo". Default: "1d"' },
            ]}
            response={`{
  "symbol": "NVDA",
  "interval": "1d",
  "period": "3mo",
  "data": [
    {
      "date": "2024-09-18",
      "open": 134.50,
      "high": 139.20,
      "low": 133.82,
      "close": 138.27,
      "volume": 312849100
    },
    {
      "date": "2024-09-17",
      "open": 131.10,
      "high": 134.92,
      "low": 130.44,
      "close": 133.75,
      "volume": 245612800
    }
  ],
  "total_points": 63
}`}
          />

          {/* Code Examples */}
          <section id="code-examples" className="scroll-mt-20 space-y-6">
            <h2 className="text-xl font-bold text-white">Code Examples</h2>
            <p className="text-sm text-[hsl(215,20%,65%)]">
              Copy-paste examples to start pulling congressional trading data in seconds.
            </p>

            {/* Python */}
            <div id="python" className="scroll-mt-20">
              <h3 className="text-sm font-semibold text-[hsl(210,100%,70%)] mb-3 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                Python
              </h3>
              <CodeBlock
                language="python"
                label="python - requests"
                code={`import requests

# Get the latest congressional trades
response = requests.get("${BASE_URL}/api/v1/trades/recent/list", params={
    "limit": 25
})
trades = response.json()

for trade in trades["trades"]:
    print(f"{trade['politician']} {trade['transaction_type']} "
          f"{trade['ticker']} ({trade['amount_range']})")

# Get all senators' trading activity
senators = requests.get("${BASE_URL}/api/v1/politicians/", params={
    "chamber": "senate",
    "limit": 100
}).json()

# Get a stock quote for a recently traded ticker
quote = requests.get(
    f"${BASE_URL}/api/v1/market-data/public/quote/NVDA"
).json()
print(f"NVDA: \${quote['price']} ({quote['change_percent']:+.2f}%)")`}
              />
            </div>

            {/* JavaScript */}
            <div id="javascript" className="scroll-mt-20">
              <h3 className="text-sm font-semibold text-yellow-400 mb-3 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                JavaScript
              </h3>
              <CodeBlock
                language="javascript"
                label="javascript - fetch"
                code={`// Get recent congressional trades
const response = await fetch(
  "${BASE_URL}/api/v1/trades/recent/list?limit=25"
);
const { trades } = await response.json();

trades.forEach(trade => {
  console.log(
    \`\${trade.politician} \${trade.transaction_type} \` +
    \`\${trade.ticker} (\${trade.amount_range})\`
  );
});

// Get historical data to correlate with trade timing
const history = await fetch(
  "${BASE_URL}/api/v1/market-data/public/historical/NVDA?period=6mo"
).then(r => r.json());

console.log(\`Got \${history.total_points} data points for \${history.symbol}\`);`}
              />
            </div>

            {/* cURL */}
            <div id="curl" className="scroll-mt-20">
              <h3 className="text-sm font-semibold text-green-400 mb-3 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-green-500"></span>
                cURL
              </h3>
              <CodeBlock
                language="bash"
                label="curl"
                code={`# Recent trades
curl -s "${BASE_URL}/api/v1/trades/recent/list?limit=5" | jq .

# Filter politicians by chamber
curl -s "${BASE_URL}/api/v1/politicians/?chamber=senate&limit=10" | jq .

# Real-time quote
curl -s "${BASE_URL}/api/v1/market-data/public/quote/AAPL" | jq .

# Historical price data
curl -s "${BASE_URL}/api/v1/market-data/public/historical/TSLA?period=1y&interval=1wk" | jq .`}
              />
            </div>
          </section>

          {/* Error Codes */}
          <section className="scroll-mt-20">
            <div className="terminal-panel">
              <div className="terminal-panel-header">
                <span>ERROR CODES</span>
              </div>
              <div className="p-5 bg-[hsl(220,60%,4%)]">
                <div className="rounded-lg border border-[hsl(215,40%,16%)] overflow-hidden">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-[hsl(215,50%,10%)] text-[hsl(215,20%,60%)]">
                        <th className="text-left px-4 py-2 font-medium text-xs uppercase tracking-wider">Status</th>
                        <th className="text-left px-4 py-2 font-medium text-xs uppercase tracking-wider">Meaning</th>
                      </tr>
                    </thead>
                    <tbody className="text-[hsl(215,20%,70%)]">
                      <tr className="border-t border-[hsl(215,40%,14%)]">
                        <td className="px-4 py-2.5"><code className="text-green-400 font-mono">200</code></td>
                        <td className="px-4 py-2.5 text-xs">Success</td>
                      </tr>
                      <tr className="border-t border-[hsl(215,40%,14%)]">
                        <td className="px-4 py-2.5"><code className="text-yellow-400 font-mono">400</code></td>
                        <td className="px-4 py-2.5 text-xs">Bad request - check your parameters</td>
                      </tr>
                      <tr className="border-t border-[hsl(215,40%,14%)]">
                        <td className="px-4 py-2.5"><code className="text-yellow-400 font-mono">404</code></td>
                        <td className="px-4 py-2.5 text-xs">Resource not found (invalid symbol, politician ID, etc.)</td>
                      </tr>
                      <tr className="border-t border-[hsl(215,40%,14%)]">
                        <td className="px-4 py-2.5"><code className="text-red-400 font-mono">429</code></td>
                        <td className="px-4 py-2.5 text-xs">Rate limit exceeded - wait and retry, or upgrade your plan</td>
                      </tr>
                      <tr className="border-t border-[hsl(215,40%,14%)]">
                        <td className="px-4 py-2.5"><code className="text-red-400 font-mono">500</code></td>
                        <td className="px-4 py-2.5 text-xs">Server error - please report if persistent</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </section>

          {/* Premium CTA */}
          <section id="premium" className="scroll-mt-20">
            <div className="terminal-panel border-[hsl(45,96%,58%)]/30">
              <div className="terminal-panel-header bg-gradient-to-r from-[hsl(45,96%,20%)] to-transparent">
                <div className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[hsl(45,96%,58%)] animate-pulse"></span>
                  <span className="text-[hsl(45,96%,58%)]">PREMIUM API ACCESS</span>
                </div>
              </div>
              <div className="p-6 bg-[hsl(220,60%,4%)]">
                <h3 className="text-xl font-bold text-white mb-3">Need more from the API?</h3>
                <p className="text-sm text-[hsl(215,20%,65%)] mb-5 max-w-2xl">
                  Upgrade to Premium for higher rate limits, webhook notifications when politicians file new trades,
                  real-time alerts, bulk CSV exports, and full historical archive access.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div className="p-3 rounded-lg bg-[hsl(215,50%,8%)] border border-[hsl(215,40%,16%)]">
                    <div className="text-lg font-bold text-[hsl(45,96%,58%)] font-mono">200/min</div>
                    <div className="text-xs text-[hsl(215,20%,55%)]">API Rate Limit</div>
                  </div>
                  <div className="p-3 rounded-lg bg-[hsl(215,50%,8%)] border border-[hsl(215,40%,16%)]">
                    <div className="text-lg font-bold text-[hsl(45,96%,58%)] font-mono">Webhooks</div>
                    <div className="text-xs text-[hsl(215,20%,55%)]">Real-time Notifications</div>
                  </div>
                  <div className="p-3 rounded-lg bg-[hsl(215,50%,8%)] border border-[hsl(215,40%,16%)]">
                    <div className="text-lg font-bold text-[hsl(45,96%,58%)] font-mono">CSV</div>
                    <div className="text-xs text-[hsl(215,20%,55%)]">Bulk Data Export</div>
                  </div>
                  <div className="p-3 rounded-lg bg-[hsl(215,50%,8%)] border border-[hsl(215,40%,16%)]">
                    <div className="text-lg font-bold text-[hsl(45,96%,58%)] font-mono">Alerts</div>
                    <div className="text-xs text-[hsl(215,20%,55%)]">Trade Notifications</div>
                  </div>
                </div>
                <Link
                  href="/pricing"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-[hsl(45,96%,58%)] to-[hsl(38,92%,45%)] text-[hsl(220,60%,8%)] font-bold text-sm hover:shadow-lg hover:shadow-[hsl(45,96%,58%)]/20 transition-all"
                >
                  View Premium Plans
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>
              </div>
            </div>
          </section>

          {/* Support */}
          <section id="support" className="scroll-mt-20">
            <div className="terminal-panel">
              <div className="terminal-panel-header">
                <span>SUPPORT & COMMUNITY</span>
              </div>
              <div className="p-5 bg-[hsl(220,60%,4%)] text-sm text-[hsl(215,20%,70%)] space-y-3">
                <p>
                  Found a bug or have a feature request? We welcome contributions and feedback.
                </p>
                <div className="flex flex-wrap gap-4">
                  <a
                    href="mailto:api@quantengines.com"
                    className="px-4 py-2 rounded-lg bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] hover:border-[hsl(45,96%,58%)]/50 text-xs font-medium text-white transition-colors"
                  >
                    api@quantengines.com
                  </a>
                  <Link
                    href="/"
                    className="px-4 py-2 rounded-lg bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] hover:border-[hsl(45,96%,58%)]/50 text-xs font-medium text-white transition-colors"
                  >
                    QuantEngines Dashboard
                  </Link>
                </div>
              </div>
            </div>
          </section>

          {/* Footer attribution for SEO */}
          <div className="text-center py-6 text-xs text-[hsl(215,20%,40%)]">
            <p>
              QuantEngines Congressional Trading API -- Free for developers, researchers, and journalists.
            </p>
            <p className="mt-1">
              Data sourced from public STOCK Act filings. Updated daily.
            </p>
          </div>
        </div>
      </div>
    </>
  )
}
