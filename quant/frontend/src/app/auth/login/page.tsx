'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const { api } = await import('@/lib/api')
      await api.login(email, password)
      router.push('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[hsl(220,60%,4%)] via-[hsl(220,55%,6%)] to-[hsl(220,60%,4%)] px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <div className="w-10 h-10 rounded bg-gradient-to-br from-[hsl(45,96%,58%)] to-[hsl(38,92%,45%)] flex items-center justify-center text-[hsl(220,60%,8%)] font-bold text-lg shadow-lg">
              Q
            </div>
            <span className="text-2xl font-bold text-white">QUANTENGINES</span>
          </Link>
          <p className="text-[hsl(215,20%,60%)] text-sm">
            Sign in to access your dashboard
          </p>
        </div>

        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white">Welcome back</CardTitle>
            <CardDescription className="text-[hsl(215,20%,55%)]">
              Enter your credentials to continue
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {error && (
                <div className="p-3 rounded bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                  {error}
                </div>
              )}
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-[hsl(215,20%,70%)]">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="bg-[hsl(220,60%,4%)] border-[hsl(215,40%,20%)] text-white placeholder:text-[hsl(215,20%,40%)]"
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="password" className="text-sm font-medium text-[hsl(215,20%,70%)]">
                    Password
                  </label>
                  <Link href="/auth/forgot-password" className="text-xs text-[hsl(45,96%,58%)] hover:underline">
                    Forgot password?
                  </Link>
                </div>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="bg-[hsl(220,60%,4%)] border-[hsl(215,40%,20%)] text-white placeholder:text-[hsl(215,20%,40%)]"
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-4">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)] font-semibold"
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </Button>
              <p className="text-sm text-center text-[hsl(215,20%,55%)]">
                Don&apos;t have an account?{' '}
                <Link href="/auth/register" className="text-[hsl(45,96%,58%)] hover:underline font-medium">
                  Sign up
                </Link>
              </p>
            </CardFooter>
          </form>
        </Card>

        <p className="text-xs text-center text-[hsl(215,20%,45%)] mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  )
}
