<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Spinner } from 'frappe-ui'
import {
  Bell,
  BellOff,
  BookOpen,
  Award,
  Calendar,
  FileText,
  AlertCircle,
  Check,
  CheckCheck,
  Trash2,
} from 'lucide-vue-next'
import Pagination from '@/components/common/Pagination.vue'

const router = useRouter()

const loading = ref(false)
const error = ref(null)

// Pagination
const currentPage = ref(1)
const pageSize = 3

// Đọc tab từ URL hash, mặc định là 'all'
const validTabs = ['all', 'unread', 'read']
const getTabFromHash = () => {
  const hash = window.location.hash.replace('#', '')
  return validTabs.includes(hash) ? hash : 'all'
}
const activeTab = ref(getTabFromHash())

// Cập nhật URL hash khi đổi tab
watch(activeTab, (newTab) => {
  window.location.hash = newTab
  currentPage.value = 1 // Reset page khi đổi tab
})

// Mock Data - Thông báo
const notifications = ref([
  {
    id: 1,
    type: 'homework',
    title: 'Bài tập mới: Luyện tập từ vựng Unit 5',
    message:
      'Giáo viên Nguyễn Văn A vừa giao bài tập "Luyện tập từ vựng Unit 5" cho lớp Tiếng Anh giao tiếp. Hạn nộp: 15/01/2026.',
    time: '5 phút trước',
    date: '2026-01-12',
    read: false,
    link: '/homework',
  },
  {
    id: 2,
    type: 'achievement',
    title: 'Chúc mừng! Bạn đã nhận được huy hiệu mới',
    message:
      'Bạn đã hoàn thành xuất sắc 10 bài tập liên tiếp và nhận được huy hiệu "Học sinh chăm chỉ". Tiếp tục phát huy nhé!',
    time: '1 giờ trước',
    date: '2026-01-12',
    read: false,
    link: '/profile',
  },
  {
    id: 3,
    type: 'schedule',
    title: 'Nhắc nhở lịch học ngày mai',
    message:
      'Bạn có lớp học "Tiếng Anh giao tiếp" vào lúc 14:00 ngày mai (13/01/2026) tại phòng A101. Đừng quên chuẩn bị bài nhé!',
    time: '2 giờ trước',
    date: '2026-01-12',
    read: false,
    link: '/schedule',
  },
  {
    id: 4,
    type: 'result',
    title: 'Kết quả bài kiểm tra giữa kỳ môn Toán',
    message:
      'Kết quả bài kiểm tra giữa kỳ môn Toán đã được công bố. Điểm của bạn: 8.5/10. Xếp hạng: 5/30 học sinh trong lớp.',
    time: '1 ngày trước',
    date: '2026-01-11',
    read: true,
    link: '/assessment-results',
  },
  {
    id: 5,
    type: 'announcement',
    title: 'Thông báo lịch nghỉ Tết Nguyên Đán 2026',
    message:
      'Nhà trường thông báo lịch nghỉ Tết Nguyên Đán 2026: Từ ngày 15/01 đến 25/01/2026. Chúc các em và gia đình một năm mới an khang thịnh vượng!',
    time: '2 ngày trước',
    date: '2026-01-10',
    read: true,
    link: null,
  },
  {
    id: 6,
    type: 'homework',
    title: 'Nhắc nhở: Bài tập sắp đến hạn',
    message:
      'Bài tập "Bài tập về nhà Unit 4" sẽ hết hạn trong 2 ngày nữa (14/01/2026). Hãy hoàn thành và nộp bài đúng hạn nhé!',
    time: '3 ngày trước',
    date: '2026-01-09',
    read: true,
    link: '/homework',
  },
  {
    id: 7,
    type: 'schedule',
    title: 'Lịch học đã được cập nhật',
    message:
      'Lịch học tuần tới đã được cập nhật. Lớp Tiếng Anh giao tiếp sẽ chuyển sang phòng B202 thay vì A101 như trước.',
    time: '4 ngày trước',
    date: '2026-01-08',
    read: true,
    link: '/schedule',
  },
  {
    id: 8,
    type: 'achievement',
    title: 'Bạn đã đạt mốc 100 điểm thưởng!',
    message:
      'Chúc mừng bạn đã tích lũy được 100 điểm thưởng! Bạn có thể đổi điểm lấy các phần quà hấp dẫn tại mục Thành tích.',
    time: '5 ngày trước',
    date: '2026-01-07',
    read: true,
    link: '/achievements-ranking',
  },
])

// Computed
const allNotifications = computed(() => notifications.value)
const unreadNotifications = computed(() =>
  notifications.value.filter((n) => !n.read),
)
const readNotifications = computed(() =>
  notifications.value.filter((n) => n.read),
)

const tabCounts = computed(() => ({
  all: allNotifications.value.length,
  unread: unreadNotifications.value.length,
  read: readNotifications.value.length,
}))

