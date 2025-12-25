/**
 * Mobile Navigation Menu Component
 */

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export function MobileMenu() {
  const [isOpen, setIsOpen] = useState(false)
  const [quantToolsOpen, setQuantToolsOpen] = useState(false)
  const pathname = usePathname()

  const links = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/politicians', label: 'Politicians' },
    { href: '/signals', label: 'Signals' },
  ]

  const quantTools = [
    { href: '/charts', label: '📊 Advanced Charts' },
    { href: '/portfolio', label: '💼 Portfolio Analyzer' },
    { href: '/options', label: '📈 Options Calculator' },
    { href: '/scanner', label: '🔍 Quant Scanner' },
    { href: '/backtesting', label: '⚡ Backtesting Engine' },
    { href: '/tools', label: '🛠️ Basic Tools' },
  ]

  const bottomLinks = [
    { href: '/resources', label: 'Resources' },
  ]

  const isActive = (href: string) => pathname === href

  return (
    <div className="md:hidden">
      {/* Hamburger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative w-10 h-10 rounded-lg hover:bg-white/5 transition-colors flex items-center justify-center"
        aria-label="Toggle menu"
      >
        <div className="w-5 h-4 flex flex-col justify-between">
          <span
            className={`w-full h-0.5 bg-foreground transition-all duration-300 ${
              isOpen ? 'rotate-45 translate-y-1.5' : ''
            }`}
          />
          <span
            className={`w-full h-0.5 bg-foreground transition-all duration-300 ${
              isOpen ? 'opacity-0' : ''
            }`}
          />
          <span
            className={`w-full h-0.5 bg-foreground transition-all duration-300 ${
              isOpen ? '-rotate-45 -translate-y-2' : ''
            }`}
          />
        </div>
      </button>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 animate-fade-in"
            onClick={() => setIsOpen(false)}
          />

          {/* Menu Panel */}
          <div className="fixed top-16 right-0 left-0 mx-4 bg-card border border-border rounded-xl p-6 z-50 glass-strong animate-slide-in-right shadow-2xl max-h-[80vh] overflow-y-auto">
            <nav className="space-y-2">
              {/* Main links */}
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsOpen(false)}
                  className={`block px-4 py-3 rounded-lg font-medium transition-all ${
                    isActive(link.href)
                      ? 'bg-primary text-primary-foreground shadow-lg'
                      : 'text-foreground hover:bg-white/5 hover:text-primary'
                  }`}
                >
                  {link.label}
                </Link>
              ))}

              {/* Quant Tools Collapsible */}
              <div>
                <button
                  onClick={() => setQuantToolsOpen(!quantToolsOpen)}
                  className="w-full px-4 py-3 rounded-lg font-medium transition-all text-foreground hover:bg-white/5 hover:text-primary flex items-center justify-between"
                >
                  <span>Quant Tools</span>
                  <svg
                    className={`w-5 h-5 transition-transform ${quantToolsOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {quantToolsOpen && (
                  <div className="mt-1 space-y-1 pl-4 animate-fade-in">
                    {quantTools.map((tool) => (
                      <Link
                        key={tool.href}
                        href={tool.href}
                        onClick={() => setIsOpen(false)}
                        className={`block px-4 py-2 rounded-lg text-sm transition-all ${
                          isActive(tool.href)
                            ? 'bg-primary/20 text-primary font-semibold'
                            : 'text-muted-foreground hover:bg-white/5 hover:text-primary'
                        }`}
                      >
                        {tool.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              {/* Bottom links */}
              {bottomLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsOpen(false)}
                  className={`block px-4 py-3 rounded-lg font-medium transition-all ${
                    isActive(link.href)
                      ? 'bg-primary text-primary-foreground shadow-lg'
                      : 'text-foreground hover:bg-white/5 hover:text-primary'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>

            {/* Status Badge */}
            <div className="mt-6 pt-6 border-t border-border/50">
              <div className="flex items-center justify-center gap-2 px-3 py-2 rounded-full bg-primary/10 border border-primary/20">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                <span className="text-sm font-medium text-primary">System Live</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
