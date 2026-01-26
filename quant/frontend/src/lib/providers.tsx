/**
 * React Query Provider Configuration
 *
 * Optimized for performance with aggressive caching and deduplication.
 * Performance improvements:
 * - Increased staleTime to 10 minutes (less refetching)
 * - Added cacheTime for background cache retention
 * - Enabled query deduplication
 * - Retry strategy tuned for API reliability
 */

'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Cache Configuration
            staleTime: 1000 * 60 * 10, // 10 minutes (increased from 5 for better caching)
            gcTime: 1000 * 60 * 30, // 30 minutes (background cache retention)

            // Network Configuration
            retry: 2, // Retry failed requests twice
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff

            // Refetch Configuration
            refetchOnWindowFocus: false, // Don't refetch on window focus (saves bandwidth)
            refetchOnReconnect: true, // Refetch when network reconnects
            refetchOnMount: false, // Use cache on component mount if data is not stale

            // Performance Optimization
            structuralSharing: true, // Share unchanged data between renders (memory optimization)
          },
          mutations: {
            retry: 1, // Retry mutations once on failure
            retryDelay: 1000, // Wait 1s before retrying mutation
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
