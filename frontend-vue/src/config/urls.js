/**
 * Centralized URL Configuration
 * Reads from environment variables injected at build-time by Vite
 */

// Read from Vite env vars (injected at build time)
const VENDING_IP = import.meta.env.VITE_DISTRIBUTOR_IP
const API_PORT = import.meta.env.VITE_API_PORT || '8000'
const VENDING_PORT = import.meta.env.VITE_VENDING_MACHINE_PORT || '1500'

// Validate required environment variables
if (!VENDING_IP) {
  console.error('❌ Missing required environment variable!')
  console.error('Required: VITE_DISTRIBUTOR_IP')
  console.error('Check frontend-vue/.env.development or .env.production')
}

/**
 * Detect current environment and return appropriate URLs
 * Auto-detects server IP from window.location (no manual config needed!)
 */
function getEnvironmentConfig() {
  const hostname = window.location.hostname
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1'
  const isDevelopment = import.meta.env.DEV

  // Auto-detect server IP from current URL
  const serverHost = hostname

  if (isLocalhost) {
    // Running on development machine (localhost)
    return {
      API_BASE: `http://localhost:${API_PORT}/api`,
      VENDING_MACHINE_BASE: `http://${VENDING_IP}:${VENDING_PORT}`,
      ENV_TYPE: 'development-local'
    }
  } else {
    // Running on network device (smartphone, tablet, etc.)
    // Auto-uses the same IP you used to access the page!
    return {
      API_BASE: `http://${serverHost}:${API_PORT}/api`,
      VENDING_MACHINE_BASE: `http://${VENDING_IP}:${VENDING_PORT}`,
      ENV_TYPE: 'production-network'
    }
  }
}

// Export the configuration
export const URL_CONFIG = getEnvironmentConfig()

// Export individual URLs for convenience
export const API_BASE_URL = URL_CONFIG.API_BASE
export const VENDING_MACHINE_BASE_URL = URL_CONFIG.VENDING_MACHINE_BASE

export default URL_CONFIG