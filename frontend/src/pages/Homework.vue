<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createResource, Spinner } from 'frappe-ui'
import { studentStore } from '@/stores/student'

const { studentInfo } = studentStore()
const router = useRouter()
const route = useRoute()

const loading = ref(false)
const error = ref(null)
const homeworks = ref([])

// Đọc tab từ URL hash, mặc định là 'assigned'
const validTabs = ['assigned', 'overdue', 'submitted']
const getTabFromHash = () => {
  const hash = window.location.hash.replace('#', '')
  return validTabs.includes(hash) ? hash : 'assigned'
}
const activeTab = ref(getTabFromHash())

// Cập nhật URL hash khi đổi tab
watch(activeTab, (newTab) => {
  window.location.hash = newTab
})

// Lắng nghe sự kiện hashchange (khi user bấm back/forward)
onMounted(() => {
  window.addEventListener('hashchange', () => {
    activeTab.value = getTabFromHash()
  })
})

function loadHomeworks() {
  const studentId = studentInfo?.name
  if (!studentId) {
    error.value = 'Không tìm thấy thông tin học sinh.'
    return
  }
  loading.value = true
  error.value = null
  createResource({
    url: 'education.education.api.get_homeworks_by_student',
    method: 'POST',
    params: { student: studentId },
    onSuccess: (res) => {
      const data = res?.message || res
      homeworks.value = Array.isArray(data) ? data : data?.data || []
      loading.value = false
    },
    onError: (err) => {
      error.value = err?.message || 'Không thể tải danh sách bài tập.'
      loading.value = false
    },
  }).submit()
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}

function formatDateLabel(dateStr) {
  if (!dateStr) return 'Không rõ ngày'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}

function countDaysToDeadline(dateStr) {
  if (!dateStr) return { value: 0, unit: 'days' }
  try {
    const target = new Date(dateStr)
    const now = new Date()

    // Calculate days difference (ignoring time)
    const targetDay = new Date(target)
    const todayDay = new Date(now)
    targetDay.setHours(0, 0, 0, 0)
    todayDay.setHours(0, 0, 0, 0)
    const diffDays = Math.ceil(
      (targetDay.getTime() - todayDay.getTime()) / (1000 * 60 * 60 * 24),
    )

    // If same day (diffDays === 0), calculate by hours
    if (diffDays === 0) {
      const diffMs = target.getTime() - now.getTime()
      const diffHours = Math.ceil(diffMs / (1000 * 60 * 60))
      return { value: Math.max(0, diffHours), unit: 'hours' }
    }

    return { value: diffDays, unit: 'days' }
  } catch {
    return { value: 0, unit: 'days' }
  }
}

function isOverdue(hw) {
  if (!hw?.date_end) return false
  try {
    return new Date(hw.date_end).getTime() < new Date().getTime()
  } catch {
    return false
  }
}

function hasSubmission(hw) {
  return (
    Array.isArray(hw?.list_student_submit) && hw.list_student_submit.length > 0
  )
}

const sortedHomeworks = computed(() => {
  return [...homeworks.value].sort((a, b) => {
    const aTime = a?.date_start ? new Date(a.date_start).getTime() : 0
    const bTime = b?.date_start ? new Date(b.date_start).getTime() : 0
    return bTime - aTime
  })
})

const assignedHomeworks = computed(() =>
  sortedHomeworks.value.filter((hw) => !isOverdue(hw) && !hasSubmission(hw)),
)
const overdueHomeworks = computed(() =>
  sortedHomeworks.value.filter((hw) => isOverdue(hw) && !hasSubmission(hw)),
)
const submittedHomeworks = computed(() =>
  sortedHomeworks.value.filter((hw) => hasSubmission(hw)),
)

const tabCounts = computed(() => ({
  assigned: assignedHomeworks.value.length,
  overdue: overdueHomeworks.value.length,
  submitted: submittedHomeworks.value.length,
}))

const groupedByDate = computed(() => {
  const source =
    activeTab.value === 'assigned'
      ? assignedHomeworks.value
      : activeTab.value === 'overdue'
        ? overdueHomeworks.value
        : submittedHomeworks.value

  const groups = {}
  for (const hw of source) {
    const key = formatDateLabel(hw.date_start)
    if (!groups[key]) groups[key] = []
    groups[key].push(hw)
  }
  return Object.entries(groups).map(([dateLabel, items]) => ({
    dateLabel,
    items,
  }))
})

function goToDetail(hw) {
  if (!hw?.name) return
  router.push({ path: `/homework/${hw.name}` })
}

onMounted(() => {
  window.addEventListener('hashchange', () => {
    activeTab.value = getTabFromHash()
  })
  loadHomeworks()
})
</script>

