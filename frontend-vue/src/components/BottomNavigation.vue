<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 safe-bottom">
    <div class="flex justify-around py-1">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.to"
        class="flex flex-col items-center py-2 px-3 min-h-16 min-w-16 touch-feedback transition-colors rounded-lg"
        :class="[
          isActive(item.name)
            ? 'text-blue-600 bg-blue-50'
            : 'text-gray-600 hover:text-gray-900'
        ]"
        @click="handleNavClick(item)"
      >
        <component
          :is="item.icon"
          :class="[
            'w-6 h-6 mb-1 transition-transform',
            isActive(item.name) ? 'scale-110' : 'scale-100'
          ]"
        />
        <span class="text-xs font-medium">{{ item.label }}</span>

        <!-- Alert badge for alerts tab -->
        <div
          v-if="item.name === 'alerts' && alertStore.criticalCount > 0"
          class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full min-w-5 h-5 flex items-center justify-center px-1"
        >
          {{ alertStore.criticalCount > 99 ? '99+' : alertStore.criticalCount }}
        </div>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAlertStore } from '@/stores/alerts'
import {
  Home,
  AlertTriangle,
  Grid3x3,
  BarChart3
} from 'lucide-vue-next'

const route = useRoute()
const alertStore = useAlertStore()

const navItems = [
  {
    name: 'dashboard',
    to: '/',
    icon: Home,
    label: 'Home'
  },
  {
    name: 'alerts',
    to: '/alerts',
    icon: AlertTriangle,
    label: 'Alert'
  },
  {
    name: 'motors',
    to: '/motors',
    icon: Grid3x3,
    label: 'Motori'
  },
  {
    name: 'statistics',
    to: '/statistics',
    icon: BarChart3,
    label: 'Stats'
  }
]

const isActive = computed(() => (name) => {
  return route.name === name
})

const handleNavClick = (item) => {
  // Add haptic feedback if available
  if (navigator.vibrate) {
    navigator.vibrate(50)
  }

  // Clear alerts badge when clicking alerts
  if (item.name === 'alerts') {
    alertStore.markAllAsRead()
  }
}
</script>

<style scoped>
.router-link-active {
  @apply text-blue-600 bg-blue-50;
}

/* Ensure bottom nav is above all content */
nav {
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}
</style>