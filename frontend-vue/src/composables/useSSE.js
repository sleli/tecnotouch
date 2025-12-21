import { ref, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'

export function useSSE() {
  const appStore = useAppStore()
  const isConnected = ref(false)
  const error = ref(null)
  let eventSource = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 5
  const reconnectDelay = 5000

  // Handlers per diversi tipi di eventi
  const eventHandlers = ref({
    connected: [],
    download_started: [],
    download_progress: [],
    download_completed: [],
    download_error: [],
    heartbeat: []
  })

  const connect = () => {
    if (eventSource) {
      return // Già connesso
    }

    try {
      const url = `${appStore.apiBase}/events`
      console.log('🔄 Connecting to SSE:', url)

      eventSource = new EventSource(url)

      eventSource.onopen = () => {
        console.log('✅ SSE Connected')
        isConnected.value = true
        error.value = null
        reconnectAttempts = 0 // Reset counter su connessione riuscita
      }

      eventSource.onerror = (event) => {
        console.error('❌ SSE Error:', event)
        isConnected.value = false
        error.value = 'Errore di connessione SSE'

        // Riconnessione automatica con limite
        if (reconnectAttempts < maxReconnectAttempts) {
          reconnectAttempts++
          setTimeout(() => {
            if (!isConnected.value && reconnectAttempts <= maxReconnectAttempts) {
              console.log(`🔄 Attempting SSE reconnection... (${reconnectAttempts}/${maxReconnectAttempts})`)
              disconnect()
              connect()
            }
          }, reconnectDelay)
        } else {
          console.error(`❌ SSE Max reconnection attempts (${maxReconnectAttempts}) reached. Stopping reconnection.`)
          error.value = 'Connessione SSE non disponibile'
        }
      }

      // Handler per eventi specifici
      eventSource.addEventListener('connected', (event) => {
        const data = JSON.parse(event.data)
        console.log('📡 SSE Event - Connected:', data)
        executeHandlers('connected', data)
      })

      eventSource.addEventListener('download_started', (event) => {
        const data = JSON.parse(event.data)
        console.log('📡 SSE Event - Download Started:', data)
        executeHandlers('download_started', data)
      })

      eventSource.addEventListener('download_progress', (event) => {
        const data = JSON.parse(event.data)
        console.log('📡 SSE Event - Download Progress:', data)
        executeHandlers('download_progress', data)
      })

      eventSource.addEventListener('download_completed', (event) => {
        const data = JSON.parse(event.data)
        console.log('📡 SSE Event - Download Completed:', data)
        executeHandlers('download_completed', data)
      })

      eventSource.addEventListener('download_error', (event) => {
        const data = JSON.parse(event.data)
        console.log('📡 SSE Event - Download Error:', data)
        executeHandlers('download_error', data)
      })

      eventSource.addEventListener('heartbeat', (event) => {
        const data = JSON.parse(event.data)
        // Non loggare heartbeat per evitare spam
        executeHandlers('heartbeat', data)
      })

    } catch (err) {
      console.error('❌ Failed to create SSE connection:', err)
      error.value = err.message
    }
  }

  const disconnect = () => {
    if (eventSource) {
      console.log('🛑 Disconnecting SSE')
      eventSource.close()
      eventSource = null
      isConnected.value = false
    }
  }

  const resetReconnectAttempts = () => {
    reconnectAttempts = 0
    error.value = null
  }

  const executeHandlers = (eventType, data) => {
    const handlers = eventHandlers.value[eventType]
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (err) {
          console.error(`❌ Error in SSE handler for ${eventType}:`, err)
        }
      })
    }
  }

  // Metodi per registrare handlers
  const onConnected = (handler) => {
    eventHandlers.value.connected.push(handler)
  }

  const onDownloadStarted = (handler) => {
    eventHandlers.value.download_started.push(handler)
  }

  const onDownloadProgress = (handler) => {
    eventHandlers.value.download_progress.push(handler)
  }

  const onDownloadCompleted = (handler) => {
    eventHandlers.value.download_completed.push(handler)
  }

  const onDownloadError = (handler) => {
    eventHandlers.value.download_error.push(handler)
  }

  const onHeartbeat = (handler) => {
    eventHandlers.value.heartbeat.push(handler)
  }

  // Cleanup automatico
  onUnmounted(() => {
    disconnect()
  })

  return {
    // Stato
    isConnected,
    error,

    // Metodi di controllo
    connect,
    disconnect,
    resetReconnectAttempts,

    // Registrazione handlers
    onConnected,
    onDownloadStarted,
    onDownloadProgress,
    onDownloadCompleted,
    onDownloadError,
    onHeartbeat
  }
}