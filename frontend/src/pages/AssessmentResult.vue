<template>
  <div
    class="p-5 space-y-6 bg-gradient-to-br from-[#F25A23]/5 via-white to-[#F25A23]/5"
  >
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- Header -->
      <div class="flex flex-col gap-4">
        <div>
          <h2
            class="text-xl sm:text-[25px] font-semibold uppercase text-primary"
          >
            Kết quả học tập
          </h2>
          <p class="mt-1 text-sm text-slate-600">
            Xem kết quả đánh giá học tập của bạn
          </p>
        </div>
      </div>

      <!-- Course Filter -->
      <div v-if="availableCourses.length > 1">
        <div class="flex flex-col gap-2 items-start">
          <p class="font-semibold text-primary uppercase text-sm">
            Lọc theo khóa học
          </p>
          <div class="relative w-full sm:w-72" @click.stop>
            <div
              class="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-r from-[#F25A23]/15 via-white to-[#F25A23]/10 opacity-80"
            />
            <button
              type="button"
              class="relative flex w-full items-center justify-between rounded-2xl border border-gray-200 bg-white px-4 py-2.5 text-sm text-slate-800 shadow-xs focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-orange-500 hover:border-orange-500 transition-colors duration-200 text-left backdrop-blur-sm"
              @click="toggleDropdown"
              @keydown.escape.stop.prevent="closeDropdown"
            >
              <span class="block">{{ selectedCourseLabel }}</span>
              <span class="ml-2 flex items-center text-primary">
                <ChevronDown
                  class="h-4 w-4 transition-transform duration-150"
                  :class="{ 'rotate-180': isDropdownOpen }"
                />
              </span>
            </button>
            <div
              v-if="isDropdownOpen"
              class="absolute z-20 mt-1 w-full rounded-2xl border border-[#F25A23]/20 bg-white shadow-2xl max-h-72 overflow-y-auto py-1 backdrop-blur-sm"
            >
              <button
                type="button"
                class="flex w-full items-center justify-between gap-2 px-3 py-2 text-sm text-left"
                :class="[
                  !selectedCourse
                    ? 'bg-[#F25A23]/10 text-primary font-semibold'
                    : 'text-slate-700',
                  'hover:bg-[#F25A23]/15 hover:text-primary transition-colors duration-150',
                ]"
                @click.stop="selectCourse('')"
              >
                <span>Tất cả khóa học</span>
                <Check v-if="!selectedCourse" class="h-4 w-4" />
              </button>
              <button
                v-for="course in availableCourses"
                :key="course"
                type="button"
                class="flex w-full items-center justify-between gap-2 px-3 py-2 text-sm text-left"
                :class="[
                  course === selectedCourse
                    ? 'bg-[#F25A23]/10 text-primary font-semibold'
                    : 'text-slate-700',
                  'hover:bg-[#F25A23]/15 hover:text-primary transition-colors duration-150',
                ]"
                @click.stop="selectCourse(course)"
              >
                <span>{{ course }}</span>
                <Check v-if="course === selectedCourse" class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-16">
        <div class="flex flex-col items-center gap-3">
          <Spinner class="w-8 h-8" />
          <p class="text-sm text-slate-500">Đang tải kết quả...</p>
        </div>
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="rounded-xl bg-red-50 border border-red-200 p-6 text-center"
      >
        <div class="text-red-500 text-4xl mb-3">⚠️</div>
        <p class="text-red-800 font-medium">{{ error }}</p>
      </div>

      <!-- Results -->
      <template v-else>
        <!-- Results List -->
        <div v-if="assessmentResults.length > 0" class="space-y-4">
          <div
            v-for="result in assessmentResults"
            :key="result.name"
            @click="goToDetail(result.name)"
            class="relative overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm hover:shadow-md hover:border-[#F25A23]/40 hover:bg-[#F25A23]/5 transition-all duration-200 cursor-pointer"
          >
            <div class="flex flex-col sm:flex-row items-start sm:items-center">
              <!-- Left: Info Section -->
              <div class="flex-1 p-4 sm:p-5 w-full">
                <div class="flex items-start gap-3">
                  <div
                    class="flex-shrink-0 w-10 h-10 bg-[#F25A23]/10 rounded-full flex items-center justify-center"
                  >
                    <FileText class="w-5 h-5 text-primary" />
                  </div>
                  <div class="min-w-0 flex-1 space-y-1.5">
                    <h4 class="text-base font-semibold text-gray-900">
                      {{ result.assessment_group || 'Đánh giá' }}
                    </h4>
                    <div class="flex flex-col gap-1.5">
                      <div class="flex items-center gap-2">
                        <BookOpen
                          class="w-4 h-4 text-slate-400 flex-shrink-0"
                        />
                        <span class="text-sm text-slate-600">{{
                          result.course || '—'
                        }}</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <Users class="w-4 h-4 text-slate-400 flex-shrink-0" />
                        <span class="text-sm text-slate-600">{{
                          result.student_group || '—'
                        }}</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <Calendar
                          class="w-4 h-4 text-slate-400 flex-shrink-0"
                        />
                        <span class="text-sm text-slate-600">{{
                          formatDate(result.creation)
                        }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right: Score Section -->
              <div
                class="flex items-center justify-center p-4 sm:p-5 border-t sm:border-t-0 sm:border-l border-gray-100 bg-gradient-to-br from-[#F25A23]/5 to-transparent w-full sm:w-32 md:w-40"
              >
                <div class="flex flex-col items-center gap-2">
                  <!-- Circular Score Display -->
                  <div class="relative">
                    <svg
                      class="w-16 h-16 md:w-20 md:h-20 transform -rotate-90"
                      viewBox="0 0 80 80"
                    >
                      <circle
                        cx="40"
                        cy="40"
                        r="34"
                        stroke="#E5E7EB"
                        stroke-width="6"
                        fill="none"
                      />
                      <circle
                        cx="40"
                        cy="40"
                        r="34"
                        :stroke="getScoreColor(result)"
                        stroke-width="6"
                        fill="none"
                        stroke-linecap="round"
                        :stroke-dasharray="`${(getScorePercentage(result) / 100) * 213.6} 213.6`"
                      />
                    </svg>
                    <div
                      class="absolute inset-0 flex flex-col items-center justify-center"
                    >
                      <span
                        class="text-base md:text-lg font-bold text-gray-900"
                        >{{ result.total_score ?? '—' }}</span
                      >
                      <span class="text-xs text-slate-500"
                        >/{{ result.maximum_score ?? '—' }}</span
                      >
                    </div>
                  </div>

                  <!-- Grade Badge -->
                  <div
                    v-if="result.grade"
                    class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold"
                    :class="getGradeBadgeClass(result.grade)"
                  >
                    <Award class="w-3 h-3" />
                    <span>{{ result.grade }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <Pagination
            :current-page="currentPage"
            :total-count="totalCount"
            :page-size="pageLength"
            @update:current-page="currentPage = $event"
          />
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-16">
          <div
            class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#F25A23]/10 mb-4"
          >
            <ClipboardList class="w-8 h-8 text-primary" />
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            Chưa có kết quả đánh giá
          </h3>
          <p class="text-slate-600 max-w-sm mx-auto">
            Bạn chưa có kết quả đánh giá nào. Kết quả sẽ hiển thị khi có đánh
            giá mới.
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { createResource, Spinner } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { studentStore } from '@/stores/student'
import Pagination from '@/components/common/Pagination.vue'
import { getGradeBadgeClass } from '@/utils/gradeUtils'
import {
  FileText,
  Users,
  Calendar,
  Award,
  ChevronDown,
  Check,
  ClipboardList,
  BookOpen,
} from 'lucide-vue-next'

const router = useRouter()
const { studentInfo } = studentStore()

const loading = ref(false)
const error = ref(null)
const assessmentResults = ref([])
const selectedCourse = ref('')
const availableCourses = ref([])
const currentPage = ref(1)
const totalCount = ref(0)
const pageLength = ref(10)
const coursesLoaded = ref(false)
const isDropdownOpen = ref(false)

const selectedCourseLabel = computed(() => {
  return selectedCourse.value || 'Tất cả khóa học'
})

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value
}

function closeDropdown() {
  isDropdownOpen.value = false
}

function selectCourse(course) {
  selectedCourse.value = course
  isDropdownOpen.value = false
}

function goToDetail(resultName) {
  router.push(`/assessment-result/${resultName}`)
}

function handleClickOutside() {
  if (isDropdownOpen.value) {
    isDropdownOpen.value = false
  }
}

function getScorePercentage(result) {
  if (!result.total_score || !result.maximum_score) return 0
  return Math.min(100, (result.total_score / result.maximum_score) * 100)
}

function getScoreColor(result) {
  const percentage = getScorePercentage(result)
  if (percentage >= 80) return '#10B981' // green
  if (percentage >= 60) return '#F59E0B' // amber
  if (percentage >= 40) return '#F25A23' // primary/orange
  return '#EF4444' // red
}

function loadAssessmentResults() {
  const studentId = studentInfo?.name
  if (!studentId) {
    error.value = 'Không tìm thấy thông tin học sinh.'
    return
  }

  loading.value = true
  error.value = null

  createResource({
    url: 'education.education.api.get_assessment_results_for_student',
    method: 'POST',
    params: {
      student: studentId,
      course: selectedCourse.value || null,
      start: (currentPage.value - 1) * pageLength.value,
      page_length: pageLength.value,
    },
    onSuccess: (res) => {
      const data = res?.message || res
      assessmentResults.value = Array.isArray(data) ? data : []
      loadAssessmentResultsCount()
      if (!coursesLoaded.value) {
        coursesLoaded.value = true
        loadCourseOptions()
      }
      loading.value = false
    },
    onError: (err) => {
      console.error('API Error:', err)
      error.value = err?.message || 'Không thể tải kết quả đánh giá.'
      loading.value = false
    },
  }).submit()
}

function loadCourseOptions() {
  const studentId = studentInfo?.name
  if (!studentId) {
    availableCourses.value = []
    return
  }

  createResource({
    url: 'education.education.api.get_assessment_result_courses',
    method: 'POST',
    params: { student: studentId },
    onSuccess: (res) => {
      const data = res?.message || res
      availableCourses.value = Array.isArray(data) ? data : []
    },
    onError: () => {
      availableCourses.value = []
    },
  }).submit()
}

function loadAssessmentResultsCount() {
  const studentId = studentInfo?.name
  if (!studentId) return

  createResource({
    url: 'education.education.api.get_assessment_results_count',
    method: 'POST',
    params: {
      student: studentId,
      course: selectedCourse.value || null,
    },
    onSuccess: (res) => {
      totalCount.value = res?.message || res || 0
    },
    onError: () => {
      totalCount.value = 0
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
    })
  } catch {
    return '—'
  }
}

onMounted(() => {
  loadAssessmentResults()
  window.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', handleClickOutside)
})

watch(selectedCourse, () => {
  currentPage.value = 1
  loadAssessmentResults()
})

watch(currentPage, () => {
  loadAssessmentResults()
})
</script>
