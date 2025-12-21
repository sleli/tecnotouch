<template>
  <div class="motor-grid-container">

    <!-- Motors grid -->
    <div class="relative">
      <!-- Loading state -->
      <div
        v-if="appStore.isLoading && motorsStore.motors.length === 0"
        class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-4 p-4"
      >
        <div
          v-for="n in 20"
          :key="`skeleton-${n}`"
          class="aspect-square bg-gray-200 rounded-lg animate-pulse"
        />
      </div>

      <!-- Motors -->
      <div
        v-else-if="motorsStore.filteredMotors.length > 0"
        class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-4 p-4"
      >
        <MotorCard
          v-for="motor in motorsStore.filteredMotors"
          :key="motor.id"
          :motor="motor"
          @click="handleMotorClick(motor)"
          @long-press="handleMotorLongPress(motor)"
        />
      </div>

      <!-- Empty state -->
      <div
        v-else
        class="text-center py-12 px-4"
      >
        <Grid3x3 class="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          Nessun motore trovato
        </h3>
        <p class="text-gray-600 mb-4">
          {{ getEmptyStateMessage() }}
        </p>
        <button
          @click="motorsStore.setFilter('all')"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors touch-feedback"
        >
          Mostra tutti
        </button>
      </div>
    </div>

    <!-- Motor detail popup with analytics -->
    <MotorDetailPopup
      :is-open="selectedMotor !== null"
      :motor-id="selectedMotor?.id || null"
      @close="selectedMotor = null"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMotorsStore } from '@/stores/motors'
import { useAppStore } from '@/stores/app'
import { Grid3x3 } from 'lucide-vue-next'
import MotorCard from './MotorCard.vue'
import MotorDetailPopup from './MotorDetailPopup.vue'

const motorsStore = useMotorsStore()
const appStore = useAppStore()

// Local state
const selectedMotor = ref(null)

// Computed
const getEmptyStateMessage = () => {
  return 'Non ci sono motori da visualizzare'
}

// Methods
const handleMotorClick = (motor) => {
  selectedMotor.value = motor
  motorsStore.selectMotor(motor)

  // Haptic feedback
  if (navigator.vibrate) {
    navigator.vibrate(50)
  }
}

const handleMotorLongPress = (motor) => {
  // Long press for quick actions
  if (navigator.vibrate) {
    navigator.vibrate([50, 50, 50])
  }

  // Could open context menu or quick actions
  handleMotorClick(motor)
}


// Lifecycle
onMounted(() => {
  // Start auto refresh
  motorsStore.startAutoRefresh()
})

onUnmounted(() => {
  // Stop auto refresh
  motorsStore.stopAutoRefresh()
})
</script>

<style scoped>
.filter-btn {
  @apply px-3 py-2 rounded-lg font-medium text-sm transition-all duration-200 min-h-10 flex items-center;
}

.motor-grid-container {
  @apply pb-20; /* Account for bottom navigation */
}

/* Custom scrollbar */
.motor-grid-container ::-webkit-scrollbar {
  width: 4px;
}

.motor-grid-container ::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.motor-grid-container ::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}
</style>