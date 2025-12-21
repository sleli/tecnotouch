<template>
  <div
    class="motor-card touch-feedback"
    @click.prevent="handleCardClick"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
  >
    <!-- Header: Motor ID + Status indicator -->
    <div class="motor-header">
      <div class="motor-id">{{ motor.id || 'M?' }}</div>
      <div class="status-indicator" :class="getStatusClass(motor)"></div>
    </div>

    <!-- Primary: Product name (full) -->
    <div
      v-if="motor.product"
      class="motor-product"
      :title="motor.product"
    >
      {{ truncateProduct(motor.product) }}
    </div>

    <!-- Secondary: Sales count -->
    <div class="motor-sales">
      <span v-if="motor.totalSales !== undefined">
        {{ motor.totalSales }} vendite
      </span>
      <span v-else>
        N/A
      </span>
    </div>

    <!-- Footer: Price + Last sale -->
    <div class="motor-footer">
      <div v-if="motor.price" class="motor-price">
        €{{ formatPrice(motor.price) }}
      </div>
      <div
        v-if="motor.lastSaleDateTime"
        class="motor-last-sale"
        :title="`Ultima vendita: ${formatLastSale(motor.lastSaleDateTime)}`"
      >
        {{ getLastSaleText(motor.lastSaleDateTime) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, defineProps, computed, onMounted } from 'vue'
import { useAnalyticsStore } from '../stores/analytics'
import { useMotorAnalytics } from '../composables/useMotorAnalytics'

const emit = defineEmits(['click', 'long-press'])

const props = defineProps({
  motor: {
    type: Object,
    required: true
  }
})

// Analytics integration
const analyticsStore = useAnalyticsStore()
const { fetchAllStatus } = useMotorAnalytics()

// Load status data on mount if not cached
onMounted(() => {
  if (!analyticsStore.isStatusCacheValid()) {
    fetchAllStatus()
  }
})

// Touch handling for long press and scroll detection
let touchStartTime = 0
let touchStartY = 0
let longPressTimer = null
let hasMoved = false

const handleTouchStart = (e) => {
  touchStartTime = Date.now()
  touchStartY = e.touches[0].clientY
  hasMoved = false

  // Start long press timer
  longPressTimer = setTimeout(() => {
    if (!hasMoved && navigator.vibrate) {
      navigator.vibrate([50, 50, 50])
    }
    if (!hasMoved) {
      emit('long-press', props.motor)
    }
  }, 500) // 500ms for long press
}

const handleTouchMove = (e) => {
  if (!touchStartY) return

  const currentY = e.touches[0].clientY
  const deltaY = Math.abs(currentY - touchStartY)

  // If user moves more than 10px, consider it a scroll
  if (deltaY > 10) {
    hasMoved = true
    // Clear long press timer on scroll
    if (longPressTimer) {
      clearTimeout(longPressTimer)
      longPressTimer = null
    }
  }
}

const handleTouchEnd = (e) => {
  const touchDuration = Date.now() - touchStartTime

  // Clear long press timer
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }

  // Only emit click if it was a short tap AND user didn't scroll
  if (touchDuration < 500 && !hasMoved) {
    // Prevent the default click event and manually emit
    e.preventDefault()
    emit('click', props.motor)
  }

  // Reset tracking variables
  hasMoved = false
  touchStartY = 0
}

// Utility methods
const truncateProduct = (product) => {
  if (!product) return ''
  // Allow full product names on mobile with wrapping instead of truncation
  const isMobile = window.innerWidth <= 640
  if (isMobile) {
    // On mobile, don't truncate - let it wrap to multiple lines
    return product
  }
  // On desktop, keep some truncation if needed
  const maxLength = 16
  return product.length > maxLength ? product.substring(0, maxLength) + '...' : product
}

const formatPrice = (price) => {
  if (typeof price === 'number') {
    return price.toFixed(2)
  }
  return String(price || '0.00')
}

