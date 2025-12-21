<template>
  <div
    class="alert-card touch-feedback"
    :class="[
      `alert-${alert.level}`,
      { 'alert-unread': !alert.read },
      { 'alert-compact': compact }
    ]"
    @click="$emit('click', alert)"
  >
    <div class="flex items-start space-x-3">
      <!-- Icon -->
      <div
        class="flex-shrink-0 p-2 rounded-full"
        :class="iconBgClass"
      >
        <component
          :is="alertIcon"
          class="w-5 h-5"
          :class="iconColorClass"
        />
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h4
              class="font-medium text-gray-900 truncate"
              :class="{ 'text-sm': compact }"
            >
              {{ alert.title }}
            </h4>
            <p
              class="text-gray-600 mt-1"
              :class="compact ? 'text-xs' : 'text-sm'"
            >
              {{ alert.message }}
            </p>
          </div>

          <!-- Timestamp -->
          <div class="flex-shrink-0 ml-2">
            <p
              class="text-gray-500 text-right"
              :class="compact ? 'text-xs' : 'text-xs'"
            >
              {{ formatTimestamp(alert.timestamp) }}
            </p>
          </div>
        </div>

        <!-- Actions (for non-compact cards) -->
        <div v-if="!compact" class="flex items-center justify-between mt-3">
          <div class="flex items-center space-x-2">
            <!-- Unread indicator -->
            <span
              v-if="!alert.read"
              class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full"
            >
              Nuovo
            </span>

            <!-- Motor link (if applicable) -->
            <button
              v-if="alert.motorId"
              @click.stop="navigateToMotor(alert.motorId)"
              class="text-xs text-blue-600 hover:text-blue-700 px-2 py-1 rounded hover:bg-blue-50 transition-colors"
            >
              Motore {{ alert.motorId }}
            </button>
          </div>

          <!-- Dismiss button -->
          <button
            @click.stop="$emit('dismiss', alert)"
            class="p-1 text-gray-400 hover:text-red-600 rounded transition-colors touch-feedback"
            title="Rimuovi alert"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  X
} from 'lucide-vue-next'

const router = useRouter()

const props = defineProps({
  alert: {
    type: Object,
    required: true
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'dismiss'])

// Alert level configuration
const alertConfig = {
  critical: {
    icon: XCircle,
    bgClass: 'bg-red-100',
    iconClass: 'text-red-600',
    cardClass: 'border-red-200 bg-red-50'
  },
  warning: {
    icon: AlertTriangle,
    bgClass: 'bg-yellow-100',
    iconClass: 'text-yellow-600',
    cardClass: 'border-yellow-200 bg-yellow-50'
  },
  info: {
    icon: Info,
    bgClass: 'bg-blue-100',
    iconClass: 'text-blue-600',
    cardClass: 'border-blue-200 bg-blue-50'
  },
  success: {
    icon: CheckCircle,
    bgClass: 'bg-green-100',
    iconClass: 'text-green-600',
    cardClass: 'border-green-200 bg-green-50'
  }
}

// Computed
const config = computed(() => {
  return alertConfig[props.alert.level] || alertConfig.info
})

const alertIcon = computed(() => config.value.icon)
const iconBgClass = computed(() => config.value.bgClass)
const iconColorClass = computed(() => config.value.iconClass)

// Methods
const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'Ora'
  if (diffMins < 60) return `${diffMins}m fa`
  if (diffHours < 24) return `${diffHours}h fa`
  if (diffDays < 7) return `${diffDays}g fa`

  return date.toLocaleDateString('it-IT', {
    day: '2-digit',
    month: '2-digit'
  })
}

const navigateToMotor = (motorId) => {
  // Navigate to motors view and potentially highlight specific motor
  router.push({
    name: 'motors',
    query: { highlight: motorId }
  })

  if (window.$toast) {
    window.$toast.info(`Mostrando motore ${motorId}`)
  }
}
</script>

<style scoped>
.alert-card {
  @apply bg-white border rounded-xl p-4 cursor-pointer transition-all duration-200;
}

.alert-card:hover {
  @apply shadow-md;
}

.alert-card.alert-compact {
  @apply p-3;
}

.alert-card.alert-unread {
  @apply border-l-4;
}

.alert-card.alert-critical {
  @apply border-red-200 bg-red-50;
}

.alert-card.alert-critical.alert-unread {
  @apply border-l-red-500;
}

.alert-card.alert-warning {
  @apply border-yellow-200 bg-yellow-50;
}

.alert-card.alert-warning.alert-unread {
  @apply border-l-yellow-500;
}

.alert-card.alert-info {
  @apply border-blue-200 bg-blue-50;
}

.alert-card.alert-info.alert-unread {
  @apply border-l-blue-500;
}

.alert-card.alert-success {
  @apply border-green-200 bg-green-50;
}

.alert-card.alert-success.alert-unread {
  @apply border-l-green-500;
}
</style>