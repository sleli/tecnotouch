import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: {
        title: 'Dashboard',
        subtitle: 'Panoramica generale del sistema'
      }
    },
    {
      path: '/motors',
      name: 'motors',
      component: () => import('@/views/MotorsView.vue'),
      meta: {
        title: 'Motori',
        subtitle: 'Gestione e monitoraggio motori'
      }
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('@/views/StatisticsView.vue'),
      meta: {
        title: 'Statistiche',
        subtitle: 'Analisi vendite e performance'
      }
    },
    {
      path: '/alerts',
      name: 'alerts',
      component: () => import('@/views/AlertsView.vue'),
      meta: {
        title: 'Alert',
        subtitle: 'Notifiche e avvisi sistema'
      }
    }
  ]
})

// Update document title on route change
router.afterEach((to) => {
  document.title = to.meta.title
    ? `${to.meta.title} - Distributore Dashboard`
    : 'Distributore Dashboard'
})

export default router