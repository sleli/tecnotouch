<template>
  <!-- DEBUG: Cache Buster v2.0 -->
  <div class="statistics-view h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-4 py-3 flex-shrink-0 safe-top">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-gray-900">Statistiche</h1>
          <p class="text-sm text-gray-500">Analisi vendite e performance</p>
        </div>
        <button
          @click="refreshStats"
          :disabled="loading"
          class="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors touch-feedback"
        >
          <RefreshCw
            class="w-5 h-5"
            :class="{ 'animate-spin': loading }"
          />
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar pb-20">
      <div class="p-4 space-y-6">
        <!-- Date Filter -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-3">Periodo</h3>

          <!-- Quick Filter Buttons -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
            <button
              @click="setQuickFilter('today')"
              :disabled="loading"
              :class="[
                'px-3 py-2 text-sm font-medium rounded-lg transition-colors touch-feedback disabled:opacity-50',
                activeFilter === 'today' ? 'bg-blue-100 text-blue-700 border-2 border-blue-300' : 'bg-gray-50 text-gray-700 border border-gray-300 hover:bg-gray-100'
              ]"
            >
              Oggi
            </button>
            <button
              @click="setQuickFilter('week')"
              :disabled="loading"
              :class="[
                'px-3 py-2 text-sm font-medium rounded-lg transition-colors touch-feedback disabled:opacity-50',
                activeFilter === 'week' ? 'bg-blue-100 text-blue-700 border-2 border-blue-300' : 'bg-gray-50 text-gray-700 border border-gray-300 hover:bg-gray-100'
              ]"
            >
              Ultima Settimana
            </button>
            <button
              @click="setQuickFilter('month')"
              :disabled="loading"
              :class="[
                'px-3 py-2 text-sm font-medium rounded-lg transition-colors touch-feedback disabled:opacity-50',
                activeFilter === 'month' ? 'bg-blue-100 text-blue-700 border-2 border-blue-300' : 'bg-gray-50 text-gray-700 border border-gray-300 hover:bg-gray-100'
              ]"
            >
              Mese Corrente
            </button>
            <button
              @click="setQuickFilter('custom')"
              :disabled="loading"
              :class="[
                'px-3 py-2 text-sm font-medium rounded-lg transition-colors touch-feedback disabled:opacity-50',
                activeFilter === 'custom' ? 'bg-blue-100 text-blue-700 border-2 border-blue-300' : 'bg-gray-50 text-gray-700 border border-gray-300 hover:bg-gray-100'
              ]"
            >
              Personalizzato
            </button>
          </div>

          <!-- Custom Date Inputs (shown only when custom is selected) -->
          <div v-show="activeFilter === 'custom'" class="flex flex-col sm:flex-row gap-3">
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700 whitespace-nowrap">Da:</label>
              <input
                v-model="dateFilter.from"
                type="date"
                class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-10 touch-feedback"
              >
            </div>
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700 whitespace-nowrap">A:</label>
              <input
                v-model="dateFilter.to"
                type="date"
                class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-10 touch-feedback"
              >
            </div>
            <button
              @click="applyDateFilter"
              :disabled="loading"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors min-h-10 touch-feedback disabled:opacity-50"
            >
              Applica
            </button>
          </div>
        </div>

        <!-- Overview KPIs -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KPICard
            title="Vendite Totali"
            :value="stats.totalSales"
            :loading="loading"
            icon="TrendingUp"
            color="blue"
            subtitle="nel periodo"
          />
          <KPICard
            title="Ricavi Totali"
            :value="formatCurrency(stats.totalRevenue)"
            :loading="loading"
            icon="Euro"
            color="green"
            subtitle="ricavi netti"
          />
          <KPICard
            title="Prodotti Diversi"
            :value="stats.uniqueProducts"
            :loading="loading"
            icon="Package"
            color="purple"
            subtitle="tipologie vendute"
          />
        </div>

        <!-- Charts Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Revenue by Payment Method -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Pagamenti</h3>
              <button class="text-sm text-blue-600 hover:text-blue-700 px-3 py-1 rounded touch-feedback">
                Dettagli
              </button>
            </div>
            <div class="h-48">
              <PaymentMethodChart
                :data="chartData.paymentMethods"
                :loading="loading"
              />
            </div>
          </div>

          <!-- Top Products -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">
                Top Prodotti {{ viewMode === 'tipologia' ? '(Tipologie)' : '(Marche)' }}
              </h3>
              <div class="flex items-center space-x-2">
                <!-- Toggle buttons -->
                <div class="flex bg-gray-100 rounded-lg p-1">
                  <button
                    @click="viewMode = 'tipologia'"
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded transition-colors touch-feedback',
                      viewMode === 'tipologia'
                        ? 'bg-white text-blue-700 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    ]"
                  >
                    T
                  </button>
                  <button
                    @click="viewMode = 'marca'"
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded transition-colors touch-feedback',
                      viewMode === 'marca'
                        ? 'bg-white text-blue-700 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    ]"
                  >
                    M
                  </button>
                </div>
              </div>
            </div>
            <div class="h-48">
              <TopProductsChart
                :data="displayTopProducts"
                :loading="loading"
              />
            </div>
          </div>
        </div>

        <!-- Detailed Tables -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Package Type/Brand Statistics -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">
                {{ viewMode === 'tipologia' ? 'Per Tipologia' : 'Per Marca' }}
              </h3>
              <div class="flex items-center space-x-2">
                <!-- Toggle buttons -->
                <div class="flex bg-gray-100 rounded-lg p-1">
                  <button
                    @click="viewMode = 'tipologia'"
                    :class="[
                      'px-3 py-1 text-xs font-medium rounded transition-colors touch-feedback',
                      viewMode === 'tipologia'
                        ? 'bg-white text-blue-700 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    ]"
                  >
                    Tipologia
                  </button>
                  <button
                    @click="viewMode = 'marca'"
                    :class="[
                      'px-3 py-1 text-xs font-medium rounded transition-colors touch-feedback',
                      viewMode === 'marca'
                        ? 'bg-white text-blue-700 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    ]"
                  >
                    Marca
                  </button>
                </div>
                <button
                  @click="exportBrandStats"
                  class="text-sm text-blue-600 hover:text-blue-700 px-3 py-1 rounded touch-feedback"
                >
                  Esporta
                </button>
              </div>
            </div>
            <div class="overflow-x-auto custom-scrollbar">
              <table class="w-full text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left font-medium text-gray-900">
                      {{ viewMode === 'tipologia' ? 'Tipologia' : 'Marca' }}
                    </th>
                    <th class="px-3 py-2 text-right font-medium text-gray-900">Vendite</th>
                    <th class="px-3 py-2 text-right font-medium text-gray-900">Ricavi</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-if="loading">
                    <td colspan="3" class="px-3 py-8 text-center text-gray-500">
                      <div class="loading-spinner mx-auto mb-2"></div>
                      Caricamento...
                    </td>
                  </tr>
                  <tr
                    v-else
                    v-for="item in displayStats"
                    :key="item.name"
                    class="hover:bg-gray-50"
                  >
                    <td class="px-3 py-2 font-medium text-gray-900">{{ item.name || 'N/A' }}</td>
                    <td class="px-3 py-2 text-right text-gray-600">{{ item.sales || 0 }}</td>
                    <td class="px-3 py-2 text-right text-gray-600">€{{ (item.revenue || 0).toFixed(2) }}</td>
                  </tr>
                  <tr v-if="!loading && displayStats.length === 0">
                    <td colspan="3" class="px-3 py-8 text-center text-gray-500">
                      Nessun dato disponibile
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Recent Transactions -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Transazioni Recenti</h3>
              <button
                @click="showAllTransactions"
                class="text-sm text-blue-600 hover:text-blue-700 px-3 py-1 rounded touch-feedback"
              >
                Vedi tutte
              </button>
            </div>
            <div class="space-y-3 custom-scrollbar max-h-80 overflow-y-auto">
              <div v-if="loading" class="text-center text-gray-500 py-8">
                <div class="loading-spinner mx-auto mb-2"></div>
                Caricamento transazioni...
              </div>
              <div
                v-else
                v-for="transaction in recentTransactions"
                :key="transaction.id"
                class="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                  <div>
                    <p class="font-medium text-gray-900 text-sm">{{ transaction.product }}</p>
                    <p class="text-xs text-gray-500">{{ formatTimestamp(transaction.timestamp) }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-medium text-gray-900 text-sm">€{{ transaction.amount.toFixed(2) }}</p>
                  <p class="text-xs text-gray-500">{{ transaction.motor }}</p>
                </div>
              </div>
              <div v-if="!loading && recentTransactions.length === 0" class="text-center text-gray-500 py-8">
                Nessuna transazione recente
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useApi, API_ENDPOINTS } from '@/composables/useApi'
import { RefreshCw } from 'lucide-vue-next'
import KPICard from '@/components/KPICard.vue'
import PaymentMethodChart from '@/components/charts/PaymentMethodChart.vue'
import TopProductsChart from '@/components/charts/TopProductsChart.vue'

