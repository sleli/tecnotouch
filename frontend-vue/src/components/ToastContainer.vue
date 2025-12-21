<template>
  <div
    class="fixed top-4 right-4 z-50 space-y-3 max-w-sm w-full pointer-events-none safe-top"
  >
    <Transition name="toast" appear>
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast pointer-events-auto"
        :class="[
          `toast-${toast.type}`,
          { 'show': toast.show }
        ]"
      >
        <div class="flex items-start space-x-3 p-4 rounded-lg shadow-lg">
          <component
            :is="getIcon(toast.type)"
            class="w-5 h-5 mt-0.5 flex-shrink-0"
          />
          <div class="flex-1 min-w-0">
            <p
              v-if="toast.title"
              class="font-medium text-sm"
            >
              {{ toast.title }}
            </p>
            <p
              class="text-sm"
              :class="{ 'mt-1': toast.title }"
            >
              {{ toast.message }}
            </p>
          </div>
          <button
            @click="removeToast(toast.id)"
            class="flex-shrink-0 p-1 rounded hover:bg-black hover:bg-opacity-10 transition-colors"
          >
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- Progress bar -->
        <div
          v-if="toast.duration > 0"
          class="h-1 bg-black bg-opacity-20 rounded-b-lg overflow-hidden"
        >
          <div
            class="h-full bg-black bg-opacity-30 toast-progress"
            :style="{ animationDuration: `${toast.duration}ms` }"
          ></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  CheckCircle,
  XCircle,
  Info,
  AlertTriangle,
  X
} from 'lucide-vue-next'

// Toast state
const toasts = ref([])

// Toast icons mapping
const getIcon = (type) => {
  const icons = {
    success: CheckCircle,
    error: XCircle,
    info: Info,
    warning: AlertTriangle
  }
  return icons[type] || Info
}

// Add toast
const addToast = (toast) => {
  const id = Date.now() + Math.random()
  const newToast = {
    id,
    show: false,
    duration: toast.duration || 1500,
    type: toast.type || 'info',
    ...toast
  }

  toasts.value.push(newToast)

  // Show toast with slight delay for animation
  setTimeout(() => {
    const toastIndex = toasts.value.findIndex(t => t.id === id)
    if (toastIndex > -1) {
      toasts.value[toastIndex].show = true
    }
  }, 10)

  // Auto remove if duration is set
  if (newToast.duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, newToast.duration)
  }

  return id
}

// Remove toast
const removeToast = (id) => {
  const toastIndex = toasts.value.findIndex(t => t.id === id)
  if (toastIndex > -1) {
    toasts.value[toastIndex].show = false
    setTimeout(() => {
      toasts.value.splice(toastIndex, 1)
    }, 300)
  }
}

// Global toast methods
onMounted(() => {
  // Make toast methods globally available
  window.$toast = {
    success: (message, options = {}) => addToast({ ...options, type: 'success', message }),
    error: (message, options = {}) => addToast({ ...options, type: 'error', message, duration: 2000 }),
    warning: (message, options = {}) => addToast({ ...options, type: 'warning', message }),
    info: (message, options = {}) => addToast({ ...options, type: 'info', message })
  }
})
</script>

<style scoped>
.toast {
  transform: translateX(100%);
  opacity: 0;
  transition: all 0.3s ease-in-out;
}

.toast.show {
  transform: translateX(0);
  opacity: 1;
}

.toast-success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.toast-error {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.toast-info {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.toast-warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

@keyframes toast-progress {
  0% { width: 100%; }
  100% { width: 0%; }
}

.toast-progress {
  animation: toast-progress linear forwards;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>