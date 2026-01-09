<template>
  <div class="relative" ref="containerRef">
    <!-- Input Display -->
    <div
      ref="inputRef"
      @click="toggleCalendar"
      class="flex items-center justify-between w-full px-3 py-2 border rounded-lg cursor-pointer transition-all duration-200"
      :class="[
        isOpen
          ? 'border-[#F25A23] ring-2 ring-[#F25A23]/20'
          : 'border-gray-300 hover:border-gray-400',
        error ? 'border-red-500' : '',
      ]"
    >
      <div class="flex items-center gap-2">
        <Calendar class="w-4 h-4 text-gray-400" />
        <span :class="modelValue ? 'text-gray-900' : 'text-gray-400'">
          {{ displayValue }}
        </span>
      </div>
      <ChevronDown
        class="w-4 h-4 text-gray-400 transition-transform duration-200"
        :class="{ 'rotate-180': isOpen }"
      />
    </div>

    <!-- Calendar Dropdown - NO Teleport, stay inside container -->
    <div
      v-show="isOpen"
      ref="dropdownRef"
      class="absolute left-0 mt-1 w-72 bg-white rounded-xl shadow-xl border border-gray-200 p-4"
      style="z-index: 999999"
    >
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <button
          type="button"
          @click.prevent.stop="prevMonth"
          class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ChevronLeft class="w-5 h-5 text-gray-600" />
        </button>
        <span class="font-semibold text-gray-900">
          {{ currentMonthYear }}
        </span>
        <button
          type="button"
          @click.prevent.stop="nextMonth"
          class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ChevronRight class="w-5 h-5 text-gray-600" />
        </button>
      </div>

      <!-- Weekday Headers -->
      <div class="grid grid-cols-7 gap-1 mb-2">
        <div
          v-for="day in weekDays"
          :key="day"
          class="text-center text-xs font-medium text-gray-500 py-1"
        >
          {{ day }}
        </div>
      </div>

      <!-- Days Grid -->
      <div class="grid grid-cols-7 gap-1">
        <button
          v-for="(day, index) in calendarDays"
          :key="index"
          type="button"
          @click.prevent.stop="selectDate(day)"
          :disabled="!day.isCurrentMonth || day.isPast"
          class="relative p-2 text-sm rounded-lg transition-all duration-150"
          :class="getDayClasses(day)"
        >
          {{ day.date }}
        </button>
      </div>

      <!-- Footer -->
      <div
        class="flex items-center justify-between mt-4 pt-3 border-t border-gray-100"
      >
        <button
          type="button"
          @click.prevent.stop="selectToday"
          :disabled="isTodayPast"
          class="text-sm text-[#F25A23] hover:text-[#d94d1a] font-medium disabled:text-gray-300 disabled:cursor-not-allowed"
        >
          Hôm nay
        </button>
        <button
          type="button"
          @click.prevent.stop="clearDate"
          class="text-sm text-gray-500 hover:text-gray-700"
        >
          Xóa
        </button>
      </div>
    </div>

    <!-- Error Message -->
    <p v-if="error" class="mt-1 text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/vi'
import {
  Calendar,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
} from 'lucide-vue-next'

// Set dayjs locale to Vietnamese
dayjs.locale('vi')

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Chọn ngày',
  },
  minDate: {
    type: String,
    default: '',
  },
  futureOnly: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const currentMonth = ref(dayjs())
const containerRef = ref(null)
const inputRef = ref(null)
const dropdownRef = ref(null)

const weekDays = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

const displayValue = computed(() => {
  if (!props.modelValue) return props.placeholder
  return dayjs(props.modelValue).format('DD/MM/YYYY')
})

const currentMonthYear = computed(() => {
  return currentMonth.value.format('MMMM YYYY')
})

const today = computed(() => dayjs().startOf('day'))

const isTodayPast = computed(() => {
  if (!props.futureOnly) return false
  return today.value.isBefore(dayjs().startOf('day'))
})

const calendarDays = computed(() => {
  const startOfMonth = currentMonth.value.startOf('month')
  const endOfMonth = currentMonth.value.endOf('month')
  const startDay = startOfMonth.day()
  const daysInMonth = endOfMonth.date()

  const days = []

  // Previous month days
  const prevMonthObj = currentMonth.value.subtract(1, 'month')
  const daysInPrevMonth = prevMonthObj.daysInMonth()
  for (let i = startDay - 1; i >= 0; i--) {
    const date = daysInPrevMonth - i
    days.push({
      date,
      fullDate: prevMonthObj.date(date).format('YYYY-MM-DD'),
      isCurrentMonth: false,
      isPast: true,
    })
  }

  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    const fullDate = currentMonth.value.date(i).format('YYYY-MM-DD')
    const dateObj = dayjs(fullDate)
    let isPast = false

    if (props.futureOnly) {
      isPast = dateObj.isBefore(today.value)
    }
    if (props.minDate) {
      isPast = isPast || dateObj.isBefore(dayjs(props.minDate))
    }

    days.push({
      date: i,
      fullDate,
      isCurrentMonth: true,
      isPast,
      isToday: dateObj.isSame(today.value, 'day'),
      isSelected: props.modelValue === fullDate,
    })
  }

  // Next month days
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const nextMonthObj = currentMonth.value.add(1, 'month')
    days.push({
      date: i,
      fullDate: nextMonthObj.date(i).format('YYYY-MM-DD'),
      isCurrentMonth: false,
      isPast: false,
    })
  }

  return days
})

function getDayClasses(day) {
  const classes = []

  if (!day.isCurrentMonth) {
    classes.push('text-gray-300 cursor-default')
  } else if (day.isPast) {
    classes.push('text-gray-300 cursor-not-allowed')
  } else if (day.isSelected) {
    classes.push('bg-[#F25A23] text-white font-semibold')
  } else if (day.isToday) {
    classes.push(
      'bg-[#F25A23]/10 text-[#F25A23] font-semibold hover:bg-[#F25A23]/20',
    )
  } else {
    classes.push('text-gray-700 hover:bg-gray-100')
  }

  return classes.join(' ')
}

function toggleCalendar() {
  isOpen.value = !isOpen.value
}

function closeCalendar() {
  isOpen.value = false
}

function prevMonth() {
  currentMonth.value = currentMonth.value.subtract(1, 'month')
}

function nextMonth() {
  currentMonth.value = currentMonth.value.add(1, 'month')
}

function selectDate(day) {
  if (!day.isCurrentMonth || day.isPast) return

  emit('update:modelValue', day.fullDate)
  emit('change', day.fullDate)
  isOpen.value = false
}

function selectToday() {
  const todayStr = today.value.format('YYYY-MM-DD')
  emit('update:modelValue', todayStr)
  emit('change', todayStr)
  isOpen.value = false
}

function clearDate() {
  emit('update:modelValue', '')
  emit('change', '')
  isOpen.value = false
}

// Handle click outside using capture phase
function handleDocumentClick(e) {
  if (!isOpen.value) return

  // Check if click is inside container (input or dropdown)
  if (containerRef.value && containerRef.value.contains(e.target)) {
    return
  }

  closeCalendar()
}

onMounted(() => {
  // Use capture phase to get events before Dialog can stop them
  document.addEventListener('click', handleDocumentClick, true)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick, true)
})
</script>
