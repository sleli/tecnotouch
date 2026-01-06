import { Workbox } from 'workbox-window'

let wb = null
let registration = null

export const registerSW = async () => {
  if (!('serviceWorker' in navigator)) {
    console.log('Service Worker not supported')
    return
  }

  try {
    // Create workbox instance
    wb = new Workbox('/sw.js')

    // Add event listeners
    wb.addEventListener('waiting', () => {
      console.log('New service worker is waiting')
      showUpdateAvailable()
    })

    wb.addEventListener('controlling', () => {
      console.log('New service worker is now controlling')
      window.location.reload()
    })

    wb.addEventListener('activated', (event) => {
      console.log('Service worker activated')
      if (event.isUpdate) {
        console.log('Service worker updated')
        if (window.$toast) {
          window.$toast.success('App aggiornata!', {
            duration: 3000
          })
        }
      }
    })

    // Register service worker
    registration = await wb.register()

    return registration
  } catch (error) {
    console.error('Service worker registration failed:', error)
    return null
  }
}

const showUpdateAvailable = () => {
  if (window.$toast) {
    window.$toast.info('Nuova versione disponibile', {
      title: 'Aggiornamento',
      duration: 0, // Don't auto-dismiss
      actions: [
        {
          text: 'Aggiorna',
          handler: () => {
            if (wb) {
              wb.messageSkipWaiting()
            }
          }
        },
        {
          text: 'Dopo',
          handler: () => {}
        }
      ]
    })
  }
}

export const unregisterSW = async () => {
  if (registration) {
    await registration.unregister()
    console.log('Service worker unregistered')
  }
}

// Check for app updates periodically
export const checkForUpdates = async () => {
  if (wb) {
    await wb.update()
  }
}

// PWA Install prompt
let deferredPrompt = null

export const initInstallPrompt = () => {
  window.addEventListener('beforeinstallprompt', (e) => {
    console.log('Install prompt available')
    e.preventDefault()
    deferredPrompt = e
    showInstallBanner()
  })

  window.addEventListener('appinstalled', () => {
    console.log('PWA was installed')
    deferredPrompt = null

    if (window.$toast) {
      window.$toast.success('App installata!', {
        title: 'Installazione completata'
      })
    }
  })
}

const showInstallBanner = () => {
  // Show install banner after 30 seconds
  setTimeout(() => {
    if (deferredPrompt && !window.matchMedia('(display-mode: standalone)').matches) {
      if (window.$toast) {
        window.$toast.info('Installa l\'app per un\'esperienza migliore', {
          title: 'Distributore Dashboard',
          duration: 8000,
          actions: [
            {
              text: 'Installa',
              handler: installPWA
            },
            {
              text: 'Non ora',
              handler: () => {}
            }
          ]
        })
      }
    }
  }, 30000)
}

export const installPWA = async () => {
  if (!deferredPrompt) {
    console.log('Install prompt not available')
    return false
  }

  try {
    deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice

    console.log(`User response to install prompt: ${outcome}`)

    if (outcome === 'accepted') {
      console.log('User accepted the install prompt')
    } else {
      console.log('User dismissed the install prompt')
    }

    deferredPrompt = null
    return outcome === 'accepted'
  } catch (error) {
    console.error('Install prompt failed:', error)
    return false
  }
}

// Push notifications
export const requestNotificationPermission = async () => {
  if (!('Notification' in window)) {
    console.log('This browser does not support notifications')
    return 'not-supported'
  }

  if (Notification.permission === 'granted') {
    return 'granted'
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission()
    return permission
  }

  return Notification.permission
}

export const showNotification = (title, options = {}) => {
  if (Notification.permission === 'granted') {
    const defaultOptions = {
      icon: '/icon-192.png',
      badge: '/icon-192.png',
      tag: 'vending-dashboard',
      renotify: false,
      requireInteraction: false,
      ...options
    }

    try {
      return new Notification(title, defaultOptions)
    } catch (error) {
      console.error('Failed to show notification:', error)
      return null
    }
  } else {
    console.log('Notification permission not granted')
    return null
  }
}

// Network status monitoring
export const initNetworkMonitoring = () => {
  const updateNetworkStatus = () => {
    const isOnline = navigator.onLine

    // Dispatch custom event
    window.dispatchEvent(new CustomEvent('network-status-changed', {
      detail: { isOnline }
    }))

    // Show toast notification
    if (window.$toast) {
      if (isOnline) {
        window.$toast.success('Connessione ripristinata', {
          duration: 3000
        })
      } else {
        window.$toast.warning('Modalità offline', {
          title: 'Nessuna connessione',
          duration: 5000
        })
      }
    }
  }

  window.addEventListener('online', updateNetworkStatus)
  window.addEventListener('offline', updateNetworkStatus)

  return () => {
    window.removeEventListener('online', updateNetworkStatus)
    window.removeEventListener('offline', updateNetworkStatus)
  }
}

// Check if app is running in standalone mode (installed PWA)
export const isStandalone = () => {
  return window.matchMedia('(display-mode: standalone)').matches ||
         window.navigator.standalone === true
}

// Get app info
export const getAppInfo = () => {
  return {
    isStandalone: isStandalone(),
    isServiceWorkerSupported: 'serviceWorker' in navigator,
    isNotificationSupported: 'Notification' in window,
    isPushSupported: 'PushManager' in window,
    isOnline: navigator.onLine,
    userAgent: navigator.userAgent,
    platform: navigator.platform
  }
}