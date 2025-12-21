<template>
  <div class="alerts-view h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-4 py-3 flex-shrink-0 safe-top">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-gray-900">Alert</h1>
          <p class="text-sm text-gray-500">
            {{ alertStore.unreadCount }} non letti di {{ alertStore.alerts.length }}
          </p>
        </div>
        <div class="flex items-center space-x-2">
          <button
            v-if="alertStore.unreadCount > 0"
            @click="alertStore.markAllAsRead"
            class="text-sm text-blue-600 hover:text-blue-700 px-3 py-2 rounded-lg hover:bg-blue-50 transition-colors touch-feedback"
          >
            Segna tutti letti
          </button>
          <button
            @click="refreshAlerts"
            class="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors touch-feedback"
            title="Aggiorna alert"
          >
            <RefreshCw class="w-5 h-5" />
          </button>
          <button
            @click="alertStore.clearOldAlerts"
            class="p-2 text-gray-600 hover:text-gray-800 rounded-lg hover:bg-gray-100 transition-colors touch-feedback"
            title="Pulisci vecchi alert"
          >
            <Trash2 class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <!-- Empty state -->
      <div
        v-if="alertStore.alerts.length === 0"
        class="flex flex-col items-center justify-center h-full px-4"
      >
        <AlertTriangle class="w-16 h-16 text-gray-300 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Nessun Alert</h3>
        <p class="text-gray-600 text-center">
          Non ci sono alert da visualizzare al momento.
        </p>
      </div>

      <!-- Alerts list -->
      <div v-else class="p-4 space-y-3 pb-20">
        <!-- Critical alerts section -->
        <div v-if="criticalAlerts.length > 0">
          <h2 class="text-sm font-semibold text-red-600 mb-3 flex items-center">
            <AlertTriangle class="w-4 h-4 mr-2" />
            Alert Critici ({{ criticalAlerts.length }})
          </h2>
          <div class="space-y-2 mb-6">
            <AlertCard
              v-for="alert in criticalAlerts"
              :key="alert.id"
              :alert="alert"
              @click="handleAlertClick(alert)"
              @dismiss="handleAlertDismiss(alert)"
            />
          </div>
        </div>

        <!-- Warning alerts section -->
        <div v-if="warningAlerts.length > 0">
          <h2 class="text-sm font-semibold text-yellow-600 mb-3 flex items-center">
            <AlertTriangle class="w-4 h-4 mr-2" />
            Avvisi ({{ warningAlerts.length }})
          </h2>
          <div class="space-y-2 mb-6">
            <AlertCard
              v-for="alert in warningAlerts"
              :key="alert.id"
              :alert="alert"
              @click="handleAlertClick(alert)"
              @dismiss="handleAlertDismiss(alert)"
            />
          </div>
        </div>

        <!-- Info alerts section -->
        <div v-if="infoAlerts.length > 0">
          <h2 class="text-sm font-semibold text-blue-600 mb-3 flex items-center">
            <Info class="w-4 h-4 mr-2" />
            Informazioni ({{ infoAlerts.length }})
          </h2>
          <div class="space-y-2">
            <AlertCard
              v-for="alert in infoAlerts"
              :key="alert.id"
              :alert="alert"
              @click="handleAlertClick(alert)"
              @dismiss="handleAlertDismiss(alert)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Alert detail modal -->
    <AlertDetailModal
      v-if="selectedAlert"
      :alert="selectedAlert"
      @close="selectedAlert = null"
      @dismiss="handleAlertDismiss"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAlertStore } from '@/stores/alerts'
import { useMotorsStore } from '@/stores/motors'
import {
  AlertTriangle,
  Info,
  Trash2,
  RefreshCw
} from 'lucide-vue-next'
import AlertCard from '@/components/AlertCard.vue'
import AlertDetailModal from '@/components/AlertDetailModal.vue'

const router = useRouter()
const alertStore = useAlertStore()
const motorsStore = useMotorsStore()

// Local state
const selectedAlert = ref(null)

// Computed
const criticalAlerts = computed(() => {
  return alertStore.sortedAlerts.filter(alert => alert.level === 'critical')
})

const warningAlerts = computed(() => {
  return alertStore.sortedAlerts.filter(alert => alert.level === 'warning')
})

const infoAlerts = computed(() => {
  return alertStore.sortedAlerts.filter(alert => alert.level === 'info')
})

// Methods
const handleAlertClick = (alert) => {
  selectedAlert.value = alert

  // Mark as read when clicked
  if (!alert.read) {
    alertStore.markAsRead(alert.id)
  }

  // If alert is related to a motor, we could navigate to it
  if (alert.motorId) {
    // Could implement motor-specific actions
    console.log('Alert for motor:', alert.motorId)
  }
}

const handleAlertDismiss = (alert) => {
  alertStore.removeAlert(alert.id)

  if (selectedAlert.value && selectedAlert.value.id === alert.id) {
    selectedAlert.value = null
  }

  if (window.$toast) {
    window.$toast.success('Alert rimosso')
  }
}

const refreshAlerts = async () => {
  // Clear old alerts and refresh
  alertStore.clearOldAlerts()

  // Could add API call here in the future to fetch new alerts
  return Promise.resolve()
}

// Expose refresh method to parent
defineExpose({
  refreshAlerts
})

// Add some demo alerts on mount for testing
onMounted(() => {
  // Clear old alerts first
  alertStore.clearOldAlerts()

  // If no alerts exist, add some demo ones for testing
  if (alertStore.alerts.length === 0) {


    // Demo info alert
    alertStore.addAlert({
      level: 'info',
      title: 'Sistema Aggiornato',
      message: 'Dashboard aggiornata alla versione 2.0 con nuove funzionalità PWA.'
    })
  }
})
</script>

<style scoped>
.alerts-view {
  /* Account for bottom navigation */
  padding-bottom: env(safe-area-inset-bottom);
}
</style>