<template>
  <Teleport to="body">
    <Transition name="modal" appear>
      <div class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div
          class="modal-content bg-white rounded-t-2xl sm:rounded-2xl shadow-xl w-full sm:max-w-lg sm:w-full max-h-[80vh] overflow-hidden flex flex-col"
          @click.stop
        >
          <!-- Header -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 safe-top">
            <div class="flex items-center space-x-3">
              <div
                class="p-2 rounded-full"
                :class="iconBgClass"
              >
                <component
                  :is="alertIcon"
                  class="w-5 h-5"
                  :class="iconColorClass"
                />
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">{{ alert.title }}</h3>
                <p class="text-sm text-gray-500">{{ formatTimestamp(alert.timestamp) }}</p>
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
              <!-- Alert Message -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Messaggio</h4>
                <p class="text-gray-900 leading-relaxed">{{ alert.message }}</p>
              </div>

              <!-- Alert Details -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 mb-3">Dettagli</h4>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Livello:</span>
                    <span
                      class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="levelBadgeClass"
                    >
                      {{ levelLabel }}
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Data/Ora:</span>
                    <span class="font-medium">{{ fullTimestamp }}</span>
                  </div>
                  <div v-if="alert.motorId" class="flex justify-between">
                    <span class="text-gray-600">Motore:</span>
                    <span class="font-medium">{{ alert.motorId }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Stato:</span>
                    <span
                      class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="alert.read ? 'bg-gray-100 text-gray-600' : 'bg-blue-100 text-blue-600'"
                    >
                      {{ alert.read ? 'Letto' : 'Non letto' }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Motor-specific actions -->
              <div v-if="alert.motorId" class="bg-blue-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 mb-3">Azioni Rapide</h4>
                <div class="space-y-2">
                  <button
                    @click="navigateToMotor"
                    class="w-full flex items-center justify-center space-x-2 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors touch-feedback"
                  >
                    <Grid3x3 class="w-4 h-4" />
                    <span>Visualizza Motore {{ alert.motorId }}</span>
                  </button>
                </div>
              </div>

              <!-- System alert info -->
              <div v-else class="bg-green-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 mb-2">Informazioni Sistema</h4>
                <p class="text-sm text-gray-600">
                  Questo è un alert di sistema che non richiede azioni specifiche sui motori.
                </p>
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
                @click="handleDismiss"
                class="flex-1 py-3 px-4 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors touch-feedback flex items-center justify-center space-x-2"
              >
                <Trash2 class="w-4 h-4" />
                <span>Rimuovi</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  X,
  Grid3x3,
  Trash2,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle
} from 'lucide-vue-next'

const router = useRouter()

const props = defineProps({
  alert: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'dismiss'])

// Alert level configuration
const alertConfig = {
  critical: {
    icon: XCircle,
    bgClass: 'bg-red-100',
    iconClass: 'text-red-600',
    badgeClass: 'bg-red-100 text-red-800',
    label: 'Critico'
  },
  warning: {
    icon: AlertTriangle,
    bgClass: 'bg-yellow-100',
    iconClass: 'text-yellow-600',
    badgeClass: 'bg-yellow-100 text-yellow-800',
    label: 'Avviso'
  },
  info: {
    icon: Info,
    bgClass: 'bg-blue-100',
    iconClass: 'text-blue-600',
    badgeClass: 'bg-blue-100 text-blue-800',
    label: 'Informazione'
  },
  success: {
    icon: CheckCircle,
    bgClass: 'bg-green-100',
    iconClass: 'text-green-600',
    badgeClass: 'bg-green-100 text-green-800',
    label: 'Successo'
  }
}

// Computed properties
const config = computed(() => {
  return alertConfig[props.alert.level] || alertConfig.info
})

const alertIcon = computed(() => config.value.icon)
const iconBgClass = computed(() => config.value.bgClass)
const iconColorClass = computed(() => config.value.iconClass)
const levelBadgeClass = computed(() => config.value.badgeClass)
const levelLabel = computed(() => config.value.label)

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMins / 60)

  if (diffMins < 1) return 'Ora'
  if (diffMins < 60) return `${diffMins} minuti fa`
  if (diffHours < 24) return `${diffHours} ore fa`

  return date.toLocaleDateString('it-IT', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fullTimestamp = computed(() => {
  if (!props.alert.timestamp) return 'N/A'

  const date = new Date(props.alert.timestamp)
  return date.toLocaleDateString('it-IT', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

// Methods
const navigateToMotor = () => {
  router.push({
    name: 'motors',
    query: { highlight: props.alert.motorId }
  })

  emit('close')

  if (window.$toast) {
    window.$toast.info(`Navigando al motore ${props.alert.motorId}`)
  }
}


const handleDismiss = () => {
  emit('dismiss', props.alert)
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