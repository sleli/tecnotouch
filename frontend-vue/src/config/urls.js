/**
 * Centralized URL Configuration
 * Unico punto per configurare tutti gli URL del sistema
 */

// 🌐 Network Configuration - MODIFY THESE FOR YOUR NETWORK
const NETWORK_CONFIG = {
  // Server IP address on your local network
  SERVER_IP: '192.168.1.18',

  // Vending machine IP (for production)
  VENDING_MACHINE_IP: '192.168.1.65',

  // Ports
  PORTS: {
    FRONTEND_DEV: 3001,
    FRONTEND_PROD: 3000,
    API_SERVER: 8000,
    SIMULATOR: 1500,
    VENDING_MACHINE: 1500
  }
}

/**
 * Detect current environment and return appropriate URLs
 */
function getEnvironmentConfig() {
  const hostname = window.location.hostname
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1'
  const isDevelopment = import.meta.env.DEV

  console.log('🌍 URL Config - Hostname:', hostname, '| Dev:', isDevelopment, '| Localhost:', isLocalhost)

  if (isLocalhost) {
    // Running on development machine
    return {
      API_BASE: `http://localhost:${NETWORK_CONFIG.PORTS.API_SERVER}/api`,
      FRONTEND_BASE: `http://localhost:${isDevelopment ? NETWORK_CONFIG.PORTS.FRONTEND_DEV : NETWORK_CONFIG.PORTS.FRONTEND_PROD}`,
      SIMULATOR_BASE: `http://localhost:${NETWORK_CONFIG.PORTS.SIMULATOR}`,
      VENDING_MACHINE_BASE: `http://${NETWORK_CONFIG.VENDING_MACHINE_IP}:${NETWORK_CONFIG.PORTS.VENDING_MACHINE}`,
      ENV_TYPE: 'development-local'
    }
  } else {
    // Running on network device (smartphone, tablet, etc.)
    return {
      API_BASE: `http://${NETWORK_CONFIG.SERVER_IP}:${NETWORK_CONFIG.PORTS.API_SERVER}/api`,
      FRONTEND_BASE: `http://${NETWORK_CONFIG.SERVER_IP}:${isDevelopment ? NETWORK_CONFIG.PORTS.FRONTEND_DEV : NETWORK_CONFIG.PORTS.FRONTEND_PROD}`,
      SIMULATOR_BASE: `http://${NETWORK_CONFIG.SERVER_IP}:${NETWORK_CONFIG.PORTS.SIMULATOR}`,
      VENDING_MACHINE_BASE: `http://${NETWORK_CONFIG.VENDING_MACHINE_IP}:${NETWORK_CONFIG.PORTS.VENDING_MACHINE}`,
      ENV_TYPE: 'development-network'
    }
  }
}

// Export the configuration
export const URL_CONFIG = getEnvironmentConfig()

// Export individual URLs for convenience
export const API_BASE_URL = URL_CONFIG.API_BASE
export const FRONTEND_BASE_URL = URL_CONFIG.FRONTEND_BASE
export const SIMULATOR_BASE_URL = URL_CONFIG.SIMULATOR_BASE
export const VENDING_MACHINE_BASE_URL = URL_CONFIG.VENDING_MACHINE_BASE

// Log configuration for debugging
console.log('🚀 URL Configuration loaded:', {
  environment: URL_CONFIG.ENV_TYPE,
  apiBase: API_BASE_URL,
  frontendBase: FRONTEND_BASE_URL,
  simulatorBase: SIMULATOR_BASE_URL,
  vendingMachine: VENDING_MACHINE_BASE_URL
})

export default URL_CONFIG