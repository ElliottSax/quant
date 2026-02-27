'use client'

import Link from 'next/link'
import { CreditCard, Share2, Bell, Lock, Palette, HelpCircle, LogOut } from 'lucide-react'

export default function SettingsPage() {
  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/auth/login'
  }

  const settings = [
    {
      title: 'Subscription',
      description: 'Manage your subscription tier and billing',
      icon: CreditCard,
      href: '/settings/subscription',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      title: 'Referral Program',
      description: 'Share your code and earn credits',
      icon: Share2,
      href: '/settings/referral',
      color: 'from-green-500 to-emerald-500',
    },
    {
      title: 'Notifications',
      description: 'Manage email alerts and notifications',
      icon: Bell,
      href: '/settings/notifications',
      color: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Security',
      description: 'Two-factor auth and password management',
      icon: Lock,
      href: '/settings/security',
      color: 'from-red-500 to-orange-500',
    },
    {
      title: 'Appearance',
      description: 'Dark mode, themes, and display options',
      icon: Palette,
      href: '/settings/appearance',
      color: 'from-indigo-500 to-purple-500',
    },
    {
      title: 'Help & Support',
      description: 'FAQs, contact support, and documentation',
      icon: HelpCircle,
      href: '/settings/help',
      color: 'from-yellow-500 to-orange-500',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account, subscription, and preferences</p>
        </div>

        {/* Settings Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {settings.map((setting) => {
            const Icon = setting.icon
            return (
              <Link
                key={setting.href}
                href={setting.href}
                className="group block"
              >
                <div className="bg-slate-800/50 hover:bg-slate-800 border border-slate-700 hover:border-slate-600 rounded-lg p-6 transition-all duration-300 h-full">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${setting.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-1 group-hover:text-blue-400 transition-colors">
                    {setting.title}
                  </h3>
                  <p className="text-gray-400 text-sm">{setting.description}</p>
                </div>
              </Link>
            )
          })}
        </div>

        {/* Account Danger Zone */}
        <div className="max-w-2xl">
          <h2 className="text-2xl font-bold text-white mb-4">Account</h2>
          <button
            onClick={handleLogout}
            className="w-full px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
          >
            <LogOut className="w-5 h-5" />
            Log Out
          </button>
          <p className="text-gray-400 text-sm mt-2">
            You will be logged out of this device.
          </p>
        </div>

        {/* Support Banner */}
        <div className="mt-12 bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-lg p-6">
          <h3 className="text-lg font-bold text-white mb-2">Need Help?</h3>
          <p className="text-gray-300 mb-4">
            Can't find what you're looking for? Our support team is here to help.
          </p>
          <div className="flex gap-4">
            <a
              href="/docs/faq"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Read FAQ
            </a>
            <a
              href="/contact"
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              Contact Support
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
