<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource, Spinner } from 'frappe-ui'
import { useApi } from '@/composables/useApi'
import { studentStore } from '@/stores/student'
import { toastSuccess, toastError } from '@/utils'
import {
  ArrowLeft,
  FileText,
  Calendar,
  Clock,
  AlertCircle,
  Upload,
  Link as LinkIcon,
  Edit3,
  Send,
  X,
  CheckCircle,
  MessageSquare,
  Star,
  User,
  ExternalLink,
  BookOpen,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const { studentInfo } = studentStore()
const homeworkName = route.params.homeworkName
const homework = ref(null)
const loading = ref(false)
const error = ref(null)
const submitting = ref(false)
const submitError = ref(null)
const submitSuccess = ref(false)
const submittedHomework = ref(null)
const loadingSubmission = ref(false)
const isEditing = ref(false)
const submitForm = reactive({ description: '', link_file: '', file: '' })
const submissionMode = ref('link')
const formErrors = reactive({ link_file: '', description: '' })
const fileObj = ref(null)
const fileUploading = ref(false)
const uploadError = ref(null)
const showFileModal = ref(false)
const { uploadEducationFile } = useApi()

const formattedDateStart = computed(() => {
  if (!homework.value?.date_start) return '—'
  return new Date(homework.value.date_start).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
})
const formattedDateEnd = computed(() => {
  if (!homework.value?.date_end) return '—'
  return new Date(homework.value.date_end).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
})
const isOverdue = computed(() => {
  if (!homework.value?.date_end) return false
  try {
    return new Date(homework.value.date_end).getTime() < new Date().getTime()
  } catch {
    return false
  }
})
const hasSubmitted = computed(() => submittedHomework.value !== null)
const canEdit = computed(() => {
  if (!hasSubmitted.value) return false
  // Nếu đã có điểm số -> không cho phép chỉnh sửa
  if (submittedHomework.value?.score != null) return false
  // Nếu chưa quá hạn -> cho phép edit
  if (!isOverdue.value) return true
  // Nếu quá hạn nhưng allow_late = 1 -> vẫn cho phép edit
  if (homework.value?.allow_late === 1) return true
  return false
})

const hasScore = computed(() => submittedHomework.value?.score != null)

// Score color based on score range (thang điểm 10)
const scoreColor = computed(() => {
  const score = submittedHomework.value?.score
  if (score == null)
    return { text: '#059669', bg: '#d1fae5', border: '#6ee7b7' }

  if (score >= 8)
    return { text: '#059669', bg: '#d1fae5', border: '#6ee7b7' } // Xuất sắc - Xanh lá
  else if (score >= 6.5)
    return { text: '#2563eb', bg: '#dbeafe', border: '#93c5fd' } // Khá - Xanh dương
  else if (score >= 5)
    return { text: '#d97706', bg: '#fef3c7', border: '#fcd34d' } // Trung bình - Vàng cam
  else return { text: '#dc2626', bg: '#fee2e2', border: '#fca5a5' } // Yếu - Đỏ
})

// Computed để tránh lỗi Jinja2 parse optional chaining trong template
const studentName = computed(() => {
  return studentInfo?.student_name ? studentInfo.student_name : '—'
})

const allowLateSubmission = computed(() => homework.value?.allow_late === 1)
const canSubmit = computed(() => {
  // Nếu chưa quá hạn -> cho phép nộp
  if (!isOverdue.value) return true
  // Nếu quá hạn nhưng allow_late = 1 -> vẫn cho phép nộp
  if (homework.value?.allow_late === 1) return true
  return false
})
const isFormValid = computed(() => {
  const linkOk =
    submissionMode.value === 'link'
      ? submitForm.link_file?.trim()?.length > 0 && !formErrors.link_file
      : true
  const fileOk =
    submissionMode.value === 'file'
      ? submitForm.file?.trim()?.length > 0 && !uploadError.value
      : true
  return linkOk && fileOk && !formErrors.description
})

function goBack() {
  router.back()
}
function loadSubmission() {
  const studentId = studentInfo?.name
  if (!studentId) return
  loadingSubmission.value = true
  createResource({
    url: 'education.education.api.get_student_homework_submission',
    method: 'POST',
    params: { homework_name: homeworkName, student: studentId },
    onSuccess: (res) => {
      const data = res?.message || res
      submittedHomework.value = data || null
      if (data) {
        submitForm.description = data.description || ''
        submitForm.link_file = data.link_file || ''
        submitForm.file = data.file || ''
      }
      loadingSubmission.value = false
    },
    onError: () => {
      submittedHomework.value = null
      loadingSubmission.value = false
    },
  }).submit()
}
onMounted(() => {
  if (!homeworkName) {
    error.value = 'Thiếu mã bài tập'
    return
  }
  loading.value = true
  createResource({
    url: 'education.education.api.get_homework',
    method: 'POST',
    params: { homework_name: homeworkName },
    onSuccess: (res) => {
      homework.value = res?.message || res || null
      loading.value = false
      loadSubmission()
    },
    onError: (err) => {
      error.value = err?.message || 'Không thể tải thông tin bài tập'
      loading.value = false
    },
  }).submit()
})
function validateForm() {
  formErrors.link_file = ''
  formErrors.description = ''
  let isValid = true
  if (submissionMode.value === 'link') {
    if (!submitForm.link_file?.trim()) {
      formErrors.link_file = 'Link file bài làm là bắt buộc.'
      isValid = false
    } else {
      try {
        const url = new URL(submitForm.link_file.trim())
        if (!['http:', 'https:'].includes(url.protocol)) {
          formErrors.link_file = 'Link file phải là URL hợp lệ.'
          isValid = false
        }
      } catch {
        formErrors.link_file = 'Link file phải là URL hợp lệ.'
        isValid = false
      }
    }
  }
  if (submissionMode.value === 'file' && !submitForm.file?.trim()) {
    uploadError.value = 'File là bắt buộc.'
    isValid = false
  }
  if (
    submitForm.description?.trim()?.length > 0 &&
    submitForm.description.trim().length < 3
  ) {
    formErrors.description = 'Ghi chú phải có ít nhất 3 ký tự.'
    isValid = false
  }
  return isValid
}
function handleSubmitHomework() {
  submitError.value = null
  submitSuccess.value = false
  uploadError.value = null
  if (!validateForm()) return
  const studentId = studentInfo?.name
  if (!studentId) {
    submitError.value = 'Không tìm thấy thông tin học sinh.'
    return
  }
  const isUpdate = submittedHomework.value !== null
  submitting.value = true
  createResource({
    url: 'education.education.api.submit_homework',
    method: 'POST',
    params: {
      homework_name: homeworkName,
      parent: homeworkName,
      student: studentId,
      description: submitForm.description,
      file: submitForm.file,
      link_file: submitForm.link_file,
    },
    onSuccess: (res) => {
      submitting.value = false
      isEditing.value = false
      let response = res?.message || res
      if (typeof response === 'string') {
        try {
          response = JSON.parse(response)
        } catch {
          response = { success: true }
        }
      }
      if (response?.success === false) {
        submitError.value = response?.message || 'Có lỗi xảy ra.'
        return
      }
      submitError.value = null
      formErrors.link_file = ''
      formErrors.description = ''
      submitSuccess.value = true
      toastSuccess({
        message: isUpdate
          ? 'Cập nhật bài nộp thành công'
          : 'Nộp bài tập thành công',
      })
      loadSubmission()
    },
    onError: (err) => {
      submitting.value = false
      submitSuccess.value = false
      submitError.value = err?.message || 'Không thể nộp bài tập.'
      toastError({ message: submitError.value })
    },
  }).submit()
}
function toggleEdit() {
  if (canEdit.value) {
    isEditing.value = !isEditing.value
    if (!isEditing.value) {
      formErrors.link_file = ''
      formErrors.description = ''
      submitError.value = null
    }
  }
}
function openFileModal() {
  if (submissionMode.value !== 'file') submissionMode.value = 'file'
  showFileModal.value = true
}
function closeFileModal() {
  if (!submitForm.file && !window.confirm('Bạn chưa tải file. Đóng cửa sổ?'))
    return
  showFileModal.value = false
  uploadError.value = null
  fileObj.value = null
}
function onFileChange(e) {
  fileObj.value = e?.target?.files?.[0] || null
  uploadError.value = null
}
async function uploadHomeworkFile() {
  uploadError.value = null
  if (!fileObj.value) {
    uploadError.value = 'Vui lòng chọn file.'
    return
  }
  if (isOverdue.value && !allowLateSubmission.value) {
    uploadError.value = 'Đã quá hạn nộp bài.'
    return
  }
  fileUploading.value = true
  try {
    const payload = await uploadEducationFile(fileObj.value, {
      folder: 'Home/Homework',
    })
    if (payload?.success === false)
      throw new Error(payload?.message || 'Tải file thất bại')
    submitForm.file = payload?.file_url || payload?.message?.file_url || ''
    toastSuccess({ message: 'Tải file thành công' })
    showFileModal.value = false
    fileObj.value = null
  } catch (err) {
    uploadError.value = err?.message || 'Tải file thất bại'
    toastError({ message: uploadError.value })
  } finally {
    fileUploading.value = false
  }
}
</script>

<template>
  <div class="p-4 sm:p-5 space-y-4">
    <button
      @click="goBack"
      class="inline-flex items-center gap-2 px-3 py-1.5 text-sm text-slate-600 rounded-lg border border-transparent hover:bg-[#F25A23]/10 hover:text-primary hover:border-[#F25A23]/20 transition-all duration-200"
    >
      <ArrowLeft class="w-4 h-4" /><span>Quay lại</span>
    </button>
    <div v-if="loading" class="flex justify-center items-center py-16">
      <div class="flex flex-col items-center gap-3">
        <Spinner class="w-8 h-8" />
        <p class="text-sm text-slate-500">Đang tải thông tin bài tập...</p>
      </div>
    </div>
    <div
      v-else-if="error"
      class="rounded-xl bg-red-50 border border-red-200 p-6 text-center"
    >
      <div class="text-red-500 text-4xl mb-3">⚠️</div>
      <p class="text-red-800 font-medium">{{ error }}</p>
    </div>
    <template v-else-if="homework">
      <!-- Header Card - Responsive Design -->
      <div
        class="rounded-xl border bg-white shadow-sm overflow-hidden"
        :class="isOverdue ? 'border-red-200' : 'border-gray-200'"
      >
        <div class="p-4">
          <!-- Mobile: Stack layout, Desktop: Row layout -->
          <div
            class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
          >
            <!-- Left: Title & Info -->
            <div class="flex items-start gap-3 min-w-0 flex-1">
              <div
                class="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center"
                :class="isOverdue ? 'bg-red-100' : 'bg-[#F25A23]/10'"
              >
                <span
                  class="material-symbols-outlined text-xl"
                  :class="isOverdue ? 'text-red-500' : 'text-primary'"
                  >description</span
                >
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-start justify-between gap-2 sm:block">
                  <h1
                    class="text-base sm:text-lg line-clamp-2 sm:truncate"
                    style="font-weight: 800; color: #1f2937"
                  >
                    {{ homework.title || 'Không có tiêu đề' }}
                  </h1>
                  <!-- Mobile: Badge inline with title -->
                  <div class="flex-shrink-0 sm:hidden flex flex-wrap gap-1">
                    <div
                      v-if="allowLateSubmission"
                      class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-semibold bg-blue-100 text-blue-700"
                    >
                      <span class="material-symbols-outlined text-xs"
                        >history</span
                      >Nộp trễ
                    </div>
                    <div
                      v-if="isOverdue"
                      class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-semibold bg-red-100 text-red-700"
                    >
                      <span class="material-symbols-outlined text-xs"
                        >error</span
                      >Quá hạn
                    </div>
                    <div
                      v-else-if="hasSubmitted"
                      class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-semibold bg-green-100 text-green-700"
                    >
                      <span class="material-symbols-outlined text-xs"
                        >check_circle</span
                      >Đã nộp
                    </div>
                    <div
                      v-else
                      class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-semibold bg-amber-100 text-amber-700"
                    >
                      <span class="material-symbols-outlined text-xs"
                        >schedule</span
                      >Chưa nộp
                    </div>
                  </div>
                </div>
                <!-- Date info - Stack on mobile -->
                <div
                  class="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-1 sm:gap-x-4 mt-2 text-xs sm:text-sm text-slate-600"
                >
                  <div class="flex items-center gap-1.5">
                    <span
                      class="material-symbols-outlined text-base text-slate-400"
                      >calendar_today</span
                    >
                    <span class="text-slate-500">Ngày giao:</span>
                    <span class="font-medium">{{ formattedDateStart }}</span>
                  </div>
                  <div class="flex items-center gap-1.5">
                    <span
                      class="material-symbols-outlined text-base"
                      :class="isOverdue ? 'text-red-500' : 'text-slate-400'"
                      >schedule</span
                    >
                    <span :class="isOverdue ? 'text-red-500' : 'text-slate-500'"
                      >Hạn nộp:</span
                    >
                    <span
                      :class="
                        isOverdue ? 'text-red-600 font-semibold' : 'font-medium'
                      "
                      >{{ formattedDateEnd }}</span
                    >
                  </div>
                </div>
              </div>
            </div>
            <!-- Desktop: Status Badge -->
            <div class="hidden sm:flex flex-shrink-0 self-center gap-2">
              <div
                v-if="allowLateSubmission"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700"
              >
                <span class="material-symbols-outlined text-sm">history</span
                >Cho phép nộp trễ
              </div>
              <div
                v-if="isOverdue"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-red-100 text-red-700"
              >
                <span class="material-symbols-outlined text-sm">error</span>Quá
                hạn
              </div>
              <div
                v-else-if="hasSubmitted"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-green-100 text-green-700"
              >
                <span class="material-symbols-outlined text-sm"
                  >check_circle</span
                >Đã nộp
              </div>
              <div
                v-else
                class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-700"
              >
                <span class="material-symbols-outlined text-sm">schedule</span
                >Chưa nộp
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Score Section - Prominent at top, right after Header -->
      <div
        v-if="submittedHomework?.score != null"
        class="shadow-sm rounded-lg overflow-hidden bg-white border border-gray-200"
      >
        <div
          class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 bg-gray-50"
        >
          <h3
            class="text-base sm:text-lg flex items-center gap-2"
            style="font-weight: 800; color: #1f2937"
          >
            <span class="material-symbols-outlined text-yellow-500">star</span>
            Kết quả chấm điểm
          </h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-0">
          <!-- Score Column -->
          <div
            class="p-4 flex items-center justify-center border-b md:border-b-0 md:border-r border-gray-100"
          >
            <div
              class="w-16 h-16 rounded-full flex items-center justify-center shadow-md"
              :style="{
                backgroundColor: scoreColor.bg,
                borderWidth: '2px',
                borderStyle: 'solid',
                borderColor: scoreColor.border,
              }"
            >
              <span :style="{ color: scoreColor.text }">
                <span class="text-xl font-bold">{{
                  submittedHomework.score
                }}</span
                ><span class="text-xs font-medium">/10</span>
              </span>
            </div>
          </div>

          <!-- Comment Column -->
          <div class="p-4 md:col-span-3">
            <div class="flex items-center gap-1.5 mb-2">
              <span class="material-symbols-outlined text-blue-500 text-base"
                >chat</span
              >
              <span
                class="text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >Nhận xét của giáo viên</span
              >
            </div>
            <div
              v-if="submittedHomework.comment"
              class="text-gray-700 text-sm leading-relaxed prose prose-sm max-w-none p-3 rounded-lg bg-blue-50 border border-blue-100"
              v-html="submittedHomework.comment"
            ></div>
            <div
              v-else
              class="p-3 rounded-lg bg-gray-50 border border-gray-100"
            >
              <span class="text-gray-400 text-sm italic"
                >Chưa có nhận xét từ giáo viên.</span
              >
            </div>
          </div>
        </div>
      </div>

      <div
        class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden"
      >
        <div
          class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 bg-gray-50"
        >
          <h2
            class="text-base sm:text-lg flex items-center gap-2"
            style="font-weight: 800; color: #1f2937"
          >
            <span class="material-symbols-outlined text-primary">menu_book</span
            >Nội dung bài tập
          </h2>
        </div>
        <div class="p-4 sm:p-6">
          <div
            class="prose prose-sm max-w-none p-4 rounded-lg bg-orange-50 border border-orange-100"
            v-html="
              homework.content ||
              '<p class=text-slate-400>Chưa có nội dung.</p>'
            "
          />
        </div>
      </div>
      <div
        v-if="hasSubmitted && !isEditing"
        class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden"
      >
        <div
          class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 bg-gray-50 flex items-center justify-between gap-2"
        >
          <h2
            class="text-base sm:text-lg flex items-center gap-2"
            style="font-weight: 800; color: #059669"
          >
            <span class="material-symbols-outlined" style="color: #059669"
              >check_circle</span
            >Bài tập đã nộp
          </h2>
          <button
            v-if="canEdit"
            type="button"
            class="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs sm:text-sm rounded-lg border border-[#F25A23]/30 text-primary bg-[#F25A23]/10 hover:bg-[#F25A23]/20 transition-all flex-shrink-0"
            @click="toggleEdit"
          >
            <Edit3 class="w-3.5 h-3.5" /><span>Chỉnh sửa</span>
          </button>
        </div>
        <div class="p-4 sm:p-6 space-y-4 sm:space-y-5">
          <div class="flex items-center gap-3 pb-4 border-b border-gray-100">
            <div
              class="flex-shrink-0 w-10 h-10 bg-[#F25A23]/10 rounded-full flex items-center justify-center"
            >
              <User class="w-5 h-5 text-primary" />
            </div>
            <div>
              <p class="text-sm text-gray-900" style="font-weight: 700">
                {{ studentName }}
              </p>
              <p class="text-xs text-slate-500">Học sinh</p>
            </div>
          </div>
          <div v-if="submittedHomework?.file" class="space-y-2">
            <label
              class="text-xs font-semibold text-gray-600 uppercase tracking-wider flex items-center gap-2"
              ><Upload class="w-4 h-4" />File đã nộp</label
            >
            <a
              :href="submittedHomework.file"
              target="_blank"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-[#F25A23]/5 border border-[#F25A23]/20 text-primary hover:bg-[#F25A23]/10 text-sm w-full overflow-hidden"
              ><FileText class="w-4 h-4 flex-shrink-0" /><span
                class="truncate flex-1 min-w-0"
                >{{ submittedHomework.file.split('/').pop() }}</span
              ><ExternalLink class="w-4 h-4 flex-shrink-0"
            /></a>
          </div>
          <div v-if="submittedHomework?.link_file" class="space-y-2">
            <label
              class="text-xs font-semibold text-gray-600 uppercase tracking-wider flex items-center gap-2"
              ><LinkIcon class="w-4 h-4" />Link bài làm</label
            >
            <a
              :href="submittedHomework.link_file"
              target="_blank"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-600 hover:bg-blue-100 text-sm w-full overflow-hidden"
              ><LinkIcon class="w-4 h-4 flex-shrink-0" /><span
                class="truncate flex-1 min-w-0"
                >{{ submittedHomework.link_file }}</span
              ><ExternalLink class="w-4 h-4 flex-shrink-0"
            /></a>
          </div>
          <div v-if="submittedHomework?.description" class="space-y-2">
            <label
              class="text-xs font-semibold text-gray-600 uppercase tracking-wider flex items-center gap-2"
              ><MessageSquare class="w-4 h-4" />Ghi chú</label
            >
            <p
              class="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 rounded-lg p-4 border border-gray-100"
            >
              {{ submittedHomework.description }}
            </p>
          </div>
          <div
            v-if="isOverdue && !allowLateSubmission && !hasScore"
            class="flex items-center gap-3 p-4 rounded-lg bg-red-50 border border-red-200"
          >
            <AlertCircle class="w-5 h-5 text-red-500" />
            <p class="text-sm text-red-700">
              Đã quá hạn nộp bài. Không thể chỉnh sửa.
            </p>
          </div>
          <div
            v-else-if="isOverdue && allowLateSubmission && !hasScore"
            class="flex items-center gap-3 p-4 rounded-lg bg-blue-50 border border-blue-200"
          >
            <Clock class="w-5 h-5 text-blue-500" />
            <p class="text-sm text-blue-700">
              Bài tập đã quá hạn nhưng giáo viên cho phép nộp trễ. Bạn vẫn có
              thể chỉnh sửa bài nộp.
            </p>
          </div>
        </div>
      </div>
      <div
        v-if="!hasSubmitted || isEditing"
        class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden"
      >
        <div
          class="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 bg-gray-50 flex items-center justify-between gap-2"
        >
          <div class="min-w-0">
            <h2
              class="text-base sm:text-lg flex items-center gap-2"
              style="font-weight: 800; color: #1f2937"
            >
              <Send class="w-5 h-5 text-primary flex-shrink-0" />{{
                hasSubmitted ? 'Chỉnh sửa bài tập' : 'Nộp bài tập'
              }}
            </h2>
          </div>
          <button
            v-if="isEditing"
            type="button"
            class="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs sm:text-sm rounded-lg border border-red-300 text-red-600 bg-red-50 hover:bg-red-100 transition-all flex-shrink-0"
            @click="toggleEdit"
          >
            <X class="w-3.5 h-3.5" /><span>Hủy</span>
          </button>
        </div>
        <div class="p-4 sm:p-6 space-y-4 sm:space-y-5">
          <!-- Thông tin học sinh -->
          <div class="flex items-center gap-3 pb-4 border-b border-gray-100">
            <div
              class="flex-shrink-0 w-10 h-10 bg-[#F25A23]/10 rounded-full flex items-center justify-center"
            >
              <User class="w-5 h-5 text-primary" />
            </div>
            <div>
              <p class="text-sm text-gray-900" style="font-weight: 700">
                {{ studentName }}
              </p>
              <p class="text-xs text-slate-500">Học sinh</p>
            </div>
          </div>
          <div class="space-y-2">
            <label
              class="text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >Hình thức nộp bài</label
            >
            <div class="flex gap-3">
              <button
                type="button"
                :class="[
                  'flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all',
                  submissionMode === 'link'
                    ? 'border-[#F25A23] bg-[#F25A23]/5 text-primary'
                    : 'border-gray-200 text-gray-600 hover:border-gray-300',
                ]"
                @click="submissionMode = 'link'"
              >
                <LinkIcon class="w-4 h-4" /><span>Gán link</span>
              </button>
              <button
                type="button"
                :class="[
                  'flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all',
                  submissionMode === 'file'
                    ? 'border-[#F25A23] bg-[#F25A23]/5 text-primary'
                    : 'border-gray-200 text-gray-600 hover:border-gray-300',
                ]"
                @click="submissionMode = 'file'"
              >
                <Upload class="w-4 h-4" /><span>Tải file</span>
              </button>
            </div>
          </div>
          <div v-if="submissionMode === 'file'" class="space-y-3">
            <label
              class="text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >Tải file bài làm <span class="text-red-500">*</span></label
            >
            <div
              class="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center hover:border-[#F25A23]/40 cursor-pointer"
              :class="{ 'border-[#F25A23] bg-[#F25A23]/5': submitForm.file }"
              @click="openFileModal"
            >
              <Upload class="w-8 h-8 mx-auto text-gray-400 mb-2" />
              <p
                v-if="submitForm.file"
                class="text-sm text-primary font-medium"
              >
                {{ submitForm.file.split('/').pop() }}
              </p>
              <p v-else class="text-sm text-gray-500">Click để chọn file</p>
            </div>
            <p
              v-if="uploadError"
              class="text-xs text-red-600 flex items-center gap-1"
            >
              <AlertCircle class="w-3 h-3" />{{ uploadError }}
            </p>
          </div>
          <div v-if="submissionMode === 'link'" class="space-y-2">
            <label
              class="text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >Link file bài làm <span class="text-red-500">*</span></label
            >
            <div class="relative">
              <LinkIcon
                class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
              />
              <input
                v-model="submitForm.link_file"
                type="text"
                placeholder="https://drive.google.com/..."
                :disabled="isOverdue && !allowLateSubmission"
                :class="[
                  'w-full pl-10 pr-4 py-3 border-2 rounded-lg text-sm outline-none transition-all disabled:bg-gray-100',
                  formErrors.link_file
                    ? 'border-red-300 focus:border-red-500'
                    : 'border-gray-200 focus:border-[#F25A23]',
                ]"
                @blur="validateForm"
                @input="formErrors.link_file = ''"
              />
            </div>
            <p
              v-if="formErrors.link_file"
              class="text-xs text-red-600 flex items-center gap-1"
            >
              <AlertCircle class="w-3 h-3" />{{ formErrors.link_file }}
            </p>
          </div>
          <div class="space-y-2">
            <label
              class="text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >Ghi chú / mô tả (không bắt buộc)</label
            >
            <textarea
              v-model="submitForm.description"
              rows="4"
              placeholder="Nhập ghi chú cho bài làm..."
              :disabled="isOverdue && !allowLateSubmission"
              :class="[
                'w-full px-4 py-3 border-2 rounded-lg text-sm outline-none transition-all resize-none disabled:bg-gray-100',
                formErrors.description
                  ? 'border-red-300 focus:border-red-500'
                  : 'border-gray-200 focus:border-[#F25A23]',
              ]"
              @blur="validateForm"
              @input="formErrors.description = ''"
            />
            <p
              v-if="formErrors.description"
              class="text-xs text-red-600 flex items-center gap-1"
            >
              <AlertCircle class="w-3 h-3" />{{ formErrors.description }}
            </p>
          </div>
          <div
            v-if="submitError"
            class="flex items-center gap-2 p-4 rounded-lg bg-red-50 border border-red-200"
          >
            <AlertCircle class="w-5 h-5 text-red-500" />
            <p class="text-sm text-red-700">{{ submitError }}</p>
          </div>

          <div class="flex justify-end pt-2">
            <button
              type="button"
              class="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-semibold text-white bg-[#F25A23] hover:bg-[#F25A23]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
              :disabled="
                submitting ||
                fileUploading ||
                (isOverdue && !allowLateSubmission) ||
                !isFormValid
              "
              @click="handleSubmitHomework"
            >
              <Spinner v-if="submitting" class="w-4 h-4" /><Send
                v-else
                class="w-4 h-4"
              /><span>{{
                submitting
                  ? 'Đang xử lý...'
                  : hasSubmitted
                    ? 'Cập nhật'
                    : 'Nộp bài'
              }}</span>
            </button>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="text-center py-16">
      <div
        class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#F25A23]/10 mb-4"
      >
        <FileText class="w-8 h-8 text-primary" />
      </div>
      <h3 class="text-lg font-semibold text-gray-900 mb-2">
        Không tìm thấy bài tập
      </h3>
      <p class="text-slate-600 max-w-sm mx-auto">
        Bài tập này không tồn tại hoặc đã bị xóa.
      </p>
    </div>
  </div>
  <div
    v-if="showFileModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden"
    >
      <div
        class="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50"
      >
        <h3 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Upload class="w-5 h-5 text-primary" />Tải file bài làm
        </h3>
        <button
          type="button"
          class="w-8 h-8 flex items-center justify-center rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100"
          @click="closeFileModal"
        >
          <X class="w-5 h-5" />
        </button>
      </div>
      <div class="p-6 space-y-4">
        <div class="space-y-2">
          <label
            class="text-xs font-semibold text-gray-600 uppercase tracking-wider"
            >Chọn file</label
          >
          <input
            type="file"
            class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[#F25A23]/10 file:text-primary hover:file:bg-[#F25A23]/20 cursor-pointer"
            @change="onFileChange"
          />
        </div>
        <button
          type="button"
          class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg text-sm font-semibold text-white bg-[#F25A23] hover:bg-[#F25A23]/90 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="
            fileUploading || (isOverdue && !allowLateSubmission) || !fileObj
          "
          @click="uploadHomeworkFile"
        >
          <Spinner v-if="fileUploading" class="w-4 h-4" /><Upload
            v-else
            class="w-4 h-4"
          /><span>{{ fileUploading ? 'Đang tải...' : 'Tải lên' }}</span>
        </button>
        <div
          v-if="submitForm.file"
          class="flex items-center gap-2 p-3 rounded-lg bg-green-50 border border-green-200"
        >
          <CheckCircle class="w-4 h-4 text-green-500" /><span
            class="text-sm text-green-700 truncate"
            >{{ submitForm.file.split('/').pop() }}</span
          >
        </div>
        <p
          v-if="uploadError"
          class="text-xs text-red-600 flex items-center gap-1"
        >
          <AlertCircle class="w-3 h-3" />{{ uploadError }}
        </p>
      </div>
      <div
        class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end"
      >
        <button
          type="button"
          class="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100"
          @click="closeFileModal"
        >
          Đóng
        </button>
      </div>
    </div>
  </div>
</template>
