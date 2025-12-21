<template>
  <Transition name="fade">
    <div class="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
      <div class="text-center">
        <div class="loading-spinner mx-auto mb-4 w-8 h-8"></div>
        <p class="text-gray-600 font-medium">{{ message }}</p>
        <p v-if="subMessage" class="text-gray-500 text-sm mt-1">{{ subMessage }}</p>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  message: {
    type: String,
    default: 'Caricamento...'
  },
  subMessage: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.loading-spinner {
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>