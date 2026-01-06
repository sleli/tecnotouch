import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAlertStore = defineStore('alerts', () => {
  // State
  const alerts = ref([])
  const unreadCount = ref(0)

  // Getters
  const criticalCount = computed(() => {
    return alerts.value.filter(alert =>
      alert.level === 'critical' && !alert.read
    ).length
  })

  const sortedAlerts = computed(() => {
    return [...alerts.value].sort((a, b) => {
      // Sort by: unread first, then by level (critical > warning > info), then by timestamp
      if (a.read !== b.read) return a.read ? 1 : -1

      const levelOrder = { critical: 0, warning: 1, info: 2 }
      if (levelOrder[a.level] !== levelOrder[b.level]) {
        return levelOrder[a.level] - levelOrder[b.level]
      }

      return new Date(b.timestamp) - new Date(a.timestamp)
    })
  })

  // Actions
  const addAlert = (alert) => {
    const newAlert = {
      id: Date.now() + Math.random(),
      timestamp: new Date(),
      read: false,
      ...alert
    }

    alerts.value.unshift(newAlert)

    if (!newAlert.read) {
      unreadCount.value++
    }

    // Send browser notification if critical
    if (alert.level === 'critical' && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(alert.title, {
          body: alert.message,
          icon: '/icon-192.png',
          tag: `alert-${newAlert.id}`,
          requireInteraction: true
        })
      }
    }

    return newAlert.id
  }

  const markAsRead = (alertId) => {
    const alert = alerts.value.find(a => a.id === alertId)
    if (alert && !alert.read) {
      alert.read = true
      unreadCount.value--
    }
  }

  const markAllAsRead = () => {
    alerts.value.forEach(alert => {
      if (!alert.read) {
        alert.read = true
      }
    })
    unreadCount.value = 0
  }

  const removeAlert = (alertId) => {
    const index = alerts.value.findIndex(a => a.id === alertId)
    if (index > -1) {
      const alert = alerts.value[index]
      if (!alert.read) {
        unreadCount.value--
      }
      alerts.value.splice(index, 1)
    }
  }

  const clearOldAlerts = (olderThanHours = 24) => {
    const cutoff = new Date(Date.now() - olderThanHours * 60 * 60 * 1000)
    const oldAlerts = alerts.value.filter(alert =>
      new Date(alert.timestamp) < cutoff && alert.read
    )

    oldAlerts.forEach(alert => removeAlert(alert.id))
  }

  const clearAllAlerts = () => {
    alerts.value = []
    unreadCount.value = 0
  }

  return {
    // State
    alerts,
    unreadCount,

    // Getters
    criticalCount,
    sortedAlerts,

    // Actions
    addAlert,
    markAsRead,
    markAllAsRead,
    removeAlert,
    clearOldAlerts,
    clearAllAlerts
  }
})