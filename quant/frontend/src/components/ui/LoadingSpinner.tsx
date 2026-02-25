/**
 * Modern loading spinner with variants
 */

'use client'

import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'default' | 'primary' | 'gradient'
  text?: string
  fullScreen?: boolean
}

export function LoadingSpinner({
  size = 'md',
  variant = 'primary',
  text,
  fullScreen = false,
}: LoadingSpinnerProps) {
  const sizeStyles = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  }

  const variantStyles = {
    default: 'border-muted-foreground',
    primary: 'border-primary',
    gradient: 'border-transparent bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500',
  }

  const spinner = (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className="relative">
        <div
          className={cn(
            'animate-spin rounded-full border-4 border-solid border-r-transparent',
            sizeStyles[size],
            variantStyles[variant]
          )}
        />
        {variant === 'gradient' && (
          <div
            className={cn(
              'absolute inset-0 animate-spin rounded-full border-4 border-solid border-r-transparent opacity-50',
              'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500',
              sizeStyles[size]
            )}
            style={{ animationDuration: '1.5s', animationDirection: 'reverse' }}
          />
        )}
      </div>
      {text && <p className="text-sm text-muted-foreground animate-pulse">{text}</p>}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-50">
        {spinner}
      </div>
    )
  }

  return spinner
}
