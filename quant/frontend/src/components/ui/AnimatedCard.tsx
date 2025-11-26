/**
 * Animated Card Component with hover effects and glassmorphism
 */

'use client'

import { ReactNode, useState } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedCardProps {
  children: ReactNode
  className?: string
  variant?: 'default' | 'glass' | 'gradient'
  hoverEffect?: boolean
  delay?: number
}

export function AnimatedCard({
  children,
  className,
  variant = 'default',
  hoverEffect = true,
  delay = 0,
}: AnimatedCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  const baseStyles = 'rounded-xl p-6 transition-all duration-300'

  const variantStyles = {
    default: 'bg-card border border-border',
    glass: 'glass',
    gradient: 'bg-gradient-to-br from-primary/5 via-purple-500/5 to-pink-500/5 border border-border/50',
  }

  const hoverStyles = hoverEffect
    ? 'hover:shadow-2xl hover:-translate-y-1 hover:border-primary/50 cursor-pointer'
    : ''

  return (
    <div
      className={cn(
        baseStyles,
        variantStyles[variant],
        hoverStyles,
        'animate-fade-in',
        className
      )}
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: 'backwards',
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}
    </div>
  )
}
