<template>
  <div class="h-full flex flex-col">
    <!-- Main content area -->
    <main class="flex-1 overflow-hidden">
      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" ref="currentView" />
        </Transition>
      </RouterView>
    </main>

    <!-- Mobile bottom navigation -->
    <BottomNavigation />

    <!-- Toast notifications -->
    <ToastContainer />

    <!-- Loading overlay -->
    <LoadingOverlay v-if="appStore.isLoading" />

  </div>
</template>

<script setup>
import { RouterView, useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useMotorsStore } from '@/stores/motors'
import { useAlertStore } from '@/stores/alerts'
import BottomNavigation from '@/components/BottomNavigation.vue'
import ToastContainer from '@/components/ToastContainer.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const appStore = useAppStore()
const motorsStore = useMotorsStore()
const alertStore = useAlertStore()
const route = useRoute()
const currentView = ref(null)


onMounted(() => {
  // Clear any cached data that might contain old stock information
  motorsStore.clearCachedMotors()
  alertStore.clearAllAlerts()

  // Initialize app
  appStore.init()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Ensure smooth transitions for pull indicator */
.pull-indicator {
  transition: transform 0.2s ease-out;
}
</style>