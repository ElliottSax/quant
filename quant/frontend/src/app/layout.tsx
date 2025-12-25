import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'
import { Providers } from '@/lib/providers'
import { MobileMenu } from '@/components/ui/MobileMenu'
import { MarketTicker } from '@/components/ui/MarketTicker'

const inter = Inter({ subsets: ['latin'] })

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200"
    >
      {children}
    </Link>
  )
}

export const metadata: Metadata = {
  title: 'Quant Analytics Platform',
  description: 'Track government stock trades with statistical rigor',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-background">
            {/* Market Ticker */}
            <MarketTicker />

            {/* Navigation */}
            <nav className="sticky top-0 z-50 border-b border-border/50 glass-strong animate-fade-in-down">
              <div className="container mx-auto px-4">
                <div className="flex h-16 items-center justify-between">
                  <div className="flex items-center gap-8">
                    <Link href="/" className="text-xl font-bold hover:text-primary transition-colors flex items-center gap-2 group">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white font-bold group-hover:scale-110 transition-transform">
                        Q
                      </div>
                      <span>Quant Analytics</span>
                    </Link>
                    <div className="hidden md:flex items-center gap-1">
                      <NavLink href="/dashboard">Dashboard</NavLink>
                      <NavLink href="/politicians">Politicians</NavLink>
                      <NavLink href="/signals">Signals</NavLink>

                      {/* Quant Tools Dropdown - Simple approach */}
                      <div className="relative group">
                        <button className="px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200 flex items-center gap-1">
                          Quant Tools
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                        <div className="absolute top-full left-0 mt-1 w-56 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                          <div className="glass-strong rounded-lg border border-border/50 shadow-xl p-2 space-y-1">
                            <Link href="/charts" className="block px-3 py-2 rounded-lg text-sm hover:bg-primary/10 hover:text-primary transition-colors">
                              📊 Advanced Charts
                            </Link>
                            <Link href="/portfolio" className="block px-3 py-2 rounded-lg text-sm hover:bg-primary/10 hover:text-primary transition-colors">
                              💼 Portfolio Analyzer
                            </Link>
                            <Link href="/options" className="block px-3 py-2 rounded-lg text-sm hover:bg-primary/10 hover:text-primary transition-colors">
                              📈 Options Calculator
                            </Link>
                            <Link href="/scanner" className="block px-3 py-2 rounded-lg text-sm hover:bg-primary/10 hover:text-primary transition-colors">
                              🔍 Quant Scanner
                            </Link>
                            <Link href="/backtesting" className="block px-3 py-2 rounded-lg text-sm hover:bg-primary/10 hover:text-primary transition-colors">
                              ⚡ Backtesting Engine
                            </Link>
                            <Link href="/network" className="block px-3 py-2 rounded-lg text-sm hover:bg-primary/10 hover:text-primary transition-colors">
                              🕸️ Network Analysis
                            </Link>
                            <div className="border-t border-border/50 my-1" />
                            <Link href="/showcase" className="block px-3 py-2 rounded-lg text-sm hover:bg-primary/10 hover:text-primary transition-colors">
                              ✨ Chart Showcase
                            </Link>
                            <Link href="/tools" className="block px-3 py-2 rounded-lg text-sm hover:bg-primary/10 hover:text-primary transition-colors">
                              🛠️ Basic Tools
                            </Link>
                          </div>
                        </div>
                      </div>

                      <NavLink href="/resources">Resources</NavLink>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                      </span>
                      <span className="text-xs font-medium text-primary">Live</span>
                    </div>
                    <MobileMenu />
                  </div>
                </div>
              </div>
            </nav>

            {/* Main content */}
            <main className="container mx-auto px-4 py-8">{children}</main>

            {/* Footer */}
            <footer className="border-t border-border/50 mt-auto glass">
              <div className="container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white font-bold">
                        Q
                      </div>
                      <span className="font-bold">Quant Analytics</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Professional-grade analytics for Congressional stock trades
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-3 text-sm">Platform</h3>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li><Link href="/dashboard" className="hover:text-primary transition-colors">Dashboard</Link></li>
                      <li><Link href="/politicians" className="hover:text-primary transition-colors">Politicians</Link></li>
                      <li><Link href="/compare" className="hover:text-primary transition-colors">Compare</Link></li>
                      <li><Link href="/signals" className="hover:text-primary transition-colors">Trading Signals</Link></li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-3 text-sm">Quant Tools</h3>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li><Link href="/charts" className="hover:text-primary transition-colors">Advanced Charts</Link></li>
                      <li><Link href="/network" className="hover:text-primary transition-colors">Network Analysis</Link></li>
                      <li><Link href="/portfolio" className="hover:text-primary transition-colors">Portfolio Analyzer</Link></li>
                      <li><Link href="/scanner" className="hover:text-primary transition-colors">Quant Scanner</Link></li>
                      <li><Link href="/backtesting" className="hover:text-primary transition-colors">Backtesting</Link></li>
                      <li><Link href="/showcase" className="hover:text-primary transition-colors">Chart Showcase</Link></li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-3 text-sm">Resources</h3>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li><Link href="/resources" className="hover:text-primary transition-colors">Free Guides</Link></li>
                      <li><Link href="/resources" className="hover:text-primary transition-colors">Video Tutorials</Link></li>
                      <li><Link href="/resources" className="hover:text-primary transition-colors">Strategy Templates</Link></li>
                      <li><Link href="/resources" className="hover:text-primary transition-colors">Community</Link></li>
                    </ul>
                  </div>
                </div>

                <div className="border-t border-border/50 pt-6 text-center text-sm text-muted-foreground">
                  <p className="mb-2">
                    Quant Analytics Platform • Track government stock trades with statistical rigor
                  </p>
                  <p className="text-xs">
                    For research and transparency purposes only. Not financial advice.
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
