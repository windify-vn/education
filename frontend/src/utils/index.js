import { ref } from 'vue'

// Simple toast state management
const toasts = ref([])
let toastId = 0

export function createToast(options = {}) {
  const { title, message, icon, iconClasses, duration = 5000 } = options

  const id = ++toastId
  const toastMessage = title || message || ''

  // Determine type based on icon/iconClasses
  let type = 'info'
  if (icon === 'check' || iconClasses?.includes('green')) {
    type = 'success'
  } else if (icon === 'x' || iconClasses?.includes('red')) {
    type = 'error'
  } else if (icon === 'alert-triangle' || iconClasses?.includes('amber')) {
    type = 'warning'
  }

  const toast = { id, message: toastMessage, type }
  toasts.value.push(toast)

  // Auto remove after duration
  setTimeout(() => {
    removeToast(id)
  }, duration)

  return id
}

export function removeToast(id) {
  const index = toasts.value.findIndex((t) => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

export function getToasts() {
  return toasts
}

export function toastSuccess(options = {}) {
  return createToast({
    ...options,
    icon: 'check',
    iconClasses: 'text-green-600',
  })
}

export function toastError(options = {}) {
  return createToast({ ...options, icon: 'x', iconClasses: 'text-red-600' })
}

export function toastInfo(options = {}) {
  return createToast({ ...options })
}

export function toastWarning(options = {}) {
  return createToast({
    ...options,
    icon: 'alert-triangle',
    iconClasses: 'text-amber-600',
  })
}

export function getCalendarDates(month = 0, year = 0) {
  let daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  let firstDay = new Date(year, month, 1)
  let leftPadding = firstDay.getDay()
  // debugger
  let datesInCurrentMonth = getCurrentMonthDates(firstDay)
  let datesInPreviousMonth = getBeforeDates(firstDay, leftPadding)
  let datesTillNow = [...datesInPreviousMonth, ...datesInCurrentMonth]
  let datesInNextMonth = getNextMonthDates(datesTillNow)
  let allDates = [...datesTillNow, ...datesInNextMonth]

  return allDates

  function getCurrentMonthDates(date) {
    let month = date.getMonth()
    if (month == 1 && isLeapYear(date)) {
      daysInMonth[month] = 29
    }

    let numberOfDays = daysInMonth[month] + 1
    let allDates = getDatesAfter(date, 1, numberOfDays)
    return allDates
  }

  function getBeforeDates(firstDay, leftPadding) {
    let allDates = getDatesAfter(firstDay, 0, leftPadding, -1)
    allDates = allDates.reverse()
    return allDates
  }

  function getNextMonthDates(currentAndPreviousMonthDates) {
    let lengthOfDates = currentAndPreviousMonthDates.length
    let lastDate = currentAndPreviousMonthDates[lengthOfDates - 1]
    let diff = 42 - lengthOfDates + 1

    let allDates = getDatesAfter(lastDate, 1, diff, 1, true)
    return allDates
  }

  function getDatesAfter(
    date,
    startIndex,
    counter,
    stepper = 1,
    getNextMonthDates = false,
  ) {
    let allDates = []
    for (let index = startIndex; index < counter; index++) {
      let tempDate = new Date(
        date.getFullYear(),
        getNextMonthDates ? date.getMonth() + 1 : date.getMonth(),
        index * stepper,
      )
      // debugger
      allDates.push(tempDate)
    }
    // debugger
    return allDates
  }

  function isLeapYear(date) {
    let year = date.getFullYear()
    return year % 400 === 0 || (year % 100 !== 0 && year % 4 === 0)
  }
}

export function groupBy(obj, fn) {
  if (typeof fn !== 'function') throw new Error(`${fn} should be a function`)
  return Object.keys(obj).reduce((acc, key) => {
    const group = fn(obj[key])
    if (!acc[group]) {
      acc[group] = []
    }
    acc[group].push(obj[key])
    return acc
  }, {})
}
