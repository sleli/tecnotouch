<template>
  <Teleport to="body">
    <Transition name="modal" appear>
      <div class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div
          class="modal-content bg-white rounded-t-2xl sm:rounded-2xl shadow-xl w-full sm:max-w-2xl sm:w-full max-h-[90vh] sm:max-h-[85vh] overflow-hidden flex flex-col"
          @click.stop
        >
          <!-- Header -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 safe-top">
            <div class="flex items-center space-x-3">
              <div>
                <h3 class="text-lg font-bold text-gray-900">
                  Motore {{ motor.id }}
                </h3>
                <p
                  v-if="motor.product"
                  class="text-sm text-gray-600"
                >
                  {{ motor.product }}
                </p>
              </div>
            </div>
            <button
              @click="$emit('close')"
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors touch-feedback"
            >
              <X class="w-6 h-6" />
            </button>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto custom-scrollbar">
            <div class="p-4 space-y-6">
              <!-- Status Card -->
              <div class="bg-gray-50 rounded-xl p-4">
                <h4 class="font-semibold text-gray-900 mb-3">Vendite</h4>
                <div class="text-center">
                  <div class="text-3xl font-bold text-blue-600 mb-1">
                    {{ motor.totalSales || 0 }}
                  </div>
                  <p class="text-sm font-medium text-gray-900">Vendite totali</p>
                  <p class="text-xs text-gray-600">Dall'ultima sincronizzazione</p>
                </div>
              </div>

              <!-- Details Grid -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- Product Info -->
                <div class="bg-white border border-gray-200 rounded-xl p-4">
                  <h5 class="font-medium text-gray-900 mb-3 flex items-center">
                    <Package class="w-4 h-4 mr-2" />
                    Prodotto
                  </h5>
                  <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-600">Nome:</span>
                      <span class="font-medium">{{ motor.product || 'N/A' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">Prezzo:</span>
                      <span class="font-medium">
                        {{ motor.price ? `€${formatPrice(motor.price)}` : 'N/A' }}
                      </span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">Categoria:</span>
                      <span class="font-medium">{{ motor.category || 'Sigarette' }}</span>
                    </div>
                  </div>
                </div>

                <!-- Sales Info -->
                <div class="bg-white border border-gray-200 rounded-xl p-4">
                  <h5 class="font-medium text-gray-900 mb-3 flex items-center">
                    <TrendingUp class="w-4 h-4 mr-2" />
                    Vendite
                  </h5>
                  <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-600">Oggi:</span>
                      <span class="font-medium">{{ motor.sales_today || 0 }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">Questa settimana:</span>
                      <span class="font-medium">{{ motor.sales_week || 'N/A' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">Ultima vendita:</span>
                      <span class="font-medium">
                        {{ motor.last_sale ? formatLastSale(motor.last_sale) : 'N/A' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Revenue Info -->
              <div class="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-4">
                <h5 class="font-medium text-gray-900 mb-3 flex items-center">
                  <Euro class="w-4 h-4 mr-2" />
                  Ricavi
                </h5>
                <div class="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div class="text-xl font-bold text-blue-600">
                      €{{ calculateRevenue('today') }}
                    </div>
                    <p class="text-xs text-gray-600">Oggi</p>
                  </div>
                  <div>
                    <div class="text-xl font-bold text-purple-600">
                      €{{ calculateRevenue('week') }}
                    </div>
                    <p class="text-xs text-gray-600">Settimana</p>
                  </div>
                  <div>
                    <div class="text-xl font-bold text-green-600">
                      €{{ calculateRevenue('month') }}
                    </div>
                    <p class="text-xs text-gray-600">Mese</p>
                  </div>
                </div>
              </div>

              <!-- Actions (for future implementation) -->
              <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
                <h5 class="font-medium text-gray-900 mb-3 flex items-center">
                  <Settings class="w-4 h-4 mr-2" />
                  Azioni Rapide
                </h5>
                <div class="grid grid-cols-1 gap-3">
                  <button
                    class="flex items-center justify-center space-x-2 p-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors touch-feedback"
                    @click="viewHistory"
                  >
                    <Clock class="w-4 h-4" />
                    <span class="text-sm">Storico Vendite</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="border-t border-gray-200 p-4 safe-bottom">
            <div class="flex space-x-3">
              <button
                @click="$emit('close')"
                class="flex-1 py-3 px-4 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors touch-feedback"
              >
                Chiudi
              </button>
              <button
                @click="refreshMotorData"
                class="flex-1 py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors touch-feedback flex items-center justify-center space-x-2"
              >
                <RefreshCw class="w-4 h-4" />
                <span>Aggiorna</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { defineEmits, defineProps } from 'vue'
import {
  X,
  Package,
  TrendingUp,
  Euro,
  Settings,
  RefreshCw,
  Clock
} from 'lucide-vue-next'

const emit = defineEmits(['close'])

const props = defineProps({
  motor: {
    type: Object,
    required: true
  }
})

// Methods

const formatPrice = (price) => {
  if (typeof price === 'number') {
    return price.toFixed(2)
  }
  return String(price || '0.00')
}

const formatDate = (date) => {
  return date.toLocaleDateString('it-IT', {
    day: '2-digit',
    month: '2-digit'
  })
}

const formatLastSale = (lastSale) => {
  if (!lastSale) return 'N/A'

  const date = new Date(lastSale)
  if (isNaN(date.getTime())) return 'N/A'

  const now = new Date()
  const diffHours = Math.floor((now - date) / (1000 * 60 * 60))

  if (diffHours < 1) return 'Ora'
  if (diffHours < 24) return `${diffHours}h fa`
  if (diffHours < 48) return 'Ieri'

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays} giorni fa`

  return date.toLocaleDateString('it-IT')
}

const calculateRevenue = (period) => {
  const price = parseFloat(props.motor.price) || 0

  switch (period) {
    case 'today':
      return ((props.motor.sales_today || 0) * price).toFixed(2)
    case 'week':
      return ((props.motor.sales_week || 0) * price).toFixed(2)
    case 'month':
      return ((props.motor.sales_month || 0) * price).toFixed(2)
    default:
      return '0.00'
  }
}


const viewHistory = () => {
  // Future implementation
  if (window.$toast) {
    window.$toast.info('Storico vendite in sviluppo')
  }
}

const refreshMotorData = async () => {
  // Future implementation - refresh specific motor data
  if (window.$toast) {
    window.$toast.success(`Dati motore ${props.motor.id} aggiornati`)
  }
}
</script>

<style scoped>
.modal-backdrop {
  backdrop-filter: blur(4px);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-content {
  transform: translateY(100%);
}

.modal-leave-to .modal-content {
  transform: translateY(100%);
}

@media (min-width: 640px) {
  .modal-enter-from .modal-content {
    transform: scale(0.95) translateY(20px);
  }

  .modal-leave-to .modal-content {
    transform: scale(0.95) translateY(20px);
  }
}
</style>