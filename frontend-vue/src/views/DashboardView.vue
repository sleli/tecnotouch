<template>
  <div class="dashboard-view h-full overflow-y-auto custom-scrollbar pb-20">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-4 py-3 safe-top">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-gray-900">Dashboard</h1>
          <p class="text-sm text-gray-500">Panoramica sistema</p>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="refreshDashboard"
            :disabled="appStore.isLoading"
            class="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors touch-feedback"
          >
            <RefreshCw
              class="w-5 h-5"
              :class="{ 'animate-spin': appStore.isLoading }"
            />
          </button>
        </div>
      </div>
    </div>

    <div class="p-4 space-y-4">
      <!-- KPI Cards -->
      <div class="grid grid-cols-2 gap-4">
        <KPICard
          title="Vendite Oggi"
          :value="dashboardStats.todaySales"
          :loading="statsLoading"
          icon="TrendingUp"
          color="green"
        />
        <KPICard
          title="Ricavi Oggi"
          :value="formatCurrency(dashboardStats.todayRevenue)"
          :loading="statsLoading"
          icon="Euro"
          color="emerald"
        />
      </div>

      <!-- Sincronizzazione Dati -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-2 text-center">Sincronizzazione Dati</h3>
        <p class="text-sm text-gray-500 mb-4 text-center">Aggiorna il sistema con i nuovi eventi dal distributore</p>
        <div class="flex justify-center">
          <button
            @click="downloadEvents"
            :disabled="downloadLoading"
            class="flex items-center space-x-4 px-6 py-4 bg-gradient-to-r from-blue-500 to-teal-600 text-white rounded-xl hover:from-blue-600 hover:to-teal-700 transition-all duration-200 transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:transform-none min-w-[240px] justify-center"
          >
            <RefreshCw
              class="w-6 h-6"
              :class="{ 'animate-spin': downloadLoading }"
            />
            <span class="text-lg font-semibold">
              {{ downloadLoading ? 'Sincronizzando...' : 'Sincronizza Sistema' }}
            </span>
          </button>
        </div>
      </div>


      <!-- Recent Alerts -->
      <div
        v-if="alertStore.alerts.length > 0"
        class="bg-white rounded-xl shadow-sm border border-gray-200 p-4"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Alert Recenti</h3>
          <router-link
            to="/alerts"
            class="text-sm text-blue-600 hover:text-blue-700 px-3 py-1 rounded touch-feedback"
          >
            Vedi tutti
          </router-link>
        </div>
        <div class="space-y-3 max-h-48 overflow-y-auto">
          <AlertCard
            v-for="alert in recentAlerts"
            :key="alert.id"
            :alert="alert"
            compact
          />
        </div>
      </div>

      <!-- System Status -->
      <div class="bg-gray-50 rounded-xl p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <button
              @click="showSystemModal = true"
              class="w-3 h-3 rounded-full transition-all hover:scale-110 touch-feedback"
              :class="appStore.isOnline ? 'bg-green-400 hover:bg-green-500' : 'bg-red-400 hover:bg-red-500'"
            />
            <div>
              <p class="font-medium text-gray-900">
                {{ getSystemStatusText() }}
              </p>
              <p class="text-sm text-gray-600 whitespace-nowrap">
                Ultima sincronizzazione: {{ appStore.formattedLastSync }}
              </p>
              <p class="text-sm font-medium text-gray-600 whitespace-nowrap">
                Ultimo evento: {{ appStore.formattedLastEventDate }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Status Modal -->
    <SystemStatusModal
      v-if="showSystemModal"
      :system-status="appStore.systemStatus"
      @close="showSystemModal = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useMotorsStore } from '@/stores/motors'
import { useAlertStore } from '@/stores/alerts'
import { useApi, API_ENDPOINTS } from '@/composables/useApi'
import { useSSE } from '@/composables/useSSE'
import {
  RefreshCw,
  TrendingUp,
  Euro,
  AlertTriangle
} from 'lucide-vue-next'

// Components
import KPICard from '@/components/KPICard.vue'
import AlertCard from '@/components/AlertCard.vue'
import SystemStatusModal from '@/components/SystemStatusModal.vue'

// Stores
const appStore = useAppStore()
const motorsStore = useMotorsStore()
const alertStore = useAlertStore()
const router = useRouter()

// API composable
const { get, post } = useApi()

// SSE composable
const sse = useSSE()

// Local state
const statsLoading = ref(false)
const downloadLoading = ref(false)
const showSystemModal = ref(false)

const dashboardStats = reactive({
  todaySales: 0,
  todayRevenue: 0
})


// Computed
const recentAlerts = computed(() => {
  return alertStore.sortedAlerts.slice(0, 3)
})

// Methods
const formatCurrency = (value) => {
  if (typeof value !== 'number') return '€0.00'
  return `€${value.toFixed(2)}`
}

const loadDashboardStats = async () => {
  try {
    statsLoading.value = true

    // Load motors data first
    await motorsStore.fetchMotors()

    // Try to load additional stats from API
    try {
      const data = await get(API_ENDPOINTS.DASHBOARD_STATS)

      // Handle API response structure
      if (data.summary) {
        dashboardStats.todaySales = data.summary.today_sales || 0
        dashboardStats.todayRevenue = data.summary.today_revenue || 0
      } else {
        // Fallback calculation from motors
        dashboardStats.todaySales = 0 // API doesn't provide this currently
        dashboardStats.todayRevenue = 0 // API doesn't provide this currently
      }
    } catch (error) {
      dashboardStats.todaySales = 0
      dashboardStats.todayRevenue = 0
    }

  } catch (error) {
    console.error('Failed to load dashboard stats:', error)
  } finally {
    statsLoading.value = false
  }
}

const loadDownloadInfo = async () => {
  try {
    const data = await get(API_ENDPOINTS.DOWNLOAD_INFO)
    if (data.last_download) {
      appStore.updateLastDownload(data.last_download)
    }
    if (data.last_event_date) {
      appStore.updateLastEventDate(data.last_event_date)
    }
  } catch (error) {
    // Silently handle - not critical
  }
}


const downloadEvents = async () => {
  try {
    downloadLoading.value = true

    const result = await post(API_ENDPOINTS.DOWNLOAD_EVENTS, {})

    if (window.$toast) {
      window.$toast.success('Download eventi avviato!', {
        title: 'Download in corso'
      })
    }

    // Non impostiamo downloadLoading a false qui perché
    // verrà fatto automaticamente quando arriva l'evento SSE

  } catch (error) {
    console.error('Download failed:', error)
    downloadLoading.value = false

    if (window.$toast) {
      window.$toast.error('Errore nel download eventi')
    }
  }
}

const getSystemStatusText = () => {
  if (appStore.apiHealthy && appStore.distributoreHealthy) {
    return 'Sistema Online'
  } else if (!appStore.apiHealthy) {
    return 'API Offline'
  } else {
    return 'Distributore Offline'
  }
}

const refreshDashboard = async () => {
  await loadDashboardStats()

  if (window.$toast) {
    window.$toast.success('Dashboard aggiornata')
  }
}

// Expose refresh method to parent
defineExpose({
  refreshDashboard
})



// Setup SSE handlers
const setupSSEHandlers = () => {
  // Handler per connessione SSE
  sse.onConnected((data) => {
    // SSE connected
  })

  // Handler per inizio download
  sse.onDownloadStarted((data) => {
    downloadLoading.value = true

    if (window.$toast) {
      window.$toast.info(data.message || 'Download iniziato', {
        title: 'Sincronizzazione'
      })
    }
  })

  // Handler per progresso download
  sse.onDownloadProgress((data) => {
    if (window.$toast && data.progress === 20) {
      window.$toast.info(data.message || 'Download in corso...', {
        title: 'Sincronizzazione'
      })
    }
  })

  // Handler per completamento download
  sse.onDownloadCompleted(async (data) => {
    downloadLoading.value = false

    // Aggiorna immediatamente il timestamp di sincronizzazione
    if (data.last_download) {
      appStore.updateLastDownload(data.last_download)
    }

    // Ricarica i dati della dashboard e info download (comprende last_event_date)
    await loadDashboardStats()
    await loadDownloadInfo()

    if (window.$toast) {
      window.$toast.success(data.message || 'Sincronizzazione completata!', {
        title: 'Successo'
      })
    }
  })

  // Handler per errori download
  sse.onDownloadError((data) => {
    console.error('❌ Download error:', data)
    downloadLoading.value = false

    if (window.$toast) {
      window.$toast.error(data.message || 'Errore durante la sincronizzazione', {
        title: 'Errore'
      })
    }
  })
}

// Lifecycle
onMounted(() => {
  // Load initial data
  loadDashboardStats()
  loadDownloadInfo()

  // Setup SSE connection and handlers
  setupSSEHandlers()
  sse.connect()

})

onUnmounted(() => {
  // Disconnetti SSE
  sse.disconnect()
})
</script>

<style scoped>
.dashboard-view {
  /* Account for safe areas */
  padding-bottom: env(safe-area-inset-bottom);
}

/* Smooth scrolling */
.dashboard-view {
  scroll-behavior: smooth;
}

/* Loading states */
.loading-shimmer {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>