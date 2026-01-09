<template>
  <Teleport to="body">
    <Transition name="modal" appear>
      <div class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div
          class="modal-content bg-white rounded-t-2xl sm:rounded-2xl shadow-xl w-full sm:max-w-md sm:w-full max-h-[80vh] overflow-hidden flex flex-col"
          @click.stop
        >
          <!-- Header -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 safe-top">
            <div class="flex items-center space-x-3">
              <div
                class="w-4 h-4 rounded-full"
                :class="systemStatus.api_reachable && systemStatus.distributore_reachable ? 'bg-green-400' : 'bg-red-400'"
              />
              <div>
                <h3 class="text-lg font-bold text-gray-900">Stato Sistema</h3>
                <p class="text-sm text-gray-500">
                  {{ formatTimestamp(systemStatus.last_check) }}
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
          <div class="flex-1 overflow-y-auto p-4">
            <div class="space-y-4">

              <!-- API Status -->
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-gray-900">API Server</h4>
                  <div class="flex items-center space-x-2">
                    <div
                      class="w-3 h-3 rounded-full"
                      :class="systemStatus.api_reachable ? 'bg-green-400' : 'bg-red-400'"
                    />
                    <span
                      class="text-sm font-medium"
                      :class="systemStatus.api_reachable ? 'text-green-600' : 'text-red-600'"
                    >
                      {{ systemStatus.api_reachable ? 'Online' : 'Offline' }}
                    </span>
                  </div>
                </div>
                <p class="text-sm text-gray-600 break-all">
                  {{ systemStatus.api_base_url || 'N/A' }}
                </p>
              </div>

              <!-- Distributore Status -->
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-gray-900">Distributore</h4>
                  <div class="flex items-center space-x-2">
                    <div
                      class="w-3 h-3 rounded-full"
                      :class="systemStatus.distributore_reachable ? 'bg-green-400' : 'bg-red-400'"
                    />
                    <span
                      class="text-sm font-medium"
                      :class="systemStatus.distributore_reachable ? 'text-green-600' : 'text-red-600'"
                    >
                      {{ systemStatus.distributore_reachable ? 'Raggiungibile' : 'Non raggiungibile' }}
                    </span>
                  </div>
                </div>
                <p class="text-sm text-gray-600">
                  {{ systemStatus.distributore_ip || 'N/A' }}
                  {{ systemStatus.distributore_ip === 'localhost' ? ' (Simulatore)' : '' }}
                </p>
              </div>

              <!-- Stato Complessivo -->
              <div class="border-t pt-4">
                <div class="flex items-center space-x-3 mb-3">
                  <div
                    class="w-4 h-4 rounded-full"
                    :class="systemStatus.api_reachable && systemStatus.distributore_reachable ? 'bg-green-400' : 'bg-red-400'"
                  />
                  <span class="font-medium text-gray-900">
                    {{ getOverallStatus() }}
                  </span>
                </div>
                <p class="text-sm text-gray-600 leading-relaxed">
                  {{ getStatusDescription() }}
                </p>
              </div>

            </div>
          </div>

          <!-- Footer -->
          <div class="p-4 border-t border-gray-200 safe-bottom">
            <div class="flex space-x-3">
              <button
                @click="refreshStatus"
                :disabled="isRefreshing"
                class="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
              >
                <RefreshCw
                  class="w-4 h-4"
                  :class="{ 'animate-spin': isRefreshing }"
                />
                <span>{{ isRefreshing ? 'Verificando...' : 'Riprova' }}</span>
              </button>
              <button
                @click="$emit('close')"
                class="px-6 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
              >
                Chiudi
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useAppStore } from '@/stores/app'
import { X, RefreshCw } from 'lucide-vue-next'

// Props
defineProps({
  systemStatus: {
    type: Object,
    required: true
  }
})

// Emits
defineEmits(['close'])

// Store
const appStore = useAppStore()

// Local state
const isRefreshing = ref(false)

// Computed
const getOverallStatus = () => {
  if (appStore.systemStatus.api_reachable && appStore.systemStatus.distributore_reachable) {
    return 'Sistema Operativo'
  } else if (!appStore.systemStatus.api_reachable) {
    return 'API Server Offline'
  } else {
    return 'Distributore Non Raggiungibile'
  }
}

const getStatusDescription = () => {
  if (appStore.systemStatus.api_reachable && appStore.systemStatus.distributore_reachable) {
    return 'Tutti i servizi sono online e funzionanti. Il sistema è pronto per le operazioni.'
  } else if (!appStore.systemStatus.api_reachable) {
    return 'Il server API non è raggiungibile. Verificare la connessione di rete e che il server sia avviato.'
  } else {
    return 'Il distributore sigarette non risponde. Controllare lo stato fisico del dispositivo e la connessione di rete.'
  }
}

// Methods
const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'Mai verificato'

  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)

  if (diff < 10) return 'Ora'
  if (diff < 60) return `${diff} sec fa`
  if (diff < 3600) return `${Math.floor(diff / 60)} min fa`
  return date.toLocaleString('it-IT')
}

const refreshStatus = async () => {
  isRefreshing.value = true
  try {
    // Passa force=true per bypassare la cache e avere dati freschi
    await appStore.checkApiHealth(true)

    // Toast notification se disponibile
    if (window.$toast) {
      window.$toast.success('Stato sistema aggiornato')
    }
  } catch (error) {
    console.error('Errore refresh status:', error)
    if (window.$toast) {
      window.$toast.error('Errore aggiornamento stato')
    }
  } finally {
    isRefreshing.value = false
  }
}
</script>

<style scoped>
/* Modal animations */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: translateY(100%);
}

@media (min-width: 640px) {
  .modal-enter-from .modal-content,
  .modal-leave-to .modal-content {
    transform: translateY(0) scale(0.95);
  }
}

/* Safe area support per mobile */
.safe-top {
  padding-top: max(1rem, env(safe-area-inset-top));
}

.safe-bottom {
  padding-bottom: max(1rem, env(safe-area-inset-bottom));
}

/* Touch feedback */
.touch-feedback {
  touch-action: manipulation;
}

.touch-feedback:active {
  transform: scale(0.98);
}
</style>