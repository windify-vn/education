<template>
  <!-- Wrapper for margin spacing when used in v-for -->
  <div class="mb-2 sm:mb-3">
    <!-- Event Card -->
    <div
      ref="eventRef"
      class="w-full p-1 sm:p-2 rounded-lg cursor-pointer transition-all duration-200 hover:opacity-80"
      :class="getBackgroundColor"
      @click="togglePopover"
    >
      <div
        class="flex gap-1.5 sm:gap-3 relative px-1 sm:px-2 items-center"
        :class="getBorderClass"
      >
        <FeatherIcon
          name="circle"
          class="h-3 sm:h-4 text-black flex-shrink-0"
        />
        <div class="flex flex-col w-full overflow-hidden">
          <p class="font-medium text-[10px] sm:text-sm text-gray-800 truncate">
            {{ calendarEvent.title }}
          </p>
          <p
            class="font-normal text-[10px] sm:text-xs text-gray-800 truncate"
            v-if="calendarEvent.from_time"
          >
            {{ calendarEvent.from_time }} - {{ calendarEvent.to_time }}
          </p>
        </div>
      </div>
    </div>

    <!-- Teleport Popover to body to escape overflow containers -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="showPopover"
          ref="popoverRef"
          class="fixed bg-white rounded-xl shadow-xl border border-gray-200 z-[9999]"
          :style="popoverStyle"
        >
          <div class="flex flex-col gap-3 p-4 min-w-[240px] max-w-[320px]">
            <!-- Title -->
            <div class="font-semibold text-base text-gray-900 break-words pr-6">
              {{ calendarEvent.title }}
            </div>

            <!-- Close button -->
            <button
              @click.stop="showPopover = false"
              class="absolute top-3 right-3 p-1 rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-600"
            >
              <FeatherIcon name="x" class="h-4 w-4" />
            </button>

            <!-- Event info -->
            <div class="flex flex-col gap-2.5">
              <div class="flex gap-2.5 items-center">
                <FeatherIcon
                  name="calendar"
                  class="h-4 w-4 text-gray-400 flex-shrink-0"
                />
                <span class="text-sm text-gray-600">{{ parseDate() }}</span>
              </div>
              <div class="flex gap-2.5 items-center" v-if="calendarEvent.with">
                <FeatherIcon
                  name="user"
                  class="h-4 w-4 text-gray-400 flex-shrink-0"
                />
                <span class="text-sm text-gray-600">{{
                  calendarEvent.with
                }}</span>
              </div>
              <div
                class="flex gap-2.5 items-center"
                v-if="calendarEvent.from_time && calendarEvent.to_time"
              >
                <FeatherIcon
                  name="clock"
                  class="h-4 w-4 text-gray-400 flex-shrink-0"
                />
                <span class="text-sm text-gray-600">
                  {{ calendarEvent.from_time }} - {{ calendarEvent.to_time }}
                </span>
              </div>
              <div class="flex gap-2.5 items-center" v-if="calendarEvent.room">
                <FeatherIcon
                  name="map-pin"
                  class="h-4 w-4 text-gray-400 flex-shrink-0"
                />
                <span class="text-sm text-gray-600"
                  >Phòng: {{ calendarEvent.room }}</span
                >
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Backdrop to close popover -->
      <div
        v-if="showPopover"
        class="fixed inset-0 z-[9998]"
        @click="showPopover = false"
      />
    </Teleport>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import {
  ref,
  computed,
  onMounted,
  onUnmounted,
  nextTick,
  Teleport,
  Transition,
} from 'vue'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
  date: {
    type: Date,
    required: true,
  },
})

const calendarEvent = computed(() => props.event)
const showPopover = ref(false)
const eventRef = ref(null)
const popoverRef = ref(null)
const popoverStyle = ref({})

async function togglePopover() {
  showPopover.value = !showPopover.value
  if (showPopover.value) {
    await nextTick()
    calculatePosition()
  }
}

function calculatePosition() {
  if (!eventRef.value) return

  const rect = eventRef.value.getBoundingClientRect()
  const popoverWidth = 280
  const popoverHeight = 200
  const padding = 8
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  let left = rect.right + padding
  let top = rect.top

  // Check if popover goes off right edge
  if (left + popoverWidth > viewportWidth - padding) {
    // Position to the left of the event
    left = rect.left - popoverWidth - padding
  }

  // If still off screen (left), center it
  if (left < padding) {
    left = Math.max(padding, (viewportWidth - popoverWidth) / 2)
  }

  // Check if popover goes off bottom edge
  if (top + popoverHeight > viewportHeight - padding) {
    top = viewportHeight - popoverHeight - padding
  }

  // Check if popover goes off top edge
  if (top < padding) {
    top = padding
  }

  popoverStyle.value = {
    left: `${left}px`,
    top: `${top}px`,
  }
}

// Recalculate on scroll/resize
function handleScrollOrResize() {
  if (showPopover.value) {
    calculatePosition()
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScrollOrResize, true)
  window.addEventListener('resize', handleScrollOrResize)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScrollOrResize, true)
  window.removeEventListener('resize', handleScrollOrResize)
})

const getBackgroundColor = computed(() => {
  if (calendarEvent.value.status) {
    return calendarEvent.value.background_color || 'bg-green-100'
  }
  return (
    colorMap[calendarEvent.value?.color]?.background_color || 'bg-green-100'
  )
})

const getBorderClass = computed(() => {
  if (calendarEvent.value.from_time && !calendarEvent.value.status) {
    return [
      'border-l-2',
      colorMap[calendarEvent.value?.color]?.border_color || 'border-green-600',
    ]
  }
  return []
})

const colorMap = {
  blue: { background_color: 'bg-blue-100', border_color: 'border-blue-600' },
  green: { background_color: 'bg-green-100', border_color: 'border-green-600' },
  red: { background_color: 'bg-red-100', border_color: 'border-red-600' },
  orange: {
    background_color: 'bg-orange-100',
    border_color: 'border-orange-600',
  },
  yellow: {
    background_color: 'bg-yellow-100',
    border_color: 'border-yellow-600',
  },
  teal: { background_color: 'bg-teal-100', border_color: 'border-teal-600' },
  violet: {
    background_color: 'bg-violet-100',
    border_color: 'border-violet-600',
  },
  cyan: { background_color: 'bg-cyan-100', border_color: 'border-cyan-600' },
  purple: {
    background_color: 'bg-purple-100',
    border_color: 'border-purple-600',
  },
  pink: { background_color: 'bg-pink-100', border_color: 'border-pink-600' },
  amber: { background_color: 'bg-amber-100', border_color: 'border-amber-600' },
}

function parseDate() {
  const date = props.date.toDateString().split(' ').slice(0, 3)
  const day = date[0]
  const eventDate = date[1] + ' ' + date[2]
  return `${day}, ${eventDate}`
}
</script>
