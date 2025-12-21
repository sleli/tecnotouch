<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <div class="mt-1">
          <div
            v-if="loading"
            class="h-8 w-16 bg-gray-200 rounded animate-pulse"
          />
          <p
            v-else
            class="text-2xl font-bold text-gray-900"
          >
            {{ displayValue }}
          </p>
        </div>
        <p v-if="subtitle" class="text-xs text-gray-500 mt-1">{{ subtitle }}</p>
      </div>
      <div
        class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
        :class="iconBgClass"
      >
        <component
          :is="iconComponent"
          class="w-6 h-6"
          :class="iconColorClass"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Grid3x3,
  TrendingUp,
  Euro,
  AlertTriangle,
  BarChart3,
  Download,
  Users,
  Package,
  Clock
} from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    default: '--'
  },
  subtitle: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  icon: {
    type: String,
    default: 'Grid3x3'
  },
  color: {
    type: String,
    default: 'blue'
  }
})

// Icon mapping
const iconMap = {
  Grid3x3,
  TrendingUp,
  Euro,
  AlertTriangle,
  BarChart3,
  Download,
  Users,
  Package,
  Clock
}

// Color classes mapping
const colorClasses = {
  blue: {
    bg: 'bg-blue-50',
    text: 'text-blue-600'
  },
  green: {
    bg: 'bg-green-50',
    text: 'text-green-600'
  },
  emerald: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-600'
  },
  red: {
    bg: 'bg-red-50',
    text: 'text-red-600'
  },
  yellow: {
    bg: 'bg-yellow-50',
    text: 'text-yellow-600'
  },
  purple: {
    bg: 'bg-purple-50',
    text: 'text-purple-600'
  },
  gray: {
    bg: 'bg-gray-50',
    text: 'text-gray-600'
  }
}

// Computed
const iconComponent = computed(() => {
  return iconMap[props.icon] || Grid3x3
})

const iconBgClass = computed(() => {
  return colorClasses[props.color]?.bg || colorClasses.blue.bg
})

const iconColorClass = computed(() => {
  return colorClasses[props.color]?.text || colorClasses.blue.text
})

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return '--'
  return props.value
})
</script>