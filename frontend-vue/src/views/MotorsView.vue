<template>
  <div class="motors-view h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-4 py-3 flex-shrink-0 safe-top">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-gray-900">Motori</h1>
          <p class="text-sm text-gray-500">
            {{ motorsStore.totalMotors }} motori totali
          </p>
        </div>
        <button
          @click="motorsStore.refreshMotors"
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

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <MotorGrid />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useMotorsStore } from '@/stores/motors'
import { RefreshCw } from 'lucide-vue-next'
import MotorGrid from '@/components/MotorGrid.vue'

const appStore = useAppStore()
const motorsStore = useMotorsStore()

onMounted(() => {
  // Load motors if not already loaded
  if (motorsStore.motors.length === 0) {
    motorsStore.fetchMotors()
  }
})
</script>