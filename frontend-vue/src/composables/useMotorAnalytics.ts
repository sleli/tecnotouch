import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { useAnalyticsStore } from '../stores/analytics'

// Types for analytics data
export interface PeriodMetrics {
  sales_count: number
  revenue: number
}

export interface LastSale {
  timestamp: string
  days_ago: number
}

export interface SalesPattern {
  average_interval_hours: number
  sales_count: number
  threshold_hours: number
}

export interface MotorAnalytics {
  motor_id: number
  position: string
  today: PeriodMetrics
  week: PeriodMetrics
  month: PeriodMetrics
  last_sale: LastSale | null
  status_indicator: 'red' | 'green' | 'neutral'
  sales_pattern: SalesPattern | null
}

export interface MotorStatusIndicator {
  motor_id: number
  status_indicator: 'red' | 'green' | 'neutral'
}

export interface AllMotorStatus {
  motors: MotorStatusIndicator[]
  last_updated: string
}

/**
 * Composable for motor analytics API integration
 * Provides reactive data and methods for fetching motor analytics
 * Integrates with analytics store for centralized state management
 */
export function useMotorAnalytics() {
  // Get store instance
  const analyticsStore = useAnalyticsStore()

  // Local reactive state (for component-specific data)
  const analytics: Ref<MotorAnalytics | null> = ref(null)
  const allStatus: Ref<AllMotorStatus | null> = ref(null)
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  // API base URL - will be determined dynamically
  const getApiBaseUrl = () => {
    // Use current host for API calls to support both local and remote access
    const protocol = window.location.protocol
    const hostname = window.location.hostname
    const port = hostname === 'localhost' ? '8000' : '8000' // API port
    return `${protocol}//${hostname}:${port}`
  }

  /**
   * Fetch detailed analytics for a specific motor
   * Integrates with store for caching and state management
   */
  const fetchAnalytics = async (motorId: number): Promise<void> => {
    if (!motorId) return

    // Set loading state in both local and store
    loading.value = true
    analyticsStore.setLoading(true)
    error.value = null
    analytics.value = null

    try {
      const baseUrl = getApiBaseUrl()
      const response = await fetch(`${baseUrl}/api/motors/${motorId}/analytics`)

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Motor ${motorId} not found`)
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      // Update both local state and store
      analytics.value = data
      analyticsStore.setMotorAnalytics(data)
      analyticsStore.setLoading(false)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch analytics'
      error.value = errorMessage
      analyticsStore.setError(errorMessage)
      analytics.value = null
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch status indicators for all motors
   * Integrates with store for caching and state management
   */
  const fetchAllStatus = async (): Promise<void> => {
    loading.value = true
    analyticsStore.setLoading(true)
    error.value = null

    try {
      const baseUrl = getApiBaseUrl()
      const response = await fetch(`${baseUrl}/api/motors/analytics/status`)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      // Update both local state and store
      allStatus.value = data
      analyticsStore.setAllMotorStatus(data)
      analyticsStore.setLoading(false)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch motor status'
      error.value = errorMessage
      analyticsStore.setError(errorMessage)
      allStatus.value = null
    } finally {
      loading.value = false
    }
  }

  /**
   * Trigger analytics refresh on the backend
   */
  const refreshAnalytics = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const baseUrl = getApiBaseUrl()
      const response = await fetch(`${baseUrl}/api/analytics/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('Analytics refresh initiated:', data.message)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to refresh analytics'
    } finally {
      loading.value = false
    }
  }

  /**
   * Get status indicator for a specific motor from all status data
   */
  const getMotorStatus = (motorId: number): 'red' | 'green' | 'neutral' | null => {
    if (!allStatus.value) return null

    const motor = allStatus.value.motors.find(m => m.motor_id === motorId)
    return motor ? motor.status_indicator : null
  }

  /**
   * Clear current analytics data
   */
  const clearAnalytics = (): void => {
    analytics.value = null
    error.value = null
  }

  /**
   * Clear all status data
   */
  const clearAllStatus = (): void => {
    allStatus.value = null
    error.value = null
  }

  // Computed properties
  const hasAnalytics = computed(() => analytics.value !== null)
  const hasError = computed(() => error.value !== null)
  const isEmpty = computed(() => !loading.value && !hasAnalytics.value && !hasError.value)

  // Status indicator styling helpers
  const getStatusClass = (status: 'red' | 'green' | 'neutral' | null): string => {
    const classes = {
      red: 'bg-red-500 text-white',
      green: 'bg-green-500 text-white',
      neutral: 'bg-gray-400 text-white'
    }
    return status ? classes[status] : 'bg-gray-300 text-gray-600'
  }

  const getStatusText = (status: 'red' | 'green' | 'neutral' | null): string => {
    const texts = {
      red: 'Overdue',
      green: 'Normal',
      neutral: 'No Data'
    }
    return status ? texts[status] : 'Unknown'
  }

  return {
    // State
    analytics,
    allStatus,
    loading,
    error,

    // Actions
    fetchAnalytics,
    fetchAllStatus,
    refreshAnalytics,
    getMotorStatus,
    clearAnalytics,
    clearAllStatus,

    // Computed
    hasAnalytics,
    hasError,
    isEmpty,

    // Utilities
    getStatusClass,
    getStatusText
  }
}