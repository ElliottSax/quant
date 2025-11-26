import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'
import { Providers } from '@/lib/providers'

const inter = Inter({ subsets: ['latin'] })

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
            {/* Navigation */}
            <nav className="border-b border-border bg-card">
              <div className="container mx-auto px-4">
                <div className="flex h-16 items-center justify-between">
                  <div className="flex items-center gap-8">
                    <Link href="/" className="text-xl font-bold">
                      Quant Analytics
                    </Link>
                    <div className="hidden md:flex items-center gap-6 text-sm">
                      <Link
                        href="/dashboard"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                      >
                        Dashboard
                      </Link>
                      <Link
                        href="/politicians"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                      >
                        Politicians
                      </Link>
                      <Link
                        href="/analytics"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                      >
                        Analytics
                      </Link>
                      <Link
                        href="/network"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                      >
                        Network
                      </Link>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-xs text-muted-foreground">
                      Research Platform
                    </div>
                  </div>
                </div>
              </div>
            </nav>

            {/* Main content */}
            <main className="container mx-auto px-4 py-8">{children}</main>

            {/* Footer */}
            <footer className="border-t border-border mt-auto">
              <div className="container mx-auto px-4 py-6">
                <div className="text-center text-sm text-muted-foreground">
                  <p>
                    Quant Analytics Platform • Track government stock trades with statistical
                    rigor
                  </p>
                  <p className="mt-2 text-xs">
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
