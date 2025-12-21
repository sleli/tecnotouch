import { ref } from 'vue'
import { useAppStore } from '@/stores/app'

export function useApi() {
  const appStore = useAppStore()
  const loading = ref(false)
  const error = ref(null)

  const apiCall = async (endpoint, options = {}) => {
    loading.value = true
    error.value = null

    try {
      let url = `${appStore.apiBase}${endpoint}`

      // Handle query parameters
      if (options.params) {
        const searchParams = new URLSearchParams()
        Object.entries(options.params).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            searchParams.append(key, value)
          }
        })

        if (searchParams.toString()) {
          url += `?${searchParams.toString()}`
        }
      }

      console.log('🔄 API Call:', url)

      const defaultOptions = {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }

      const mergedOptions = { ...defaultOptions, ...options }

      const response = await fetch(url, mergedOptions)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('✅ API Success:', endpoint, data)

      return data
    } catch (err) {
      console.error('❌ API Error:', endpoint, err)
      error.value = err.message

      // Show error toast if available
      if (window.$toast && !options.silent) {
        window.$toast.error(`Errore API: ${err.message}`, {
          title: `Errore in ${endpoint}`
        })
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  // Specific API methods
  const get = (endpoint, options = {}) => {
    return apiCall(endpoint, { ...options, method: 'GET' })
  }

  const post = (endpoint, data, options = {}) => {
    return apiCall(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  const put = (endpoint, data, options = {}) => {
    return apiCall(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  const del = (endpoint, options = {}) => {
    return apiCall(endpoint, { ...options, method: 'DELETE' })
  }

  return {
    loading,
    error,
    apiCall,
    get,
    post,
    put,
    delete: del
  }
}

// API endpoints constants
export const API_ENDPOINTS = {
  // Dashboard
  DASHBOARD_STATS: '/dashboard',
  DASHBOARD_CHARTS: '/dashboard',

  // Motors
  MOTORS_LIST: '/motors',
  MOTOR_DETAIL: (id) => `/motors/${id}`,
  MOTOR_HISTORY: (id) => `/motors/${id}/history`,

  // Statistics
  STATS_OVERVIEW: '/statistics/overview',
  STATS_BRANDS: '/statistics/by-brand',
  STATS_PACKAGE_TYPES: '/statistics/by-package-type',
  STATS_PAYMENTS: '/statistics/transactions',
  STATS_SALES_TREND: '/statistics/overview',

  // Events/Downloads
  DOWNLOAD_EVENTS: '/download-events',
  DOWNLOAD_STATUS: '/download-status',
  DOWNLOAD_INFO: '/download-info',

  // SSE
  SSE_EVENTS: '/events',

  // Health check
  HEALTH: '/health'
}