const formatLastSale = (lastSale) => {
  if (!lastSale) return 'N/A'

  const date = new Date(lastSale)
  if (isNaN(date.getTime())) return 'N/A'

  return date.toLocaleDateString('it-IT', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getLastSaleText = (lastSale) => {
  if (!lastSale) return ''

  const now = new Date()
  const saleDate = new Date(lastSale)

  if (isNaN(saleDate.getTime())) return ''

  const diffHours = Math.floor((now - saleDate) / (1000 * 60 * 60))

  if (diffHours < 1) return 'Ora'
  if (diffHours < 24) return `${diffHours}h`
  if (diffHours < 48) return 'Ieri'

  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}g`
}

// Handle non-touch clicks (desktop)
const handleCardClick = () => {
  emit('click', props.motor)
}

// Status indicator based on analytics engine
const getStatusClass = (motor) => {
  // Get analytics status if available
  const analyticsStatus = analyticsStore.getMotorStatus(motor.id)

  if (analyticsStatus) {
    switch (analyticsStatus) {
      case 'red': return 'status-overdue'
      case 'green': return 'status-normal'
      case 'neutral': return 'status-neutral'
      default: return 'status-neutral'
    }
  }

  // Fallback to legacy logic if analytics not loaded
  if (!motor.lastSaleDateTime) return 'status-neutral'

  const now = new Date()
  const saleDate = new Date(motor.lastSaleDateTime)

  if (isNaN(saleDate.getTime())) return 'status-neutral'

  const diffHours = Math.floor((now - saleDate) / (1000 * 60 * 60))

  if (diffHours < 24) return 'status-normal' // Sold in last 24h
  if (diffHours < 72) return 'status-normal' // Sold in last 3 days
  return 'status-overdue' // Older sales (might be overdue)
}
</script>

<style scoped>
.motor-card {
  @apply relative border-2 rounded-xl p-3 text-center cursor-pointer transition-all duration-200 flex flex-col justify-between items-center;
  /* Fixed heights instead of aspect-ratio to prevent overlap */
  height: 120px; /* Fixed height for desktop */
  min-height: 120px;
}

@media (max-width: 640px) {
  .motor-card {
    height: 140px; /* Taller fixed height for mobile */
    min-height: 140px;
  }
}

@media (max-width: 480px) {
  .motor-card {
    height: 150px; /* Even taller for very small screens */
    min-height: 150px;
  }
}

/* Disable hover effects on touch devices to prevent interference */
@media (hover: hover) {
  .motor-card:hover {
    @apply -translate-y-1 shadow-lg;
  }
}

.motor-card:active {
  @apply scale-95 shadow-md;
  transition: transform 0.1s ease;
}

/* Default motor card styling */
.motor-card {
  @apply border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100;
}

.motor-card:hover {
  @apply border-blue-300 bg-gradient-to-br from-blue-100 to-blue-200;
}

/* Layout elements */
.motor-header {
  @apply flex justify-between items-center mb-2 w-full;
}

.motor-footer {
  @apply flex justify-between items-center w-full mt-auto text-xs;
}

/* Text elements */
.motor-id {
  @apply font-bold text-sm text-gray-900;
}

.motor-product {
  @apply text-sm text-gray-800 font-semibold mb-1 leading-tight flex-grow;
  /* Allow text wrapping for full product names */
  word-wrap: break-word;
  hyphens: auto;
  line-height: 1.3;
  text-align: center;
}

.motor-sales {
  @apply text-xs text-gray-600 font-medium mb-2 text-center;
}

.motor-price {
  @apply text-xs text-gray-600 font-bold;
}

.motor-last-sale {
  @apply text-xs text-gray-500;
}

/* Status indicators - Analytics powered */
.status-indicator {
  @apply w-3 h-3 rounded-full border border-white shadow-sm;
}

.status-normal {
  @apply bg-green-500; /* Normal sales pattern */
}

.status-overdue {
  @apply bg-red-500; /* Overdue for sale */
}

.status-neutral {
  @apply bg-gray-400; /* Insufficient data */
}

/* Legacy status classes for fallback */
.status-active {
  @apply bg-green-500; /* Sold in last 24h */
}

.status-recent {
  @apply bg-yellow-500; /* Sold in last 3 days */
}

.status-old {
  @apply bg-gray-400; /* Older sales */
}

.status-inactive {
  @apply bg-red-400; /* No sales data */
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .motor-card {
    @apply p-3 min-h-28; /* More height for rectangular cards */
  }

  .motor-header {
    @apply mb-1;
  }

  .motor-id {
    @apply text-sm font-bold; /* Slightly larger for better visibility */
  }

  .motor-product {
    @apply text-sm mb-2 font-semibold leading-tight;
    /* Allow 2-3 lines for product names */
    max-height: 3rem; /* ~3 lines */
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
  }

  .motor-sales {
    @apply text-xs leading-tight text-gray-600 mb-2;
  }

  .motor-footer {
    @apply mt-auto;
  }

  .motor-price {
    @apply text-xs font-bold;
  }

  .motor-last-sale {
    @apply text-xs;
  }

  .status-indicator {
    @apply w-3 h-3; /* Slightly larger on mobile */
  }
}

/* Very small screens */
@media (max-width: 480px) {
  .motor-card {
    @apply p-2.5 min-h-32; /* Even more height for very small screens */
  }

  .motor-product {
    @apply text-sm font-semibold leading-tight mb-2;
    /* Allow full product names with better line height */
    max-height: 3.5rem; /* ~3-4 lines */
    -webkit-line-clamp: 4;
  }

  .motor-sales {
    @apply text-xs leading-tight mb-2;
  }

  .motor-footer {
    @apply text-xs;
  }

  .motor-price {
    @apply font-bold;
  }

  .motor-last-sale {
    @apply leading-tight;
    /* Keep last sale visible but compact */
  }
}
</style>