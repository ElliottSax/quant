'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'

export function Navigation() {
  const pathname = usePathname()
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    setIsAuthenticated(!!token)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    router.push('/')
  }

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/politicians', label: 'Politicians' },
    { href: '/charts', label: 'Charts' },
    { href: '/landing', label: 'About' },
  ]

  return (
    <nav className="sticky top-0 z-50 bg-gradient-to-b from-[hsl(215,50%,10%)] to-[hsl(220,55%,7%)] border-b border-[hsl(215,40%,18%)]">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-[hsl(45,96%,58%)] to-[hsl(38,92%,45%)] flex items-center justify-center text-[hsl(220,60%,8%)] font-bold text-sm shadow-lg group-hover:shadow-[hsl(45,96%,58%)]/40 transition-shadow">
              Q
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-white leading-tight">QUANTENGINES</span>
              <span className="text-[9px] text-[hsl(45,96%,58%)] uppercase tracking-widest leading-tight">
                Congressional Trades
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`text-sm font-medium transition-colors ${
                  pathname === link.href
                    ? 'text-[hsl(45,96%,58%)]'
                    : 'text-[hsl(210,20%,65%)] hover:text-white'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Auth Buttons */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <Link href="/auth/profile">
                  <Button variant="ghost" size="sm" className="text-[hsl(210,20%,65%)] hover:text-white">
                    Profile
                  </Button>
                </Link>
                <Button
                  onClick={handleLogout}
                  size="sm"
                  variant="outline"
                  className="border-[hsl(215,40%,20%)] text-[hsl(215,20%,60%)] hover:bg-[hsl(215,50%,14%)]"
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/auth/login">
                  <Button variant="ghost" size="sm" className="text-[hsl(210,20%,65%)] hover:text-white">
                    Login
                  </Button>
                </Link>
                <Link href="/auth/register">
                  <Button
                    size="sm"
                    className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)]"
                  >
                    Sign Up
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 text-white"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-[hsl(215,40%,18%)]">
            <div className="flex flex-col gap-2">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsMenuOpen(false)}
                  className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                    pathname === link.href
                      ? 'bg-[hsl(45,96%,58%)]/10 text-[hsl(45,96%,58%)]'
                      : 'text-[hsl(210,20%,65%)] hover:bg-[hsl(215,50%,14%)]'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
              <div className="border-t border-[hsl(215,40%,18%)] my-2"></div>
              {isAuthenticated ? (
                <>
                  <Link
                    href="/auth/profile"
                    onClick={() => setIsMenuOpen(false)}
                    className="px-4 py-2 rounded text-sm font-medium text-[hsl(210,20%,65%)] hover:bg-[hsl(215,50%,14%)]"
                  >
                    Profile
                  </Link>
                  <button
                    onClick={() => {
                      handleLogout()
                      setIsMenuOpen(false)
                    }}
                    className="px-4 py-2 rounded text-sm font-medium text-left text-[hsl(210,20%,65%)] hover:bg-[hsl(215,50%,14%)]"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/auth/login"
                    onClick={() => setIsMenuOpen(false)}
                    className="px-4 py-2 rounded text-sm font-medium text-[hsl(210,20%,65%)] hover:bg-[hsl(215,50%,14%)]"
                  >
                    Login
                  </Link>
                  <Link
                    href="/auth/register"
                    onClick={() => setIsMenuOpen(false)}
                    className="px-4 py-2 rounded text-sm font-medium bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)]"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
