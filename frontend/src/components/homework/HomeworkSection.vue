<script setup>
import { ref, reactive, watchEffect, onMounted } from 'vue'
import {
  createResource,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRow,
  ListRowItem,
} from 'frappe-ui'
import { useRouter } from 'vue-router'
import { studentStore } from '@/stores/student'
import { formatDateTimeToTimeDMY } from '../../utils/date'

const props = defineProps({
  customHomework: {
    type: [String, Object, Array],
    required: true,
    default: null,
  },
})

const { studentInfo } = studentStore()
const router = useRouter()

const homeworkList = ref([])
const homeworkLoading = ref(false)

// Check if date is overdue
function isOverdue(dateStr) {
  if (!dateStr) return false
  try {
    return new Date(dateStr).getTime() < new Date().getTime()
  } catch {
    return false
  }
}

// Format date to DD-MM-YYYY
function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    const day = String(d.getDate()).padStart(2, '0')
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const year = d.getFullYear()
    return `${day}-${month}-${year}`
  } catch {
    return '—'
  }
}

// Format time to HH:mm:ss
function formatTime(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    const hours = String(d.getHours()).padStart(2, '0')
    const minutes = String(d.getMinutes()).padStart(2, '0')
    const seconds = String(d.getSeconds()).padStart(2, '0')
    return `${hours}:${minutes}:${seconds}`
  } catch {
    return ''
  }
}

const tableData = reactive({
  rows: homeworkList,
  columns: [
    { label: 'TÊN BÀI TẬP', key: 'title', width: 1 },
    { label: 'NGÀY GIAO BÀI', key: 'date_start', width: '200px' },
    { label: 'HẠN NỘP BÀI', key: 'date_end', width: '200px' },
    { label: 'HÀNH ĐỘNG', key: 'action', width: '140px' },
  ],
})

function onHomeworkSubmitted() {
  console.log(
    '[onHomeworkSubmitted] Homework submitted successfully, reloading list...',
  )
}

onMounted(async () => {
  console.log(
    '[HomeworkSection] customHomework (initial):',
    props.customHomework,
  )

  // Lấy danh sách homework_names từ customHomework
  const homeworkNames = Array.isArray(props.customHomework)
    ? props.customHomework.map((h) => h?.homework).filter(Boolean)
    : []

  console.log('[HomeworkSection] homeworkNames:', homeworkNames)

  if (!homeworkNames.length) {
    console.log('[HomeworkSection] Không có homework nào trong customHomework')
    return
  }

  // Gọi API get_homeworks để lấy chi tiết từng Homework
  createResource({
    url: 'education.education.api.get_homeworks',
    method: 'POST',
    params: {
      homework_names: homeworkNames,
    },
    onSuccess: (res) => {
      const data = res?.message || res
      console.log(
        '[HomeworkSection] Homework details from get_homeworks:',
        data,
      )
      homeworkList.value = Array.isArray(data) ? data : []
    },
    onError: (err) => {
      console.error('[HomeworkSection] Error calling get_homeworks:', err)
    },
  }).submit()
})
</script>

