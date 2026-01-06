import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAppStore } from './app'
import { useAlertStore } from './alerts'
import { useAnalyticsStore } from './analytics'

export const useMotorsStore = defineStore('motors', () => {
  const appStore = useAppStore()
  const alertStore = useAlertStore()
  const analyticsStore = useAnalyticsStore()

  // State
  const motors = ref([])
  const selectedMotor = ref(null)
  const lastFetch = ref(null)

  // Getters
  const totalMotors = computed(() => motors.value.length)

  const filteredMotors = computed(() => {
    return motors.value
  })


  // Actions
  const fetchMotors = async () => {
    try {
      appStore.setLoading(true)

      const response = await fetch(`${appStore.apiBase}/motors`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()

      // Transform API data to match frontend expectations
      const transformedMotors = Array.isArray(data) ? data : (data.motors || [])
      motors.value = transformedMotors.map(motor => {
        return {
          id: motor.motor_id || motor.id,
          motorId: motor.motor_id || motor.id,
          product: motor.product_name || motor.product,
          productName: motor.product_name || motor.product,
          price: motor.price,
          totalSales: motor.total_sales || motor.totalSales || 0,
          hoursSinceLastSale: motor.hours_since_last_sale || motor.hoursSinceLastSale,
          lastSaleDateTime: motor.last_sale_datetime || motor.lastSaleDateTime,
          lastUpdated: new Date()
        }
      })

      lastFetch.value = new Date()

      // Trigger analytics refresh when motors are refreshed
      await refreshAnalyticsIfNeeded()

      appStore.updateLastUpdate()
      return { motors: motors.value }
    } catch (error) {
      console.error('Error fetching motors:', error)

      // Show error toast
      if (window.$toast) {
        window.$toast.error('Errore nel caricamento motori', {
          title: 'Connessione fallita'
        })
      }

      // Use cached data if available
      if (motors.value.length === 0) {
        await loadCachedMotors()
      }

      throw error
    } finally {
      appStore.setLoading(false)
    }
  }

  const refreshMotors = async () => {
    return await fetchMotors()
  }

  const selectMotor = (motor) => {
    selectedMotor.value = motor
  }

  const clearSelection = () => {
    selectedMotor.value = null
  }


  const getMotorById = (id) => {
    return motors.value.find(motor => motor.id === id)
  }


  // Cache management
  const cacheMotors = () => {
    if (motors.value.length > 0) {
      localStorage.setItem('cached_motors', JSON.stringify({
        data: motors.value,
        timestamp: Date.now()
      }))
    }
  }

  const loadCachedMotors = async () => {
    try {
      const cached = localStorage.getItem('cached_motors')
      if (cached) {
        const { data, timestamp } = JSON.parse(cached)

        // Use cached data if less than 1 hour old
        const oneHour = 60 * 60 * 1000
        if (Date.now() - timestamp < oneHour) {
          motors.value = data
          lastFetch.value = new Date(timestamp)

          if (window.$toast) {
            window.$toast.info('Dati caricati dalla cache')
          }

          return true
        }
      }
    } catch (error) {
      console.error('Error loading cached motors:', error)
    }
    return false
  }

  const clearCachedMotors = () => {
    try {
      localStorage.removeItem('cached_motors')
      return true
    } catch (error) {
      console.error('Error clearing cached motors:', error)
      return false
    }
  }

  // Analytics integration
  const refreshAnalyticsIfNeeded = async () => {
    try {
      // Only refresh analytics if cache is expired or empty
      if (!analyticsStore.isStatusCacheValid()) {
        // Use the composable to fetch fresh analytics data
        const { useMotorAnalytics } = await import('../composables/useMotorAnalytics')
        const { fetchAllStatus } = useMotorAnalytics()

        await fetchAllStatus()
      }
    } catch (error) {
      console.warn('Failed to refresh analytics:', error.message)
      // Don't throw error - analytics refresh is not critical for motor loading
    }
  }

  // Auto-refresh every 30 seconds
  let refreshInterval = null

  const startAutoRefresh = () => {
    if (refreshInterval) clearInterval(refreshInterval)

    refreshInterval = setInterval(async () => {
      if (document.visibilityState === 'visible') {
        try {
          await fetchMotors()
          // Motors fetch already includes analytics refresh via refreshAnalyticsIfNeeded
        } catch (error) {
          // Try to refresh analytics independently if motors failed
          try {
            await refreshAnalyticsIfNeeded()
          } catch (analyticsError) {
            // Silently handle
          }
        }
      }
    }, 30 * 1000)
  }

  const stopAutoRefresh = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }

  // Cache motors when they change
  motors.value && cacheMotors()

  return {
    // State
    motors,
    selectedMotor,
    lastFetch,

    // Getters
    totalMotors,
    filteredMotors,

    // Actions
    fetchMotors,
    refreshMotors,
    selectMotor,
    clearSelection,
    getMotorById,
    loadCachedMotors,
    clearCachedMotors,
    startAutoRefresh,
    stopAutoRefresh,
    refreshAnalyticsIfNeeded
  }
})