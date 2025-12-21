<template>
  <div class="chart-container">
    <div v-if="loading" class="flex items-center justify-center h-full">
      <div class="loading-spinner mr-2"></div>
      <span class="text-gray-500">Caricamento...</span>
    </div>
    <canvas
      v-else
      ref="chartRef"
      class="w-full h-full"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const chartRef = ref(null)
let chartInstance = null

const createChart = async () => {
  if (!chartRef.value || !props.data.length) return

  // Destroy existing chart
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartRef.value.getContext('2d')

  // Prepare data
  const labels = props.data.map(item => item.method)
  const amounts = props.data.map(item => item.amount)

  // Colors for different payment methods
  const colors = [
    {
      background: 'rgba(34, 197, 94, 0.8)',
      border: '#22c55e'
    },
    {
      background: 'rgba(59, 130, 246, 0.8)',
      border: '#3b82f6'
    },
    {
      background: 'rgba(168, 85, 247, 0.8)',
      border: '#a855f7'
    }
  ]

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: amounts,
        backgroundColor: colors.map(c => c.background),
        borderColor: colors.map(c => c.border),
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          cornerRadius: 8,
          padding: 12,
          displayColors: false,
          callbacks: {
            label: (context) => {
              const value = context.parsed.y
              return `€${value.toFixed(2)}`
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          border: {
            display: false
          },
          ticks: {
            color: '#6b7280',
            font: {
              size: 12
            }
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(107, 114, 128, 0.1)',
            drawBorder: false
          },
          border: {
            display: false
          },
          ticks: {
            color: '#6b7280',
            font: {
              size: 12
            },
            callback: (value) => `€${value}`
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  })
}

// Watch for data changes
watch(() => props.data, async () => {
  await nextTick()
  createChart()
}, { deep: true })

watch(() => props.loading, async (loading) => {
  if (!loading) {
    await nextTick()
    createChart()
  }
})

onMounted(async () => {
  await nextTick()
  if (!props.loading && props.data.length) {
    createChart()
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<style scoped>
.chart-container {
  @apply w-full h-full relative;
}

.loading-spinner {
  @apply w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin;
}
</style>