<template>
  <div class="overflow-hidden rounded-lg shadow-xl bg-white">
    <div
      class="p-3 md:p-6 border-b border-gray-200 flex items-center justify-between"
    >
      <h4 class="md:text-lg text-base font-semibold">Bài tập về nhà</h4>
    </div>
    <div class="p-3 md:p-6">
      <div v-if="homeworkLoading" class="text-xs text-gray-500">
        Đang tải...
      </div>
      <div v-else>
        <!-- Mobile: Card View -->
        <div v-if="tableData.rows.length" class="md:hidden space-y-3">
          <div
            v-for="row in tableData.rows"
            :key="row.name"
            class="p-4 border border-gray-200 rounded-lg hover:border-[var(--color-primary)]/40 hover:bg-[var(--color-primary)]/5 transition-all cursor-pointer"
            @click="() => router.push({ path: `/homework/${row.name}` })"
          >
            <h5 class="font-semibold text-sm text-gray-900 mb-3">
              {{ row.title || '—' }}
            </h5>
            <div class="space-y-2 text-xs text-gray-600">
              <div class="flex justify-between">
                <span class="text-gray-500">Ngày giao bài:</span>
                <span class="font-medium">{{
                  formatDateTimeToTimeDMY(row?.date_start) || '—'
                }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Hạn nộp bài:</span>
                <span class="font-medium">{{
                  formatDateTimeToTimeDMY(row?.date_end) || '—'
                }}</span>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t border-gray-100">
              <button
                class="w-full text-xs px-3 py-2 rounded border border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-white transition font-medium"
                @click.stop="
                  () => router.push({ path: `/homework/${row.name}` })
                "
              >
                Xem chi tiết
              </button>
            </div>
          </div>
        </div>

        <!-- Desktop: Card View -->
        <div v-if="tableData.rows.length" class="hidden md:block">
          <!-- Header -->
          <div
            class="grid grid-cols-12 gap-4 px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            <div class="col-span-5">TÊN BÀI TẬP</div>
            <div class="col-span-3">NGÀY GIAO BÀI</div>
            <div class="col-span-3">HẠN NỘP BÀI</div>
            <div class="col-span-1 text-right">HÀNH ĐỘNG</div>
          </div>

          <!-- Items -->
          <div class="space-y-3">
            <div
              v-for="row in tableData.rows"
              :key="row.name"
              class="grid grid-cols-12 gap-4 items-center px-4 py-4 border border-gray-200 rounded-lg hover:border-[var(--color-primary)]/40 hover:shadow-sm transition-all"
            >
              <!-- Title -->
              <div class="col-span-5 flex items-center gap-3">
                <div
                  class="w-8 h-8 rounded-lg flex items-center justify-center bg-orange-100 text-primary flex-shrink-0"
                >
                  <span class="material-symbols-rounded text-base"
                    >radio_button_checked</span
                  >
                </div>
                <span
                  class="font-bold text-gray-900 truncate cursor-pointer hover:text-[var(--color-primary)] transition-colors"
                  @click="() => router.push({ path: `/homework/${row.name}` })"
                  >{{ row.title || '—' }}</span
                >
              </div>

              <!-- Date Start -->
              <div class="col-span-3 flex items-center gap-2 text-gray-700">
                <span class="material-symbols-rounded text-gray-400 text-[20px]"
                  >calendar_today</span
                >
                <div class="flex flex-col">
                  <span class="font-semibold text-sm">{{
                    formatDate(row?.date_start)
                  }}</span>
                  <span class="text-xs text-gray-500">{{
                    formatTime(row?.date_start)
                  }}</span>
                </div>
              </div>

              <!-- Date End -->
              <div class="col-span-3 flex items-center gap-2 text-gray-700">
                <span
                  class="material-symbols-rounded text-[20px]"
                  :class="
                    isOverdue(row?.date_end)
                      ? 'text-red-500/80'
                      : 'text-gray-400'
                  "
                  >{{ isOverdue(row?.date_end) ? 'event_busy' : 'event' }}</span
                >
                <div class="flex flex-col">
                  <span
                    class="font-semibold text-sm"
                    :class="isOverdue(row?.date_end) ? 'text-red-600' : ''"
                    >{{ formatDate(row?.date_end) }}</span
                  >
                  <span
                    class="text-xs"
                    :class="
                      isOverdue(row?.date_end)
                        ? 'text-red-400/70'
                        : 'text-gray-500'
                    "
                    >{{ formatTime(row?.date_end) }}</span
                  >
                </div>
              </div>

              <!-- Action -->
              <div class="col-span-1 flex justify-end">
                <button
                  class="text-xs px-3 py-1 rounded border border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-white transition"
                  @click="() => router.push({ path: `/homework/${row.name}` })"
                >
                  Xem chi tiết
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="!tableData.rows.length"
          class="mt-2 p-6 bg-gray-50 border border-gray-200 rounded-md text-center"
        >
          <p class="text-sm text-gray-600">Chưa có bài tập nào được giao.</p>
        </div>
      </div>
    </div>
  </div>
</template>
