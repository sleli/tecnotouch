import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  MotorAnalytics,
  AllMotorStatus,
  MotorStatusIndicator
} from '../composables/useMotorAnalytics'

/**
 * Pinia store for motor analytics state management
 * Centralizes analytics data and provides cache management
 */
export const useAnalyticsStore = defineStore('analytics', () => {
  // State
  const motorAnalytics = ref(new Map<number, MotorAnalytics>())
  const allMotorStatus = ref<AllMotorStatus | null>(null)
  const lastUpdated = ref<Date | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Cache configuration
  const CACHE_TTL_MS = 5 * 60 * 1000 // 5 minutes
  const cacheTimestamps = ref(new Map<string, Date>())

  // Computed
  const hasData = computed(() => allMotorStatus.value !== null)
  const motorCount = computed(() => allMotorStatus.value?.motors.length || 0)

  const isCacheValid = computed(() => (key: string) => {
    const timestamp = cacheTimestamps.value.get(key)
    if (!timestamp) return false
    return Date.now() - timestamp.getTime() < CACHE_TTL_MS
  })

  /**
   * Get analytics data for a specific motor
   */
  const getMotorAnalytics = (motorId: number): MotorAnalytics | null => {
    return motorAnalytics.value.get(motorId) || null
  }

  /**
   * Get status indicator for a specific motor
   */
  const getMotorStatus = (motorId: number): 'red' | 'green' | 'neutral' | null => {
    if (!allMotorStatus.value) return null

    const motor = allMotorStatus.value.motors.find(m => m.motor_id === motorId)
    return motor ? motor.status_indicator : null
  }

  /**
   * Set analytics data for a specific motor
   */
  const setMotorAnalytics = (data: MotorAnalytics): void => {
    motorAnalytics.value.set(data.motor_id, data)
    cacheTimestamps.value.set(`motor_${data.motor_id}`, new Date())
    lastUpdated.value = new Date()
  }

  /**
   * Set all motor status data
   */
  const setAllMotorStatus = (data: AllMotorStatus): void => {
    allMotorStatus.value = data
    cacheTimestamps.value.set('all_status', new Date())
    lastUpdated.value = new Date()
  }

  /**
   * Update loading state
   */
  const setLoading = (loading: boolean): void => {
    isLoading.value = loading
    if (loading) {
      error.value = null
    }
  }

  /**
   * Set error state
   */
  const setError = (errorMessage: string | null): void => {
    error.value = errorMessage
    if (errorMessage) {
      isLoading.value = false
    }
  }

  /**
   * Check if motor analytics cache is valid
   */
  const isMotorCacheValid = (motorId: number): boolean => {
    return isCacheValid.value(`motor_${motorId}`)
  }

  /**
   * Check if all status cache is valid
   */
  const isStatusCacheValid = (): boolean => {
    return isCacheValid.value('all_status')
  }

  /**
   * Clear analytics data for a specific motor
   */
  const clearMotorAnalytics = (motorId: number): void => {
    motorAnalytics.value.delete(motorId)
    cacheTimestamps.value.delete(`motor_${motorId}`)
  }

  /**
   * Clear all motor status data
   */
  const clearAllStatus = (): void => {
    allMotorStatus.value = null
    cacheTimestamps.value.delete('all_status')
  }

  /**
   * Clear all cached data
   */
  const clearAll = (): void => {
    motorAnalytics.value.clear()
    allMotorStatus.value = null
    cacheTimestamps.value.clear()
    lastUpdated.value = null
    error.value = null
  }

  /**
   * Clean expired cache entries
   */
  const cleanExpiredCache = (): void => {
    const now = Date.now()

    for (const [key, timestamp] of cacheTimestamps.value) {
      if (now - timestamp.getTime() > CACHE_TTL_MS) {
        cacheTimestamps.value.delete(key)

        // Clean corresponding data
        if (key.startsWith('motor_')) {
          const motorId = parseInt(key.replace('motor_', ''))
          motorAnalytics.value.delete(motorId)
        } else if (key === 'all_status') {
          allMotorStatus.value = null
        }
      }
    }
  }

  /**
   * Get cache statistics for debugging
   */
  const getCacheStats = () => {
    return {
      motorAnalyticsCount: motorAnalytics.value.size,
      hasAllStatus: allMotorStatus.value !== null,
      cacheEntries: cacheTimestamps.value.size,
      lastUpdated: lastUpdated.value,
      isLoading: isLoading.value,
      error: error.value
    }
  }

  /**
   * Get all cached motor IDs
   */
  const getCachedMotorIds = (): number[] => {
    return Array.from(motorAnalytics.value.keys())
  }

  /**
   * Refresh status for specific motors (batch update)
   */
  const updateMotorStatuses = (statuses: MotorStatusIndicator[]): void => {
    if (!allMotorStatus.value) {
      allMotorStatus.value = {
        motors: statuses,
        last_updated: new Date().toISOString()
      }
    } else {
      // Update existing statuses
      statuses.forEach(newStatus => {
        const existingIndex = allMotorStatus.value!.motors.findIndex(
          m => m.motor_id === newStatus.motor_id
        )

        if (existingIndex >= 0) {
          allMotorStatus.value!.motors[existingIndex] = newStatus
        } else {
          allMotorStatus.value!.motors.push(newStatus)
        }
      })

      allMotorStatus.value.last_updated = new Date().toISOString()
    }

    cacheTimestamps.value.set('all_status', new Date())
    lastUpdated.value = new Date()
  }

  // Auto-cleanup expired cache every 5 minutes
  setInterval(cleanExpiredCache, 5 * 60 * 1000)

  return {
    // State
    motorAnalytics: motorAnalytics.value,
    allMotorStatus,
    lastUpdated,
    isLoading,
    error,

    // Computed
    hasData,
    motorCount,

    // Getters
    getMotorAnalytics,
    getMotorStatus,
    isMotorCacheValid,
    isStatusCacheValid,
    getCacheStats,
    getCachedMotorIds,

    // Actions
    setMotorAnalytics,
    setAllMotorStatus,
    setLoading,
    setError,
    clearMotorAnalytics,
    clearAllStatus,
    clearAll,
    cleanExpiredCache,
    updateMotorStatuses
  }
})