<template>
  <div class="p-4 sm:p-5 space-y-5">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Bài tập về nhà</h1>
      <p class="text-sm text-gray-500 mt-1">
        Quản lý các bài tập được giao, đã nộp và quá hạn
      </p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-16">
      <div class="flex flex-col items-center gap-3">
        <Spinner class="w-8 h-8" />
        <p class="text-sm text-gray-500">Đang tải danh sách bài tập...</p>
      </div>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="rounded-xl bg-red-50 border border-red-200 p-6 text-center"
    >
      <span class="material-icons text-4xl text-red-400 mb-3"
        >error_outline</span
      >
      <p class="text-red-700 font-medium">{{ error }}</p>
    </div>

    <template v-else>
      <!-- Tabs -->
      <div class="border-b border-gray-200">
        <nav
          class="-mb-px flex space-x-2 sm:space-x-6 md:space-x-8"
          aria-label="Tabs"
        >
          <!-- Tab: Bài tập được giao -->
          <button
            type="button"
            class="group inline-flex items-center py-3 sm:py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap flex-shrink-0"
            :class="
              activeTab === 'assigned'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            "
            @click="activeTab = 'assigned'"
          >
            <span
              class="material-icons mr-1 sm:mr-2 text-base sm:text-lg"
              :class="
                activeTab === 'assigned'
                  ? 'text-primary'
                  : 'text-gray-400 group-hover:text-gray-500'
              "
              >assignment</span
            >
            <span class="hidden sm:inline">Bài tập được giao</span>
            <span class="sm:hidden">Được giao</span>
            <span
              class="ml-1 sm:ml-2 py-0.5 px-1.5 sm:px-2.5 rounded-full text-xs font-semibold"
              :class="
                activeTab === 'assigned'
                  ? 'bg-orange-100 text-primary'
                  : 'bg-gray-100 text-gray-600'
              "
              >{{ tabCounts.assigned }}</span
            >
          </button>

          <!-- Tab: Bài tập quá hạn -->
          <button
            type="button"
            class="group inline-flex items-center py-3 sm:py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap flex-shrink-0"
            :class="
              activeTab === 'overdue'
                ? 'border-red-500 text-red-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            "
            @click="activeTab = 'overdue'"
          >
            <span
              class="material-icons mr-1 sm:mr-2 text-base sm:text-lg"
              :class="
                activeTab === 'overdue'
                  ? 'text-red-500'
                  : 'text-gray-400 group-hover:text-gray-500'
              "
              >assignment_late</span
            >
            <span class="hidden sm:inline">Bài tập quá hạn</span>
            <span class="sm:hidden">Quá hạn</span>
            <span
              class="ml-1 sm:ml-2 py-0.5 px-1.5 sm:px-2.5 rounded-full text-xs font-semibold"
              :class="
                activeTab === 'overdue'
                  ? 'bg-red-100 text-red-600'
                  : 'bg-gray-100 text-gray-600'
              "
              >{{ tabCounts.overdue }}</span
            >
          </button>

          <!-- Tab: Bài tập đã nộp -->
          <button
            type="button"
            class="group inline-flex items-center py-3 sm:py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap flex-shrink-0"
            :class="
              activeTab === 'submitted'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            "
            @click="activeTab = 'submitted'"
          >
            <span
              class="material-icons mr-1 sm:mr-2 text-base sm:text-lg"
              :class="
                activeTab === 'submitted'
                  ? 'text-green-500'
                  : 'text-gray-400 group-hover:text-gray-500'
              "
              >assignment_turned_in</span
            >
            <span class="hidden sm:inline">Bài tập đã nộp</span>
            <span class="sm:hidden">Đã nộp</span>
            <span
              class="ml-1 sm:ml-2 py-0.5 px-1.5 sm:px-2.5 rounded-full text-xs font-semibold"
              :class="
                activeTab === 'submitted'
                  ? 'bg-green-100 text-green-600'
                  : 'bg-gray-100 text-gray-600'
              "
              >{{ tabCounts.submitted }}</span
            >
          </button>
        </nav>
      </div>

      <!-- Empty state -->
      <div
        v-if="groupedByDate.length === 0"
        class="bg-white rounded-xl border border-dashed border-gray-300 p-8 text-center"
      >
        <div
          class="w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4"
        >
          <span class="material-icons text-2xl text-gray-400">inbox</span>
        </div>
        <p class="text-gray-500">
          <template v-if="activeTab === 'assigned'"
            >Hiện tại bạn chưa có bài tập nào được giao.</template
          >
          <template v-else-if="activeTab === 'overdue'"
            >Không có bài tập nào đã quá hạn.</template
          >
          <template v-else>Chưa có bài tập nào được nộp.</template>
        </p>
      </div>

      <!-- List grouped by date -->
      <div v-else class="space-y-5">
        <div
          v-for="group in groupedByDate"
          :key="group.dateLabel"
          class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden"
        >
          <!-- Date header -->
          <div
            class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200 flex items-center"
          >
            <span class="material-icons text-gray-400 mr-2 text-sm"
              >calendar_today</span
            >
            <h3 class="text-sm font-semibold text-gray-700">
              {{ group.dateLabel }}
            </h3>
          </div>

          <!-- Table header (Desktop) -->
          <div
            class="hidden md:grid grid-cols-12 gap-4 px-6 py-3 bg-white border-b border-gray-100 text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            <div class="col-span-6">Bài tập</div>
            <div class="col-span-2">Ngày giao</div>
            <div class="col-span-2">Ngày nộp</div>
            <div class="col-span-2 text-right">Trạng thái</div>
          </div>

          <!-- Homework items -->
          <div
            v-for="hw in group.items"
            :key="hw.name"
            class="group hover:bg-gray-50 transition-colors duration-150 border-b border-gray-100 last:border-0 cursor-pointer"
            @click="goToDetail(hw)"
          >
            <div
              class="md:grid md:grid-cols-12 md:gap-4 px-4 sm:px-6 py-4 sm:py-5 items-center"
            >
              <!-- Col 1: Homework info -->
              <div class="col-span-6 mb-3 md:mb-0">
                <div class="flex items-start">
                  <!-- Icon -->
                  <div class="flex-shrink-0 mt-0.5">
                    <div
                      class="w-10 h-10 rounded-lg flex items-center justify-center"
                      :class="
                        hasSubmission(hw)
                          ? 'bg-green-100 text-green-600'
                          : isOverdue(hw)
                            ? 'bg-red-100 text-red-500'
                            : 'bg-orange-100 text-primary'
                      "
                    >
                      <span class="material-icons">code</span>
                    </div>
                  </div>
                  <!-- Content -->
                  <div class="ml-3 sm:ml-4 min-w-0 flex-1">
                    <h4
                      class="text-base sm:text-lg font-extrabold mb-1 truncate group-hover:text-primary transition-colors"
                      :class="
                        hasSubmission(hw)
                          ? 'text-gray-700'
                          : isOverdue(hw)
                            ? 'text-gray-700'
                            : 'text-primary'
                      "
                    >
                      {{ hw.title || 'Không có tiêu đề' }}
                    </h4>
                    <div v-if="hw.assigned_in?.length" class="space-y-0.5">
                      <p
                        class="text-xs font-semibold text-gray-500 uppercase tracking-wide truncate"
                      >
                        {{ hw.assigned_in[0].program }}
                      </p>
                      <p class="text-sm text-gray-600 truncate">
                        {{ hw.assigned_in[0].course }}
                      </p>
                      <p
                        v-if="hw.assigned_in[0].topic"
                        class="text-sm text-gray-500 italic truncate"
                      >
                        {{ hw.assigned_in[0].topic }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Col 2: Start date -->
              <div
                class="col-span-2 mb-2 md:mb-0 flex md:block items-center justify-between"
              >
                <span
                  class="md:hidden text-xs font-medium text-gray-500 uppercase"
                  >Ngày giao:</span
                >
                <span class="text-sm text-gray-700 font-medium">{{
                  formatDate(hw.date_start)
                }}</span>
              </div>

              <!-- Col 3: Due date -->
              <div
                class="col-span-2 mb-2 md:mb-0 flex md:block items-center justify-between"
              >
                <span
                  class="md:hidden text-xs font-medium text-gray-500 uppercase"
                  >Ngày nộp:</span
                >
                <span
                  class="text-sm font-medium"
                  :class="isOverdue(hw) ? 'text-red-600' : 'text-gray-700'"
                >
                  {{ formatDate(hw.date_end) }}
                </span>
              </div>

              <!-- Col 4: Status -->
              <div
                class="col-span-2 flex items-center justify-between md:justify-end"
              >
                <span
                  class="md:hidden text-xs font-medium text-gray-500 uppercase"
                  >Trạng thái:</span
                >
                <!-- Đã nộp -->
                <span
                  v-if="hasSubmission(hw)"
                  class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200"
                >
                  <span
                    class="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"
                  ></span>
                  Đã nộp bài
                </span>
                <!-- Quá hạn -->
                <span
                  v-else-if="isOverdue(hw)"
                  class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200"
                >
                  <span
                    class="w-1.5 h-1.5 rounded-full bg-red-500 mr-1.5"
                  ></span>
                  Quá hạn
                </span>
                <!-- Còn X ngày -->
                <span
                  v-else
                  class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-50 text-yellow-700 border border-yellow-200"
                >
                  <span
                    class="w-1.5 h-1.5 rounded-full bg-yellow-500 mr-1.5"
                  ></span>
                  Còn {{ countDaysToDeadline(hw.date_end).value }}
                  {{
                    countDaysToDeadline(hw.date_end).unit === 'hours'
                      ? 'giờ'
                      : 'ngày'
                  }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
