// Service Worker for PWA functionality
import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { NetworkFirst, CacheFirst, StaleWhileRevalidate } from 'workbox-strategies'
import { ExpirationPlugin } from 'workbox-expiration'

// Precache all build assets
precacheAndRoute(self.__WB_MANIFEST)

// Clean up old caches
cleanupOutdatedCaches()

// API caching strategy - Network first with cache fallback
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-cache',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 50,
        maxAgeSeconds: 60 * 60, // 1 hour
      }),
    ],
  })
)

// Image caching strategy - Cache first
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images-cache',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
      }),
    ],
  })
)

// Font caching strategy - Cache first
registerRoute(
  ({ request }) => request.destination === 'font',
  new CacheFirst({
    cacheName: 'fonts-cache',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 30,
        maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
      }),
    ],
  })
)

// CSS and JS caching - Stale while revalidate
registerRoute(
  ({ request }) =>
    request.destination === 'style' ||
    request.destination === 'script',
  new StaleWhileRevalidate({
    cacheName: 'assets-cache',
  })
)

// Background sync for offline actions
const BACKGROUND_SYNC_TAG = 'background-sync'
const MOTOR_ACTIONS_STORE = 'motor-actions'

// Handle background sync
self.addEventListener('sync', event => {
  console.log('[SW] Background sync event:', event.tag)

  if (event.tag === BACKGROUND_SYNC_TAG) {
    event.waitUntil(syncPendingActions())
  }
})

// Sync pending actions when back online
async function syncPendingActions() {
  try {
    const db = await openDatabase()
    const tx = db.transaction([MOTOR_ACTIONS_STORE], 'readwrite')
    const store = tx.objectStore(MOTOR_ACTIONS_STORE)

    const actions = await getAllActions(store)

    for (const action of actions) {
      try {
        await syncAction(action)
        await deleteAction(store, action.id)
        console.log('[SW] Synced action:', action)
      } catch (error) {
        console.error('[SW] Failed to sync action:', action, error)
      }
    }

    await tx.complete
  } catch (error) {
    console.error('[SW] Background sync failed:', error)
  }
}

// Database operations
function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('VendingDashboard', 1)

    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)

    request.onupgradeneeded = event => {
      const db = event.target.result

      if (!db.objectStoreNames.contains(MOTOR_ACTIONS_STORE)) {
        const store = db.createObjectStore(MOTOR_ACTIONS_STORE, {
          keyPath: 'id',
          autoIncrement: true
        })
        store.createIndex('timestamp', 'timestamp', { unique: false })
      }
    }
  })
}

function getAllActions(store) {
  return new Promise((resolve, reject) => {
    const request = store.getAll()
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
  })
}

function deleteAction(store, id) {
  return new Promise((resolve, reject) => {
    const request = store.delete(id)
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve()
  })
}

async function syncAction(action) {
  const response = await fetch(action.url, {
    method: action.method || 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(action.data)
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return response.json()
}

// Push notification handling
self.addEventListener('push', event => {
  console.log('[SW] Push event received:', event)

  if (!event.data) {
    return
  }

  const data = event.data.json()
  const title = data.title || 'Distributore Dashboard'
  const options = {
    body: data.body || '',
    icon: data.icon || '/icon-192.png',
    badge: '/icon-192.png',
    tag: data.tag || 'default',
    data: data.data || {},
    actions: data.actions || [],
    requireInteraction: data.requireInteraction || false,
    silent: data.silent || false,
    ...data.options
  }

  event.waitUntil(
    self.registration.showNotification(title, options)
  )
})

// Notification click handling
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification click:', event)

  event.notification.close()

  const action = event.action
  const data = event.notification.data || {}

  event.waitUntil(
    (async () => {
      const clients = await self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true
      })

      // If we have an open window, focus it
      if (clients.length > 0) {
        const client = clients[0]
        client.focus()

        // Send message to client with action data
        client.postMessage({
          type: 'notification-click',
          action,
          data
        })

        return
      }

      // Otherwise open a new window
      let url = '/'

      // Handle specific notification actions
      if (data.motorId) {
        url = `/motors?highlight=${data.motorId}`
      } else if (data.url) {
        url = data.url
      }

      await self.clients.openWindow(url)
    })()
  )
})

// Message handling from main thread
self.addEventListener('message', event => {
  console.log('[SW] Message received:', event.data)

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
    return
  }

  // Handle offline action queueing
  if (event.data && event.data.type === 'QUEUE_ACTION') {
    event.waitUntil(queueAction(event.data.payload))
  }
})

// Queue action for background sync
async function queueAction(action) {
  try {
    const db = await openDatabase()
    const tx = db.transaction([MOTOR_ACTIONS_STORE], 'readwrite')
    const store = tx.objectStore(MOTOR_ACTIONS_STORE)

    const actionWithTimestamp = {
      ...action,
      timestamp: Date.now()
    }

    await addAction(store, actionWithTimestamp)
    await tx.complete

    // Register for background sync
    await self.registration.sync.register(BACKGROUND_SYNC_TAG)

    console.log('[SW] Action queued for sync:', actionWithTimestamp)
  } catch (error) {
    console.error('[SW] Failed to queue action:', error)
  }
}

function addAction(store, action) {
  return new Promise((resolve, reject) => {
    const request = store.add(action)
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
  })
}

// Periodic background sync for checking updates
self.addEventListener('periodicsync', event => {
  if (event.tag === 'check-updates') {
    event.waitUntil(checkForUpdates())
  }
})

async function checkForUpdates() {
  try {
    // Check for system updates
    console.log('[SW] Checking for updates...')
  } catch (error) {
    console.error('[SW] Failed to check for updates:', error)
  }
}

console.log('[SW] Service Worker loaded and ready')