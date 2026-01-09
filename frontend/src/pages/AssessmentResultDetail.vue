<template>
  <div
    class="p-5 space-y-6 bg-gradient-to-br from-[#F25A23]/5 via-white to-[#F25A23]/5"
  >
    <div class="max-w-5xl mx-auto space-y-6">
      <!-- Back Button -->
      <button
        @click="goBack"
        class="inline-flex items-center gap-2 px-3 py-1.5 text-sm text-slate-600 rounded-lg border border-transparent hover:bg-[#F25A23]/10 hover:text-primary hover:border-[#F25A23]/20 transition-all duration-200"
      >
        <ArrowLeft class="w-4 h-4" />
        <span>Quay lại danh sách</span>
      </button>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-16">
        <div class="flex flex-col items-center gap-3">
          <Spinner class="w-8 h-8" />
          <p class="text-sm text-slate-500">Đang tải chi tiết...</p>
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

      <!-- Content -->
      <template v-else-if="resultDetail">
        <!-- Header Card -->
        <div
          class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden"
        >
          <div class="flex flex-col md:flex-row">
            <!-- Left: Info Section -->
            <div class="flex-1 p-5">
              <div class="flex items-start gap-3">
                <div
                  class="flex-shrink-0 w-10 h-10 bg-[#F25A23]/10 rounded-full flex items-center justify-center"
                >
                  <FileText class="w-5 h-5 text-primary" />
                </div>
                <div class="min-w-0 flex-1 space-y-2">
                  <h1 class="text-xl font-bold text-gray-900">
                    {{ resultDetail.assessment_group || 'Chi tiết đánh giá' }}
                  </h1>
                  <!-- 2x2 Grid for info items -->
                  <div class="grid grid-cols-2 gap-x-4 gap-y-1.5">
                    <div class="flex items-center gap-2">
                      <BookOpen class="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <span class="text-sm text-slate-600">{{
                        resultDetail.course || '—'
                      }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <Users class="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <span class="text-sm text-slate-600">{{
                        resultDetail.student_group || '—'
                      }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <Scale class="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <span class="text-sm text-slate-600">{{
                        resultDetail.grading_scale || '—'
                      }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <Calendar class="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <span class="text-sm text-slate-600">{{
                        formatDate(resultDetail.creation)
                      }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Score Section -->
            <div
              class="flex items-center justify-center p-5 md:border-l border-t md:border-t-0 border-gray-100 bg-gradient-to-br from-[#F25A23]/5 to-transparent md:w-48"
            >
              <div class="flex flex-col items-center gap-2">
                <!-- Circular Score Display -->
                <div class="relative">
                  <svg class="w-20 h-20 transform -rotate-90">
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
                      :stroke="getScoreColor(resultDetail)"
                      stroke-width="6"
                      fill="none"
                      stroke-linecap="round"
                      :stroke-dasharray="`${getScorePercentage(resultDetail) * 2.136} 213.6`"
                    />
                  </svg>
                  <div
                    class="absolute inset-0 flex flex-col items-center justify-center"
                  >
                    <span class="text-lg font-bold text-gray-900">{{
                      resultDetail.total_score ?? '—'
                    }}</span>
                    <span class="text-xs text-slate-500"
                      >/{{ resultDetail.maximum_score ?? '—' }}</span
                    >
                  </div>
                </div>

                <!-- Grade Badge -->
                <div
                  v-if="resultDetail.grade"
                  class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-semibold"
                  :class="getGradeBadgeClass(resultDetail.grade)"
                >
                  <Award class="w-3.5 h-3.5" />
                  <span>{{ resultDetail.grade }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Criteria Details Table -->
        <div
          class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden"
        >
          <div class="px-6 py-4 border-b border-gray-100 bg-gray-50">
            <h2
              class="text-lg font-semibold text-gray-900 flex items-center gap-2"
            >
              <ClipboardList class="w-5 h-5 text-primary" />
              Chi tiết đánh giá theo tiêu chí
            </h2>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[640px]">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th
                    class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
                  >
                    STT
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
                  >
                    Tiêu chí đánh giá
                  </th>
                  <th
                    class="px-6 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
                  >
                    Trọng số
                  </th>
                  <th
                    class="px-6 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
                  >
                    Điểm đạt được
                  </th>
                  <th
                    class="px-6 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
                  >
                    Tiến độ
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr
                  v-for="(detail, index) in resultDetail.details"
                  :key="detail.name"
                  class="hover:bg-gray-50 transition-colors"
                >
                  <td class="px-6 py-4 text-sm text-gray-900">
                    {{ index + 1 }}
                  </td>
                  <td class="px-6 py-4">
                    <span class="text-sm font-medium text-gray-900">{{
                      detail.assessment_criteria || '—'
                    }}</span>
                  </td>
                  <td class="px-6 py-4 text-center">
                    <span class="text-sm text-gray-900"
                      >{{ getWeightPercentage(detail) }}%</span
                    >
                  </td>
                  <td class="px-6 py-4 text-center">
                    <span class="text-sm font-semibold text-primary">{{
                      detail.score ?? '—'
                    }}</span>
                    <span class="text-sm text-gray-500"
                      >/{{ detail.maximum_score ?? '—' }}</span
                    >
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-center justify-center gap-2">
                      <div
                        class="flex-1 max-w-[120px] bg-gray-200 rounded-full h-2"
                      >
                        <div
                          class="h-2 rounded-full transition-all"
                          :class="getProgressColor(detail)"
                          :style="{
                            width: `${getProgressPercentage(detail)}%`,
                          }"
                        ></div>
                      </div>
                      <span
                        class="text-xs text-slate-600 min-w-[40px] text-right"
                        >{{ getProgressPercentage(detail) }}%</span
                      >
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Comment Section -->
        <div
          v-if="resultDetail.comment"
          class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden"
        >
          <div class="px-6 py-4 border-b border-gray-100 bg-gray-50">
            <h2
              class="text-lg font-semibold text-gray-900 flex items-center gap-2"
            >
              <MessageSquare class="w-5 h-5 text-primary" />
              Nhận xét
            </h2>
          </div>

          <div class="px-6 py-4">
            <div class="flex items-start gap-3">
              <div
                class="flex-shrink-0 w-10 h-10 bg-[#F25A23]/10 rounded-full flex items-center justify-center"
              >
                <User class="w-5 h-5 text-primary" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-sm font-semibold text-gray-900">{{
                    resultDetail.comment_by || 'Giảng viên'
                  }}</span>
                  <span class="text-xs text-slate-400">•</span>
                  <span class="text-xs text-slate-500">{{
                    formatDate(resultDetail.modified)
                  }}</span>
                </div>
                <p class="text-sm text-gray-700">{{ resultDetail.comment }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty Comment State -->
        <div
          v-else
          class="rounded-xl border border-dashed border-gray-300 bg-white p-8 text-center"
        >
          <MessageSquare class="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p class="text-sm text-gray-500">Chưa có nhận xét nào</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource, Spinner } from 'frappe-ui'
import { getGradeBadgeClass } from '@/utils/gradeUtils'
import {
  ArrowLeft,
  BookOpen,
  Users,
  Calendar,
  Award,
  ClipboardList,
  MessageSquare,
  Scale,
  User,
  FileText,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const error = ref(null)
const resultDetail = ref(null)

function loadResultDetail() {
  const resultId = route.params.id

  if (!resultId) {
    error.value = 'Không tìm thấy ID kết quả đánh giá.'
    return
  }

  loading.value = true
  error.value = null

  createResource({
    url: 'education.education.api.get_assessment_result_detail',
    method: 'POST',
    params: { result_name: resultId },
    onSuccess: (res) => {
      const data = res?.message || res
      resultDetail.value = data
      loading.value = false
    },
    onError: (err) => {
      console.error('API Error:', err)
      error.value = err?.message || 'Không thể tải chi tiết kết quả đánh giá.'
      loading.value = false
    },
  }).submit()
}

function goBack() {
  router.push('/assessment-results')
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

function getScorePercentage(result) {
  if (!result.total_score || !result.maximum_score) return 0
  return Math.min(100, (result.total_score / result.maximum_score) * 100)
}

function getProgressPercentage(detail) {
  if (!detail.score || !detail.maximum_score) return 0
  return Math.round((detail.score / detail.maximum_score) * 100)
}

function getWeightPercentage(detail) {
  if (!detail.maximum_score || !resultDetail.value?.maximum_score) return 0
  return Math.round(
    (detail.maximum_score / resultDetail.value.maximum_score) * 100,
  )
}

function getScoreColor(result) {
  const percentage = getScorePercentage(result)
  if (percentage >= 80) return '#10B981'
  if (percentage >= 60) return '#F59E0B'
  if (percentage >= 40) return '#F25A23'
  return '#EF4444'
}

function getProgressColor(detail) {
  const percentage = getProgressPercentage(detail)
  if (percentage >= 80) return 'bg-green-500'
  if (percentage >= 60) return 'bg-amber-500'
  if (percentage >= 40) return 'bg-orange-500'
  return 'bg-red-500'
}

onMounted(() => {
  loadResultDetail()
})
</script>
