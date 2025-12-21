<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
         @click="closePopup"></div>

    <!-- Modal -->
    <div class="flex min-h-full items-center justify-center p-4">
      <div class="relative w-full max-w-md transform overflow-hidden rounded-lg bg-white shadow-xl transition-all">
        <!-- Header -->
        <div class="bg-gray-50 px-4 py-3 border-b">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">
              Motor {{ motorId }} Details
            </h3>
            <button @click="closePopup"
                    class="text-gray-400 hover:text-gray-600 focus:outline-none">
              <span class="sr-only">Close</span>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="px-4 py-6">
          <!-- Loading State -->
          <div v-if="loading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-2 text-sm text-gray-500">Loading analytics...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="text-center py-8">
            <div class="text-red-600 mb-2">
              <svg class="h-8 w-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <p class="text-sm text-gray-600">{{ error }}</p>
          </div>

          <!-- Analytics Content -->
          <div v-else-if="analytics" class="space-y-6">
            <!-- Status Indicator -->
            <div class="text-center">
              <div class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                   :class="statusClasses">
                <span class="w-2 h-2 rounded-full mr-2" :class="statusDotClasses"></span>
                {{ statusText }}
              </div>
            </div>

            <!-- Time Period Metrics -->
            <div class="grid grid-cols-3 gap-4">
              <!-- Today -->
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ analytics.today.sales_count }}</div>
                <div class="text-sm text-gray-500">Today</div>
                <div class="text-lg text-green-600">€{{ analytics.today.revenue.toFixed(2) }}</div>
              </div>

              <!-- Week -->
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ analytics.week.sales_count }}</div>
                <div class="text-sm text-gray-500">This Week</div>
                <div class="text-lg text-green-600">€{{ analytics.week.revenue.toFixed(2) }}</div>
              </div>

              <!-- Month -->
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ analytics.month.sales_count }}</div>
                <div class="text-sm text-gray-500">This Month</div>
                <div class="text-lg text-green-600">€{{ analytics.month.revenue.toFixed(2) }}</div>
              </div>
            </div>

            <!-- Last Sale -->
            <div v-if="analytics.last_sale" class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Last Sale</h4>
              <p class="text-sm text-gray-600">
                {{ formatLastSale(analytics.last_sale.timestamp) }}
                <span class="text-gray-400">({{ analytics.last_sale.days_ago }} days ago)</span>
              </p>
            </div>

            <!-- Sales Pattern -->
            <div v-if="analytics.sales_pattern" class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Sales Pattern</h4>
              <div class="text-sm text-gray-600 space-y-1">
                <p>Average: {{ analytics.sales_pattern.average_interval_hours.toFixed(1) }} hours</p>
                <p>Based on {{ analytics.sales_pattern.sales_count }} sales</p>
                <p>Threshold: {{ analytics.sales_pattern.threshold_hours.toFixed(1) }} hours</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, onMounted } from 'vue'
import { useMotorAnalytics } from '../composables/useMotorAnalytics'
import { useAnalyticsStore } from '../stores/analytics'

// Props
interface Props {
  isOpen: boolean
  motorId: number | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
}>()

// Composables and stores
const { fetchAnalytics, analytics, loading, error, clearAnalytics } = useMotorAnalytics()
const analyticsStore = useAnalyticsStore()

// Computed properties for status styling
const statusClasses = computed(() => {
  if (!analytics?.status_indicator) return 'bg-gray-100 text-gray-800'

  const classes = {
    red: 'bg-red-100 text-red-800',
    green: 'bg-green-100 text-green-800',
    neutral: 'bg-gray-100 text-gray-800'
  }
  return classes[analytics.status_indicator] || 'bg-gray-100 text-gray-800'
})

const statusDotClasses = computed(() => {
  if (!analytics?.status_indicator) return 'bg-gray-400'

  const classes = {
    red: 'bg-red-500',
    green: 'bg-green-500',
    neutral: 'bg-gray-400'
  }
  return classes[analytics.status_indicator] || 'bg-gray-400'
})

const statusText = computed(() => {
  if (!analytics?.status_indicator) return 'No Data'

  const text = {
    red: 'Overdue',
    green: 'Normal',
    neutral: 'Insufficient Data'
  }
  return text[analytics.status_indicator] || 'Unknown'
})

// Methods
const closePopup = () => {
  emit('close')
}

const formatLastSale = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

// Watch for motor changes to fetch new data
watch(() => props.motorId, (newMotorId) => {
  if (newMotorId && props.isOpen) {
    loadMotorAnalytics(newMotorId)
  }
}, { immediate: true })

// Watch for popup open/close
watch(() => props.isOpen, (isOpen) => {
  if (!isOpen) {
    clearAnalytics()
  } else if (props.motorId) {
    loadMotorAnalytics(props.motorId)
  }
})

// Watch for store updates to sync local state
watch(() => analyticsStore.getMotorAnalytics(props.motorId || 0), (storeData) => {
  if (storeData && props.isOpen && props.motorId) {
    analytics.value = storeData
  }
})

// Watch for loading and error states from store
watch(() => analyticsStore.isLoading, (storeLoading) => {
  if (props.isOpen && props.motorId) {
    loading.value = storeLoading
  }
})

watch(() => analyticsStore.error, (storeError) => {
  if (props.isOpen && props.motorId) {
    error.value = storeError
  }
})

// Centralized method to load analytics data
const loadMotorAnalytics = async (motorId: number) => {
  // Set loading state
  analyticsStore.setLoading(true)

  // Check cache first
  if (analyticsStore.isMotorCacheValid(motorId)) {
    const cachedData = analyticsStore.getMotorAnalytics(motorId)
    if (cachedData) {
      analytics.value = cachedData
      analyticsStore.setLoading(false)
      return
    }
  }

  try {
    // Fetch fresh data and let the store handle caching
    await fetchAnalytics(motorId)
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to load analytics'
    analyticsStore.setError(errorMessage)
  }
}
</script>