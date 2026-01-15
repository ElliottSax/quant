import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import Link from 'next/link'
import './globals.css'
import { Providers } from '@/lib/providers'
import { MobileMenu } from '@/components/ui/MobileMenu'
import { MarketTicker } from '@/components/ui/MarketTicker'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' })

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="px-3 py-1.5 text-sm font-medium text-[hsl(210,20%,65%)] hover:text-[hsl(45,96%,58%)] transition-colors duration-150"
    >
      {children}
    </Link>
  )
}

export const metadata: Metadata = {
  title: 'QuantEngines - Free Professional Trading Tools',
  description: 'Professional-grade quantitative analysis tools, charts, screeners, and backtesting - free and open to everyone',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans`}>
        <Providers>
          <div className="min-h-screen bg-[hsl(220,60%,4%)]">
            {/* Top Info Bar */}
            <div className="bg-gradient-to-r from-[hsl(220,60%,3%)] via-[hsl(215,50%,5%)] to-[hsl(220,60%,3%)] border-b border-[hsl(215,40%,12%)] py-1">
              <div className="container mx-auto px-4 flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-6 text-[hsl(210,20%,55%)]">
                  <span>Market Data</span>
                  <span className="text-[hsl(142,71%,55%)]">LIVE</span>
                  <Link href="/politicians" className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-[hsl(210,100%,56%)]/10 border border-[hsl(210,100%,56%)]/30 hover:bg-[hsl(210,100%,56%)]/20 transition-colors">
                    <span className="text-[hsl(210,100%,70%)]">Congressional Trades</span>
                    <span className="text-[hsl(142,71%,55%)]">NEW</span>
                  </Link>
                </div>
                <div className="flex items-center gap-4 text-[hsl(210,20%,55%)]">
                  <span>100% Free</span>
                  <span className="text-[hsl(45,96%,58%)]">No Signup Required</span>
                </div>
              </div>
            </div>

            {/* Market Ticker */}
            <MarketTicker />

            {/* Main Navigation */}
            <nav className="sticky top-0 z-50 bg-gradient-to-b from-[hsl(215,50%,10%)] to-[hsl(220,55%,7%)] border-b border-[hsl(215,40%,18%)]">
              <div className="container mx-auto px-4">
                <div className="flex h-12 items-center justify-between">
                  {/* Logo & Branding */}
                  <div className="flex items-center gap-8">
                    <Link href="/" className="flex items-center gap-2 group">
                      <div className="w-7 h-7 rounded bg-gradient-to-br from-[hsl(45,96%,58%)] to-[hsl(38,92%,45%)] flex items-center justify-center text-[hsl(220,60%,8%)] font-bold text-sm shadow-lg shadow-[hsl(45,96%,58%)]/20 group-hover:shadow-[hsl(45,96%,58%)]/40 transition-shadow">
                        Q
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-white leading-tight">QUANTENGINES</span>
                        <span className="text-[10px] text-[hsl(45,96%,58%)] uppercase tracking-widest leading-tight">Free Tools</span>
                      </div>
                    </Link>

                    {/* Primary Navigation - Quant Tools First */}
                    <div className="hidden md:flex items-center border-l border-[hsl(215,40%,18%)] pl-6">
                      <NavLink href="/charts">Charts</NavLink>
                      <NavLink href="/scanner">Screener</NavLink>
                      <NavLink href="/signals">Signals</NavLink>
                      <NavLink href="/backtesting">Backtest</NavLink>
                      <NavLink href="/portfolio">Portfolio</NavLink>

                      {/* More Tools Dropdown */}
                      <div className="relative group">
                        <button className="px-3 py-1.5 text-sm font-medium text-[hsl(210,20%,65%)] hover:text-[hsl(45,96%,58%)] transition-colors duration-150 flex items-center gap-1">
                          More
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                        <div className="absolute top-full left-0 mt-1 w-52 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-50">
                          <div className="bg-[hsl(220,55%,7%)] rounded border border-[hsl(215,40%,18%)] shadow-xl shadow-black/50 py-1">
                            <div className="px-3 py-1.5 text-[10px] font-semibold text-[hsl(45,96%,58%)] uppercase tracking-wider border-b border-[hsl(215,40%,16%)] mb-1">
                              Analysis Tools
                            </div>
                            <Link href="/options" className="block px-3 py-2 text-sm text-[hsl(210,20%,75%)] hover:bg-[hsl(215,50%,14%)] hover:text-white transition-colors">
                              Options Calculator
                            </Link>
                            <Link href="/network" className="block px-3 py-2 text-sm text-[hsl(210,20%,75%)] hover:bg-[hsl(215,50%,14%)] hover:text-white transition-colors">
                              Correlation Network
                            </Link>
                            <Link href="/compare" className="block px-3 py-2 text-sm text-[hsl(210,20%,75%)] hover:bg-[hsl(215,50%,14%)] hover:text-white transition-colors">
                              Stock Compare
                            </Link>
                            <Link href="/discoveries" className="block px-3 py-2 text-sm text-[hsl(210,20%,75%)] hover:bg-[hsl(215,50%,14%)] hover:text-white transition-colors">
                              Anomaly Detection
                            </Link>
                            <div className="border-t border-[hsl(215,40%,16%)] my-1" />
                            <div className="px-3 py-1.5 text-[10px] font-semibold text-[hsl(210,100%,56%)] uppercase tracking-wider">
                              Bonus: Insider Data
                            </div>
                            <Link href="/politicians" className="block px-3 py-2 text-sm text-[hsl(210,20%,75%)] hover:bg-[hsl(215,50%,14%)] hover:text-white transition-colors">
                              Congressional Trades
                            </Link>
                            <Link href="/dashboard" className="block px-3 py-2 text-sm text-[hsl(210,20%,75%)] hover:bg-[hsl(215,50%,14%)] hover:text-white transition-colors">
                              Insider Dashboard
                            </Link>
                            <div className="border-t border-[hsl(215,40%,16%)] my-1" />
                            <Link href="/showcase" className="block px-3 py-2 text-sm text-[hsl(210,20%,70%)] hover:bg-[hsl(215,50%,14%)] hover:text-white transition-colors">
                              Chart Showcase
                            </Link>
                            <Link href="/tools" className="block px-3 py-2 text-sm text-[hsl(210,20%,70%)] hover:bg-[hsl(215,50%,14%)] hover:text-white transition-colors">
                              All Tools
                            </Link>
                          </div>
                        </div>
                      </div>

                      <NavLink href="/resources">Learn</NavLink>
                    </div>
                  </div>

                  {/* Right Side - Quick Search & Status */}
                  <div className="flex items-center gap-4">
                    {/* Quick Ticker Search */}
                    <div className="hidden lg:flex items-center">
                      <div className="relative">
                        <input
                          type="text"
                          placeholder="Search ticker..."
                          className="w-32 px-2 py-1 text-xs font-mono bg-[hsl(220,55%,5%)] border border-[hsl(215,40%,20%)] rounded text-[hsl(210,20%,90%)] placeholder:text-[hsl(215,20%,40%)] focus:outline-none focus:border-[hsl(45,96%,58%)]/50 focus:w-40 transition-all"
                        />
                        <kbd className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-[hsl(215,20%,40%)] bg-[hsl(215,50%,14%)] px-1 rounded">
                          /
                        </kbd>
                      </div>
                    </div>

                    {/* Free Badge */}
                    <div className="hidden sm:flex items-center gap-2 px-2 py-1 rounded bg-[hsl(45,96%,58%)]/10 border border-[hsl(45,96%,58%)]/30">
                      <span className="text-xs font-bold text-[hsl(45,96%,58%)]">100% FREE</span>
                    </div>

                    <MobileMenu />
                  </div>
                </div>
              </div>
            </nav>

            {/* Secondary Navigation Tabs */}
            <div className="bg-[hsl(220,55%,5%)] border-b border-[hsl(215,40%,14%)]">
              <div className="container mx-auto px-4">
                <div className="flex items-center gap-1 py-1 overflow-x-auto scrollbar-thin">
                  <Link href="/charts" className="px-3 py-1 text-xs font-medium text-[hsl(210,20%,55%)] hover:text-[hsl(45,96%,58%)] hover:bg-[hsl(215,50%,12%)] rounded transition-colors whitespace-nowrap">
                    Live Charts
                  </Link>
                  <Link href="/scanner" className="px-3 py-1 text-xs font-medium text-[hsl(210,20%,55%)] hover:text-[hsl(45,96%,58%)] hover:bg-[hsl(215,50%,12%)] rounded transition-colors whitespace-nowrap">
                    Stock Screener
                  </Link>
                  <Link href="/signals" className="px-3 py-1 text-xs font-medium text-[hsl(210,20%,55%)] hover:text-[hsl(45,96%,58%)] hover:bg-[hsl(215,50%,12%)] rounded transition-colors whitespace-nowrap">
                    Trading Signals
                  </Link>
                  <Link href="/backtesting" className="px-3 py-1 text-xs font-medium text-[hsl(210,20%,55%)] hover:text-[hsl(45,96%,58%)] hover:bg-[hsl(215,50%,12%)] rounded transition-colors whitespace-nowrap">
                    Backtester
                  </Link>
                  <Link href="/options" className="px-3 py-1 text-xs font-medium text-[hsl(210,20%,55%)] hover:text-[hsl(45,96%,58%)] hover:bg-[hsl(215,50%,12%)] rounded transition-colors whitespace-nowrap">
                    Options
                  </Link>
                  <div className="flex-1" />
                  <span className="px-2 py-1 text-[10px] font-mono text-[hsl(215,20%,45%)]">
                    Professional Tools, Zero Cost
                  </span>
                </div>
              </div>
            </div>

            {/* Main content */}
            <main className="container mx-auto px-4 py-6">{children}</main>

            {/* Footer */}
            <footer className="border-t border-[hsl(215,40%,14%)] mt-auto bg-[hsl(220,60%,3%)]">
              <div className="container mx-auto px-4 py-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-6 h-6 rounded bg-gradient-to-br from-[hsl(45,96%,58%)] to-[hsl(38,92%,45%)] flex items-center justify-center text-[hsl(220,60%,8%)] font-bold text-xs">
                        Q
                      </div>
                      <span className="font-bold text-white text-sm">QUANTENGINES</span>
                    </div>
                    <p className="text-xs text-[hsl(215,20%,50%)] leading-relaxed">
                      Free professional-grade trading tools for everyone. Charts, screeners, backtesting, and more.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-3">Analysis Tools</h3>
                    <ul className="space-y-1.5 text-xs text-[hsl(210,20%,60%)]">
                      <li><Link href="/charts" className="hover:text-[hsl(45,96%,58%)] transition-colors">Advanced Charts</Link></li>
                      <li><Link href="/scanner" className="hover:text-[hsl(45,96%,58%)] transition-colors">Stock Screener</Link></li>
                      <li><Link href="/signals" className="hover:text-[hsl(45,96%,58%)] transition-colors">Trading Signals</Link></li>
                      <li><Link href="/backtesting" className="hover:text-[hsl(45,96%,58%)] transition-colors">Backtesting</Link></li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-3">More Tools</h3>
                    <ul className="space-y-1.5 text-xs text-[hsl(210,20%,60%)]">
                      <li><Link href="/portfolio" className="hover:text-[hsl(45,96%,58%)] transition-colors">Portfolio Analyzer</Link></li>
                      <li><Link href="/options" className="hover:text-[hsl(45,96%,58%)] transition-colors">Options Calculator</Link></li>
                      <li><Link href="/network" className="hover:text-[hsl(45,96%,58%)] transition-colors">Correlation Network</Link></li>
                      <li><Link href="/compare" className="hover:text-[hsl(45,96%,58%)] transition-colors">Stock Compare</Link></li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(210,100%,56%)] mb-3">Bonus: Insider Data</h3>
                    <ul className="space-y-1.5 text-xs text-[hsl(210,20%,60%)]">
                      <li><Link href="/politicians" className="hover:text-[hsl(45,96%,58%)] transition-colors">Congressional Trades</Link></li>
                      <li><Link href="/dashboard" className="hover:text-[hsl(45,96%,58%)] transition-colors">Insider Dashboard</Link></li>
                      <li><Link href="/discoveries" className="hover:text-[hsl(45,96%,58%)] transition-colors">Anomaly Detection</Link></li>
                      <li><Link href="/resources" className="hover:text-[hsl(45,96%,58%)] transition-colors">Learn More</Link></li>
                    </ul>
                  </div>
                </div>

                <div className="border-t border-[hsl(215,40%,14%)] pt-4 flex flex-col md:flex-row items-center justify-between gap-3">
                  <p className="text-[10px] text-[hsl(215,20%,45%)] font-mono">
                    QUANTENGINES v2.0 | Free Professional Trading Tools
                  </p>
                  <p className="text-[10px] text-[hsl(215,20%,40%)]">
                    For educational purposes only. Not financial advice.
                  </p>
                </div>
              </div>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  )
}