const currentNotifications = computed(() => {
  if (activeTab.value === 'unread') return unreadNotifications.value
  if (activeTab.value === 'read') return readNotifications.value
  return allNotifications.value
})

// Paginated notifications
const paginatedNotifications = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return currentNotifications.value.slice(start, end)
})

// Group by date (paginated)
const groupedByDate = computed(() => {
  const groups = {}
  for (const notification of paginatedNotifications.value) {
    const key = formatDateLabel(notification.date)
    if (!groups[key]) groups[key] = []
    groups[key].push(notification)
  }
  return Object.entries(groups).map(([dateLabel, items]) => ({
    dateLabel,
    items,
  }))
})

// Methods
function formatDateLabel(dateStr) {
  if (!dateStr) return 'Không rõ ngày'
  try {
    const d = new Date(dateStr)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    if (d.toDateString() === today.toDateString()) return 'Hôm nay'
    if (d.toDateString() === yesterday.toDateString()) return 'Hôm qua'

    return d.toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}

function markAsRead(notification) {
  notification.read = true
}

function markAsUnread(notification) {
  notification.read = false
}

function markAllAsRead() {
  notifications.value.forEach((n) => {
    n.read = true
  })
}

function deleteNotification(notification) {
  const index = notifications.value.findIndex((n) => n.id === notification.id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

function handleNotificationClick(notification) {
  markAsRead(notification)
  if (notification.link) {
    router.push(notification.link)
  }
}

function getIcon(type) {
  const icons = {
    homework: FileText,
    achievement: Award,
    schedule: Calendar,
    result: BookOpen,
    announcement: AlertCircle,
  }
  return icons[type] || Bell
}

function getIconBgClass(type) {
  const classes = {
    homework: 'bg-blue-100 text-blue-600',
    achievement: 'bg-yellow-100 text-yellow-600',
    schedule: 'bg-green-100 text-green-600',
    result: 'bg-purple-100 text-purple-600',
    announcement: 'bg-orange-100 text-orange-600',
  }
  return classes[type] || 'bg-gray-100 text-gray-600'
}

function getTypeLabel(type) {
  const labels = {
    homework: 'Bài tập',
    achievement: 'Thành tích',
    schedule: 'Lịch học',
    result: 'Kết quả',
    announcement: 'Thông báo',
  }
  return labels[type] || 'Khác'
}

onMounted(() => {
  window.addEventListener('hashchange', () => {
    activeTab.value = getTabFromHash()
  })
})
</script>

<template>
  <div class="p-4 sm:p-5 space-y-5">
    <!-- Header -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
    >
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Thông báo</h1>
        <p class="text-sm text-gray-500 mt-1">
          Quản lý tất cả thông báo của bạn
        </p>
      </div>
      <button
        v-if="unreadNotifications.length > 0"
        @click="markAllAsRead"
        class="inline-flex items-center px-4 py-2 text-sm font-medium text-orange-600 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
      >
        <CheckCheck class="w-4 h-4 mr-2" />
        Đánh dấu tất cả đã đọc
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-16">
      <div class="flex flex-col items-center gap-3">
        <Spinner class="w-8 h-8" />
        <p class="text-sm text-gray-500">Đang tải thông báo...</p>
      </div>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="rounded-xl bg-red-50 border border-red-200 p-6 text-center"
    >
      <AlertCircle class="w-10 h-10 text-red-400 mx-auto mb-3" />
      <p class="text-red-700 font-medium">{{ error }}</p>
    </div>

    <template v-else>
      <!-- Tabs -->
      <div class="border-b border-gray-200">
        <nav
          class="-mb-px flex space-x-2 sm:space-x-6 md:space-x-8"
          aria-label="Tabs"
        >
          <!-- Tab: Tất cả -->
          <button
            type="button"
            class="group inline-flex items-center py-3 sm:py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap flex-shrink-0"
            :class="
              activeTab === 'all'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            "
            @click="activeTab = 'all'"
          >
            <Bell
              class="mr-1 sm:mr-2 w-4 h-4 sm:w-5 sm:h-5"
              :class="
                activeTab === 'all'
                  ? 'text-primary'
                  : 'text-gray-400 group-hover:text-gray-500'
              "
            />
            <span class="hidden sm:inline">Tất cả thông báo</span>
            <span class="sm:hidden">Tất cả</span>
            <span
              class="ml-1 sm:ml-2 py-0.5 px-1.5 sm:px-2.5 rounded-full text-xs font-semibold"
              :class="
                activeTab === 'all'
                  ? 'bg-orange-100 text-primary'
                  : 'bg-gray-100 text-gray-600'
              "
              >{{ tabCounts.all }}</span
            >
          </button>

          <!-- Tab: Chưa đọc -->
          <button
            type="button"
            class="group inline-flex items-center py-3 sm:py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap flex-shrink-0"
            :class="
              activeTab === 'unread'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            "
            @click="activeTab = 'unread'"
          >
            <BellOff
              class="mr-1 sm:mr-2 w-4 h-4 sm:w-5 sm:h-5"
              :class="
                activeTab === 'unread'
                  ? 'text-blue-500'
                  : 'text-gray-400 group-hover:text-gray-500'
              "
            />
            <span class="hidden sm:inline">Chưa đọc</span>
            <span class="sm:hidden">Chưa đọc</span>
            <span
              class="ml-1 sm:ml-2 py-0.5 px-1.5 sm:px-2.5 rounded-full text-xs font-semibold"
              :class="
                activeTab === 'unread'
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-gray-100 text-gray-600'
              "
              >{{ tabCounts.unread }}</span
            >
          </button>

          <!-- Tab: Đã đọc -->
          <button
            type="button"
            class="group inline-flex items-center py-3 sm:py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap flex-shrink-0"
            :class="
              activeTab === 'read'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            "
            @click="activeTab = 'read'"
          >
            <Check
              class="mr-1 sm:mr-2 w-4 h-4 sm:w-5 sm:h-5"
              :class="
                activeTab === 'read'
                  ? 'text-green-500'
                  : 'text-gray-400 group-hover:text-gray-500'
              "
            />
            <span class="hidden sm:inline">Đã đọc</span>
            <span class="sm:hidden">Đã đọc</span>
            <span
              class="ml-1 sm:ml-2 py-0.5 px-1.5 sm:px-2.5 rounded-full text-xs font-semibold"
              :class="
                activeTab === 'read'
                  ? 'bg-green-100 text-green-600'
                  : 'bg-gray-100 text-gray-600'
              "
              >{{ tabCounts.read }}</span
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
          <BellOff class="w-6 h-6 text-gray-400" />
        </div>
        <p class="text-gray-500">
          <template v-if="activeTab === 'all'"
            >Bạn chưa có thông báo nào.</template
          >
          <template v-else-if="activeTab === 'unread'"
            >Không có thông báo chưa đọc.</template
          >
          <template v-else>Không có thông báo đã đọc.</template>
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
            <Calendar class="w-4 h-4 text-gray-400 mr-2" />
            <h3 class="text-sm font-semibold text-gray-700">
              {{ group.dateLabel }}
            </h3>
          </div>

          <!-- Notification items -->
          <div
            v-for="notification in group.items"
            :key="notification.id"
            class="group border-b border-gray-100 last:border-0 transition-colors duration-150"
            :class="
              notification.read
                ? 'bg-white hover:bg-gray-50'
                : 'bg-orange-50/50 hover:bg-orange-50'
            "
          >
            <div class="px-4 sm:px-6 py-4 sm:py-5">
              <div class="flex items-start gap-3 sm:gap-4">
                <!-- Icon -->
                <div
                  class="flex-shrink-0 w-10 h-10 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center"
                  :class="getIconBgClass(notification.type)"
                >
                  <component
                    :is="getIcon(notification.type)"
                    class="w-5 h-5 sm:w-6 sm:h-6"
                  />
                </div>

                <!-- Content -->
                <div
                  class="flex-1 min-w-0 cursor-pointer"
                  @click="handleNotificationClick(notification)"
                >
                  <div class="flex items-start justify-between gap-2">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 mb-1">
                        <span
                          class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                          :class="getIconBgClass(notification.type)"
                        >
                          {{ getTypeLabel(notification.type) }}
                        </span>
                        <span
                          v-if="!notification.read"
                          class="w-2 h-2 bg-orange-500 rounded-full"
                        ></span>
                      </div>
                      <h4
                        class="text-base font-semibold mb-1 group-hover:text-primary transition-colors"
                        :class="
                          notification.read ? 'text-gray-700' : 'text-gray-900'
                        "
                      >
                        {{ notification.title }}
                      </h4>
                      <p class="text-sm text-gray-600 line-clamp-2">
                        {{ notification.message }}
                      </p>
                      <p class="text-xs text-gray-400 mt-2">
                        {{ notification.time }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex-shrink-0 flex items-center gap-1">
                  <button
                    v-if="!notification.read"
                    @click.stop="markAsRead(notification)"
                    class="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Đánh dấu đã đọc"
                  >
                    <Check class="w-4 h-4" />
                  </button>
                  <button
                    v-else
                    @click.stop="markAsUnread(notification)"
                    class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Đánh dấu chưa đọc"
                  >
                    <BellOff class="w-4 h-4" />
                  </button>
                  <button
                    @click.stop="deleteNotification(notification)"
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Xóa thông báo"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <Pagination
          v-model:currentPage="currentPage"
          :totalCount="currentNotifications.length"
          :pageSize="pageSize"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
