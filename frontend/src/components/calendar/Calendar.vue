<template>
  <div class="p-5 h-full">
    <!-- actions buttons for calendar -->

    <!-- left side  -->
    <!-- Year, Month & Current Program and Dropdown -->
    <!-- right side -->
    <!-- Increment and Decrement Button, View change button default is months or can be set via props! -->

    <div class="flex justify-between mb-2">
      <span class="text-xl font-medium">
        {{ getMonth() + ', ' + currentYear }}</span
      >
      <div class="flex gap-x-1">
        <!-- <button class="border-2 border-green-500 p-2">Previous</button> -->
        <Button
          @click="decrementMonth"
          variant="ghost"
          class="h-4 w-4"
          icon="chevron-left"
        />
        <Button
          @click="incrementMonth"
          variant="ghost"
          class="h-4 w-4"
          icon="chevron-right"
        />
      </div>
    </div>

    <div class="h-[92%] min-h-[400px] sm:min-h-[600px] overflow-x-auto">
      <!-- Day List -->
      <div class="grid grid-cols-7 w-full min-w-[500px] pb-2 bg-gray-400">
        <span
          v-for="day in daysList"
          class="text-center text-gray-900 font-normal text-xs sm:text-md"
          >{{ day }}</span
        >
      </div>

      <!-- Date Grid -->
      <div
        class="grid grid-cols-7 border-t-[1px] border-l-[1px] border-gray-300 h-full w-full min-w-[500px] grid-rows-6"
      >
        <div
          v-for="date in currentMonthDates"
          class="border-r-[1px] border-b-[1px] border-gray-300 h-full"
        >
          <div
            class="flex justify-center h-full font-normal"
            :class="
              currentMonthDate(date) ? 'text-gray-900' : 'text-gray-900/60'
            "
          >
            <div
              v-if="currentMonthDate(date)"
              class="relative flex flex-col items-center w-full h-full"
            >
              <span
                class="py-1 sticky top-0 w-full text-center z-10"
                :class="
                  date.toDateString() === new Date().toDateString()
                    ? 'font-black bg-[var(--color-primary)]/30 text-[var(--color-primary)]'
                    : 'font-normal bg-gray-100 text-gray-900'
                "
              >
                {{ date.getDate() }}
              </span>

              <div
                class="w-full flex-1 p-1 sm:p-2 overflow-y-auto scrollbar-thin"
                :class="
                  date.toDateString() === new Date().toDateString() &&
                  'bg-[var(--color-primary)]/10'
                "
              >
                <CalendarEvent
                  v-for="calendarEvent in parsedData[parseDate(date)]"
                  :event="calendarEvent"
                  :date="date"
                  class="cursor-pointer w-full transition-all duration-300 hover:opacity-80"
                  :draggable="false"
                  :key="calendarEvent.name"
                />
              </div>
            </div>
            <span v-else>{{
              shortMonthList[date.getMonth()] + ' ' + date.getDate()
            }}</span>
          </div>
        </div>
      </div>
      <!-- <div class=" w-20 h-20 bg-orange-400 absolute top-[212px] left">

			</div> -->
    </div>
  </div>
</template>
<script setup>
import { groupBy } from '@/utils'
import { Button } from 'frappe-ui'
import { computed, ref } from 'vue'
import { getCalendarDates } from '../../utils'
import CalendarEvent from './CalendarEvent.vue'

const props = defineProps({
  events: {
    type: Object,
    required: false,
  },
})

let currentMonth = ref(new Date().getMonth())
let currentYear = ref(new Date().getFullYear())

let monthList = [
  'Tháng 1',
  'Tháng 2',
  'Tháng 3',
  'Tháng 4',
  'Tháng 5',
  'Tháng 6',
  'Tháng 7',
  'Tháng 8',
  'Tháng 9',
  'Tháng 10',
  'Tháng 11',
  'Tháng 12',
]

let shortMonthList = [
  'Th1',
  'Th2',
  'Th3',
  'Th4',
  'Th5',
  'Th6',
  'Th7',
  'Th8',
  'Th9',
  'Th10',
  'Th11',
  'Th12',
]

let daysList = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

let currentMonthDates = computed(() => {
  let allDates = getCalendarDates(currentMonth.value, currentYear.value)
  return allDates
})

let parsedData = computed(() => groupBy(props.events, (row) => row.date))

function parseDate(date) {
  let dd = date.getDate()
  let mm = date.getMonth() + 1
  let yyyy = date.getFullYear()

  if (dd < 10) dd = '0' + dd
  if (mm < 10) mm = '0' + mm

  return `${yyyy}-${mm}-${dd}`
}

function getMonth() {
  return monthList[currentMonth.value]
}

function incrementMonth() {
  currentMonth.value++
  if (currentMonth.value > 11) {
    currentMonth.value = 0
    currentYear.value++
  }
}

function decrementMonth() {
  currentMonth.value--
  if (currentMonth.value < 0) {
    currentMonth.value = 11
    currentYear.value--
  }
}

function currentMonthDate(date) {
  return date.getMonth() === currentMonth.value
}
</script>

<style>
.scrollbar-thin {
  scrollbar-width: thin;
}
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

/* Allow Popover to escape overflow containers */
[data-radix-popper-content-wrapper] {
  z-index: 9999 !important;
}
</style>
