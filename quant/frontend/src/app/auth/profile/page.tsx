'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function ProfilePage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchProfile = async () => {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          throw new Error('Failed to fetch profile')
        }

        const data = await response.json()
        setUser(data)
        setFormData({
          name: data.name,
          email: data.email,
        })
      } catch (err) {
        console.error(err)
        router.push('/auth/login')
      } finally {
        setIsLoading(false)
      }
    }

    fetchProfile()
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('token')
    router.push('/')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-[hsl(45,96%,58%)] border-t-transparent rounded-full"></div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Profile</h1>
          <p className="text-[hsl(215,20%,60%)]">Manage your account settings</p>
        </div>
        <Button
          onClick={handleLogout}
          variant="outline"
          className="border-red-500/30 text-red-400 hover:bg-red-500/10"
        >
          Logout
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white text-sm">Account Type</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)]">
              Free Tier
            </Badge>
          </CardContent>
        </Card>

        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white text-sm">API Calls</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">247</p>
            <p className="text-xs text-[hsl(215,20%,55%)]">This month</p>
          </CardContent>
        </Card>

        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white text-sm">Member Since</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-white">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
        <CardHeader>
          <CardTitle className="text-white">Personal Information</CardTitle>
          <CardDescription className="text-[hsl(215,20%,55%)]">
            Update your account details
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium text-[hsl(215,20%,70%)]">
              Full Name
            </label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              disabled={!isEditing}
              className="bg-[hsl(220,60%,4%)] border-[hsl(215,40%,20%)] text-white disabled:opacity-50"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium text-[hsl(215,20%,70%)]">
              Email Address
            </label>
            <Input
              id="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              disabled={!isEditing}
              className="bg-[hsl(220,60%,4%)] border-[hsl(215,40%,20%)] text-white disabled:opacity-50"
            />
          </div>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <Button
                  onClick={() => setIsEditing(false)}
                  className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)]"
                >
                  Save Changes
                </Button>
                <Button
                  onClick={() => setIsEditing(false)}
                  variant="outline"
                  className="border-[hsl(215,40%,20%)] text-[hsl(215,20%,60%)]"
                >
                  Cancel
                </Button>
              </>
            ) : (
              <Button
                onClick={() => setIsEditing(true)}
                className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)]"
              >
                Edit Profile
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
        <CardHeader>
          <CardTitle className="text-white">API Access</CardTitle>
          <CardDescription className="text-[hsl(215,20%,55%)]">
            Your API credentials
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-[hsl(215,20%,70%)]">
              API Key
            </label>
            <div className="flex gap-2">
              <Input
                value="••••••••••••••••••••••••••••••••"
                disabled
                className="bg-[hsl(220,60%,4%)] border-[hsl(215,40%,20%)] text-white font-mono"
              />
              <Button variant="outline" className="border-[hsl(215,40%,20%)] text-[hsl(215,20%,60%)]">
                Reveal
              </Button>
            </div>
          </div>
          <p className="text-xs text-[hsl(215,20%,55%)]">
            Keep your API key secure. Do not share it publicly.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