// Composables
const { get } = useApi()

// State
const loading = ref(false)
const activeFilter = ref('week')
const viewMode = ref('tipologia') // 'tipologia' | 'marca'
const dateFilter = reactive({
  from: '',
  to: ''
})

const stats = reactive({
  totalSales: 0,
  totalRevenue: 0,
  uniqueProducts: 0
})

const chartData = reactive({
  paymentMethods: [],
  topProducts: []
})

const brandStats = ref([])
const recentTransactions = ref([])

// Methods
const formatCurrency = (value) => {
  if (typeof value !== 'number') return '€0.00'
  return `€${value.toFixed(2)}`
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  const now = new Date()
  const diffHours = Math.floor((now - date) / (1000 * 60 * 60))

  if (diffHours < 1) return 'Ora'
  if (diffHours < 24) return `${diffHours}h fa`
  if (diffHours < 48) return 'Ieri'

  return date.toLocaleDateString('it-IT', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const extractBrandFromProduct = (productName) => {
  if (!productName) return "UNKNOWN"

  const productUpper = productName.toUpperCase()

  // Mappatura marche principali (identica al backend)
  const brands = {
    'MARLBORO': ['MARLBORO'],
    'CAMEL': ['CAMEL'],
    'WINSTON': ['WINSTON'],
    'PHILIP MORRIS': ['PHILIP MORRIS'],
    'CHESTERFIELD': ['CHESTERFIELD'],
    'LUCKY STRIKE': ['LUCKY STRIKE'],
    'ROTHMANS': ['ROTHMANS'],
    'MERIT': ['MERIT'],
    'JPS': ['JPS'],
    'DIANA': ['DIANA'],
    'CHIARAVALLE': ['CHIARAVALLE']
  }

  for (const [brand, keywords] of Object.entries(brands)) {
    if (keywords.some(keyword => productUpper.includes(keyword))) {
      return brand
    }
  }

  return "OTHER"
}

// Computed properties for dynamic data display
const displayStats = computed(() => {
  if (viewMode.value === 'tipologia') {
    return brandStats.value
  }

  // Aggregate by brand
  const brandMap = new Map()

  brandStats.value.forEach(item => {
    const brand = extractBrandFromProduct(item.name)

    if (brandMap.has(brand)) {
      const existing = brandMap.get(brand)
      existing.sales += item.sales
      existing.revenue += item.revenue
    } else {
      brandMap.set(brand, {
        name: brand,
        sales: item.sales,
        revenue: item.revenue
      })
    }
  })

  return Array.from(brandMap.values()).sort((a, b) => b.revenue - a.revenue)
})

const displayTopProducts = computed(() => {
  return displayStats.value
    .sort((a, b) => b.sales - a.sales)
    .slice(0, 5)
    .map(item => ({
      name: item.name,
      sales: item.sales
    }))
})

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'tipologia' ? 'marca' : 'tipologia'
}

const initDateFilter = () => {
  // Initialize without date filters - show all data by default
  dateFilter.from = ''
  dateFilter.to = ''
  activeFilter.value = ''
}

const setQuickFilter = async (filterType, autoApply = true) => {
  activeFilter.value = filterType
  const today = new Date()

  switch (filterType) {
    case 'today':
      dateFilter.from = today.toISOString().split('T')[0]
      dateFilter.to = today.toISOString().split('T')[0]
      break
    case 'week':
      const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
      dateFilter.from = lastWeek.toISOString().split('T')[0]
      dateFilter.to = today.toISOString().split('T')[0]
      break
    case 'month':
      const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
      dateFilter.from = firstDay.toISOString().split('T')[0]
      dateFilter.to = today.toISOString().split('T')[0]
      break
    case 'custom':
      // Keep current dates, don't auto-apply
      return
  }

  if (autoApply) {
    await loadStatistics()
    if (window.$toast) {
      const filterNames = {
        today: 'Oggi',
        week: 'Ultima Settimana',
        month: 'Mese Corrente'
      }
      window.$toast.success(`Filtro applicato: ${filterNames[filterType]}`)
    }
  }
}

const loadStatistics = async () => {
  try {
    loading.value = true

    // Load overview stats from API
    try {
      const params = {}
      if (dateFilter.from) params.date_from = dateFilter.from
      if (dateFilter.to) params.date_to = dateFilter.to

      const overviewData = await get(API_ENDPOINTS.STATS_OVERVIEW, {
        params: params
      })

      if (overviewData) {
        stats.totalSales = overviewData.total_sales || 0
        stats.totalRevenue = overviewData.total_revenue || 0

        // Calculate unique products from package type data that we load separately
        // Don't use payment methods for product count - that's incorrect
        stats.uniqueProducts = 0 // Will be updated from package type data
      }
    } catch (error) {
      console.error('Failed to load overview stats:', error)
      // Use fallback values
      stats.totalSales = 0
      stats.totalRevenue = 0
      stats.uniqueProducts = 0
    }

    // Load package type statistics
    try {
      const params = {}
      if (dateFilter.from) params.date_from = dateFilter.from
      if (dateFilter.to) params.date_to = dateFilter.to

      const packages = await get(API_ENDPOINTS.STATS_PACKAGE_TYPES, {
        params: params
      })

      brandStats.value = packages.map(packageType => {
        return {
          name: packageType.package_type,
          sales: packageType.quantity,
          revenue: packageType.revenue
        }
      })

      // Update unique products count from package type data
      stats.uniqueProducts = brandStats.value.length
    } catch (error) {
      console.error('Failed to load package type stats:', error)
      brandStats.value = []
    }

    // Load chart data
    await loadChartData()

    // Load recent transactions
    await loadRecentTransactions()

  } catch (error) {
    console.error('Failed to load statistics:', error)
    if (window.$toast) {
      window.$toast.error('Errore nel caricamento statistiche')
    }
  } finally {
    loading.value = false
  }
}

const loadChartData = async () => {
  try {
    // Load overview to get payment methods data
    const params = {}
    if (dateFilter.from) params.date_from = dateFilter.from
    if (dateFilter.to) params.date_to = dateFilter.to

    const overviewData = await get(API_ENDPOINTS.STATS_OVERVIEW, {
      params: params
    })

    if (overviewData?.payment_methods) {
      chartData.paymentMethods = Object.entries(overviewData.payment_methods).map(([method, data]) => ({
        method: method === 'CASH' ? 'Contanti' : method === 'POS' ? 'Carta' : method,
        amount: data.revenue || 0,
        count: data.count || 0,
        percentage: Math.round((data.revenue / overviewData.total_revenue) * 100) || 0
      }))
    } else {
      chartData.paymentMethods = []
    }
  } catch (error) {
    console.error('Failed to load payment methods:', error)
    chartData.paymentMethods = []
  }

  // Note: Top products data is now handled by displayTopProducts computed property
}

const loadRecentTransactions = async () => {
  try {
    const params = { limit: 20 }
    if (dateFilter.from) params.date_from = dateFilter.from
    if (dateFilter.to) params.date_to = dateFilter.to

    const transactions = await get(API_ENDPOINTS.STATS_PAYMENTS, {
      params: params
    })

    if (Array.isArray(transactions)) {
      recentTransactions.value = transactions.map(transaction => ({
        id: transaction.id,
        product: `Transazione ${transaction.id}`, // API doesn't provide product name
        amount: transaction.net_revenue,
        motor: `Metodo: ${transaction.payment_method}`,
        timestamp: parseTransactionDate(transaction.start_datetime)
      }))
    } else {
      recentTransactions.value = []
    }
  } catch (error) {
    console.error('Failed to load recent transactions:', error)
    recentTransactions.value = []
  }
}

const parseTransactionDate = (dateStr) => {
  try {
    // API provides dates like "31/08/25 23:44:01"
    const [datePart, timePart] = dateStr.split(' ')
    const [day, month, year] = datePart.split('/')
    const fullYear = `20${year}` // Convert 25 to 2025

    return new Date(`${fullYear}-${month}-${day}T${timePart}`)
  } catch (error) {
    return new Date()
  }
}

const applyDateFilter = async () => {
  if (!dateFilter.from || !dateFilter.to) {
    if (window.$toast) {
      window.$toast.warning('Seleziona entrambe le date')
    }
    return
  }

  activeFilter.value = 'custom'
  await loadStatistics()

  if (window.$toast) {
    window.$toast.success('Filtro personalizzato applicato')
  }
}

const refreshStats = async () => {
  await loadStatistics()

  if (window.$toast) {
    window.$toast.success('Statistiche aggiornate')
  }
}

// Expose refresh method to parent
defineExpose({
  refreshStats
})

const exportBrandStats = () => {
  // Mock export functionality
  if (window.$toast) {
    window.$toast.info('Export funzionalità in sviluppo')
  }
}

const showAllTransactions = async () => {
  try {
    loading.value = true

    // Load more transactions (increase limit significantly)
    const params = { limit: 500 } // Much higher limit for "view all"
    if (dateFilter.from) params.date_from = dateFilter.from
    if (dateFilter.to) params.date_to = dateFilter.to

    const allTransactions = await get(API_ENDPOINTS.STATS_PAYMENTS, {
      params: params
    })

    if (Array.isArray(allTransactions)) {
      recentTransactions.value = allTransactions.map(transaction => ({
        id: transaction.id,
        product: `Transazione ${transaction.id}`,
        amount: transaction.net_revenue,
        motor: `Metodo: ${transaction.payment_method}`,
        timestamp: parseTransactionDate(transaction.start_datetime)
      }))

      if (window.$toast) {
        window.$toast.success(`Caricate ${allTransactions.length} transazioni`)
      }
    }
  } catch (error) {
    console.error('Failed to load all transactions:', error)
    if (window.$toast) {
      window.$toast.error('Errore nel caricamento delle transazioni')
    }
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  initDateFilter()
  loadStatistics()
})
</script>

<style scoped>
.statistics-view {
  /* Account for bottom navigation */
  padding-bottom: env(safe-area-inset-bottom);
}

.loading-spinner {
  @apply w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin;
}

/* Custom table styling for mobile */
@media (max-width: 640px) {
  table {
    font-size: 0.875rem;
  }

  th, td {
    padding: 0.5rem 0.25rem;
  }
}
</style>