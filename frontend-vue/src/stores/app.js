import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { API_BASE_URL } from '@/config/urls'

export const useAppStore = defineStore('app', () => {
  // State
  const isLoading = ref(false)
  const isOnline = ref(false) // Sistema online solo se API + distributore raggiungibili
  const apiHealthy = ref(false)
  const distributoreHealthy = ref(false)
  const systemStatus = ref({
    api_reachable: false,
    distributore_reachable: false,
    distributore_ip: '',
    api_base_url: '',
    last_check: null
  })
  const lastUpdate = ref(null)
  const lastDownload = ref(null)
  const lastEventDate = ref(null)

  // Use centralized URL configuration
  const apiBase = ref(API_BASE_URL)

  // Getters
  const formattedLastUpdate = computed(() => {
    if (!lastUpdate.value) return 'Mai aggiornato'

    const now = new Date()
    const diff = Math.floor((now - lastUpdate.value) / 1000)

    if (diff < 60) return 'Ora'
    if (diff < 3600) return `${Math.floor(diff / 60)} min fa`
    if (diff < 86400) return `${Math.floor(diff / 3600)} ore fa`
    return lastUpdate.value.toLocaleDateString('it-IT')
  })

  const formattedLastSync = computed(() => {
    if (!lastDownload.value) return 'Nessuna sincronizzazione'

    const now = new Date()
    const lastDownloadDate = new Date(lastDownload.value)
    const diff = Math.floor((now - lastDownloadDate) / 1000)

    if (diff < 60) return 'Ora'
    if (diff < 3600) return `${Math.floor(diff / 60)} min fa`
    if (diff < 86400) return `${Math.floor(diff / 3600)} ore fa`
    return lastDownloadDate.toLocaleDateString('it-IT')
  })

  const formattedLastEventDate = computed(() => {
    if (!lastEventDate.value) return 'Nessun evento'

    const now = new Date()
    const lastEventDateTime = new Date(lastEventDate.value)
    const diff = Math.floor((now - lastEventDateTime) / 1000)

    if (diff < 60) return 'Ora'
    if (diff < 3600) return `${Math.floor(diff / 60)} min fa`
    if (diff < 86400) return `${Math.floor(diff / 3600)} ore fa`
    return lastEventDateTime.toLocaleDateString('it-IT')
  })

  // Actions
  const setLoading = (loading) => {
    isLoading.value = loading
  }

  const updateLastUpdate = () => {
    lastUpdate.value = new Date()
  }

  const updateLastDownload = (timestamp) => {
    lastDownload.value = timestamp
  }

  const updateLastEventDate = (timestamp) => {
    lastEventDate.value = timestamp
  }

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${apiBase.value}/health`)
      if (response.ok) {
        const data = await response.json()

        // Aggiorna stato sistema
        apiHealthy.value = data.api_reachable || false
        distributoreHealthy.value = data.distributore_reachable || false
        systemStatus.value = {
          api_reachable: data.api_reachable || false,
          distributore_reachable: data.distributore_reachable || false,
          distributore_ip: data.distributore_ip || '',
          api_base_url: data.api_base_url || apiBase.value,
          last_check: new Date().toISOString()
        }

        // Sistema online solo se entrambi raggiungibili
        isOnline.value = apiHealthy.value && distributoreHealthy.value

        return true
      } else {
        throw new Error('API non raggiungibile')
      }
    } catch (error) {
      apiHealthy.value = false
      distributoreHealthy.value = false
      isOnline.value = false
      systemStatus.value = {
        api_reachable: false,
        distributore_reachable: false,
        distributore_ip: 'N/A',
        api_base_url: 'N/A',
        last_check: new Date().toISOString()
      }
      return false
    }
  }

  const setOnlineStatus = (online) => {
    isOnline.value = online
  }

  const refreshApiUrl = () => {
    // Re-import to get fresh URL configuration
    import('@/config/urls').then(({ API_BASE_URL }) => {
      apiBase.value = API_BASE_URL
    })
  }

  const init = () => {
    // Set initial last update
    updateLastUpdate()

    // Check iniziale
    checkApiHealth()

    // Auto-update every 30 seconds
    setInterval(updateLastUpdate, 30 * 1000)

    // Check health ogni 30 secondi
    setInterval(checkApiHealth, 30 * 1000)
  }

  return {
    // State
    isLoading,
    isOnline,
    apiHealthy,
    distributoreHealthy,
    systemStatus,
    lastUpdate,
    lastDownload,
    lastEventDate,
    apiBase,

    // Getters
    formattedLastUpdate,
    formattedLastSync,
    formattedLastEventDate,

    // Actions
    setLoading,
    updateLastUpdate,
    updateLastDownload,
    updateLastEventDate,
    checkApiHealth,
    setOnlineStatus,
    refreshApiUrl,
    init
  }
})