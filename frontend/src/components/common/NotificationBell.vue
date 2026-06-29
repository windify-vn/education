<template>
  <div class="relative" ref="notificationRef">
    <!-- Bell Icon Button -->
    <button
      @click="toggleDropdown"
      class="relative p-2 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500"
    >
      <Bell class="h-5 w-5 text-gray-600" />
      <!-- Badge count -->
      <span
        v-if="unreadCount > 0"
        class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center text-[10px] font-bold text-white bg-red-500 rounded-full px-1"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- Dropdown Panel -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-lg border border-gray-200 z-50 overflow-hidden"
      >
        <!-- Header -->
        <div
          class="flex items-center justify-between px-4 py-3 border-b bg-gray-50"
        >
          <h3 class="font-semibold text-gray-900">Thông báo</h3>
          <button
            v-if="unreadCount > 0"
            @click="markAllAsRead"
            class="text-xs text-orange-600 hover:text-orange-700 font-medium"
          >
            Đánh dấu đã đọc tất cả
          </button>
        </div>

        <!-- Notification List -->
        <div class="max-h-80 overflow-y-auto">
          <div
            v-if="notifications.length === 0"
            class="p-6 text-center text-gray-500"
          >
            <BellOff class="h-10 w-10 mx-auto mb-2 text-gray-300" />
            <p>Không có thông báo nào</p>
          </div>

          <div v-else>
            <div
              v-for="notification in notifications"
              :key="notification.id"
              @click="handleNotificationClick(notification)"
              class="flex gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer border-b last:border-b-0 transition-colors"
              :class="{ 'bg-orange-50': !notification.read }"
            >
              <!-- Icon -->
              <div
                class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
                :class="getIconBgClass(notification.type)"
              >
                <component
                  :is="getIcon(notification.type)"
                  class="h-5 w-5"
                  :class="getIconClass(notification.type)"
                />
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ notification.title }}
                </p>
                <p class="text-xs text-gray-500 line-clamp-2">
                  {{ notification.message }}
                </p>
                <p class="text-xs text-gray-400 mt-1">
                  {{ notification.time }}
                </p>
              </div>

              <!-- Unread indicator -->
              <div v-if="!notification.read" class="flex-shrink-0">
                <span class="w-2 h-2 bg-orange-500 rounded-full block"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-4 py-3 border-t bg-gray-50 text-center">
          <button
            @click="viewAllNotifications"
            class="text-sm text-orange-600 hover:text-orange-700 font-medium"
          >
            Xem tất cả thông báo
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Bell,
  BellOff,
  BookOpen,
  Award,
  Calendar,
  FileText,
  AlertCircle,
} from 'lucide-vue-next'

const router = useRouter()

// State
const isOpen = ref(false)
const notificationRef = ref(null)

// Mock Data
const notifications = ref([
  {
    id: 1,
    type: 'homework',
    title: 'Bài tập mới',
    message:
      'Giáo viên vừa giao bài tập "Luyện tập từ vựng Unit 5" cho lớp của bạn.',
    time: '5 phút trước',
    read: false,
    link: '/homework',
  },
  {
    id: 2,
    type: 'achievement',
    title: 'Chúc mừng! Bạn đã nhận được huy hiệu mới',
    message:
      'Bạn đã hoàn thành xuất sắc 10 bài tập liên tiếp và nhận được huy hiệu "Học sinh chăm chỉ".',
    time: '1 giờ trước',
    read: false,
    link: '/profile',
  },
  {
    id: 3,
    type: 'schedule',
    title: 'Nhắc nhở lịch học',
    message: 'Bạn có lớp học "Tiếng Anh giao tiếp" vào lúc 14:00 hôm nay.',
    time: '2 giờ trước',
    read: false,
    link: '/schedule',
  },
  {
    id: 4,
    type: 'result',
    title: 'Kết quả đánh giá',
    message:
      'Kết quả bài kiểm tra giữa kỳ môn Toán đã được công bố. Điểm của bạn: 8.5/10.',
    time: '1 ngày trước',
    read: true,
    link: '/assessment-results',
  },
  {
    id: 5,
    type: 'announcement',
    title: 'Thông báo từ nhà trường',
    message: 'Lịch nghỉ Tết Nguyên Đán 2026: Từ ngày 15/01 đến 25/01/2026.',
    time: '2 ngày trước',
    read: true,
    link: null,
  },
])

// Computed
const unreadCount = computed(() => {
  return notifications.value.filter((n) => !n.read).length
})

// Methods
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const closeDropdown = () => {
  isOpen.value = false
}

const markAllAsRead = () => {
  notifications.value.forEach((n) => {
    n.read = true
  })
}

const handleNotificationClick = (notification) => {
  notification.read = true
  if (notification.link) {
    router.push(notification.link)
  }
  closeDropdown()
}

const viewAllNotifications = () => {
  router.push('/notifications')
  closeDropdown()
}

const getIcon = (type) => {
  const icons = {
    homework: FileText,
    achievement: Award,
    schedule: Calendar,
    result: BookOpen,
    announcement: AlertCircle,
  }
  return icons[type] || Bell
}

const getIconBgClass = (type) => {
  const classes = {
    homework: 'bg-blue-100',
    achievement: 'bg-yellow-100',
    schedule: 'bg-green-100',
    result: 'bg-purple-100',
    announcement: 'bg-orange-100',
  }
  return classes[type] || 'bg-gray-100'
}

const getIconClass = (type) => {
  const classes = {
    homework: 'text-blue-600',
    achievement: 'text-yellow-600',
    schedule: 'text-green-600',
    result: 'text-purple-600',
    announcement: 'text-orange-600',
  }
  return classes[type] || 'text-gray-600'
}

// Click outside to close
const handleClickOutside = (event) => {
  if (notificationRef.value && !notificationRef.value.contains(event.target)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
