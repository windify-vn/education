<template>
  <div class="flex h-full flex-col transition-all duration-500 ease-out relative overflow-hidden" :class="[
    isSidebarCollapsed ? 'w-16' : 'w-64'
  ]">
    <!-- Main background with lighter gradient -->
    <div class="absolute inset-0 bg-gradient-to-br from-[var(--color-primary)]/20 via-[#FF6B35]/15 to-[#E04A1A]/20">
    </div>

    <!-- Main content container -->
    <div class="relative flex flex-col h-full">
      <div class="flex justify-between items-center p-2">
        <!-- User section -->
        <div class="z-10">
          <UserDropdown :isCollapsed="isSidebarCollapsed" :educationSettings="!educationSettings.loading && educationSettings.data
            " />
        </div>
        <!-- Mobile Close Button -->
        <div class="lg:hidden flex justify-end p-2">
          <button @click="$emit('close-mobile-sidebar')"
            class="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors">
            <X class="h-5 w-5" />
          </button>
        </div>
      </div>

      <!-- Navigation menu -->
      <div class="flex-1 px-3 py-2 overflow-y-auto border-t border-[var(--color-primary)]/20">
        <nav class="space-y-1">
          <SidebarLink :label="link.label" :to="link.to" v-for="link in links" :key="link.to"
            :isCollapsed="isSidebarCollapsed" :icon="link.icon" />
        </nav>
      </div>

      <!-- Footer with toggle button (Desktop only) -->
      <div class="hidden lg:block px-3 py-3 border-t border-[var(--color-primary)]/20">
        <SidebarLink :label="isSidebarCollapsedStorage ? 'Mở rộng' : 'Thu gọn'" :isCollapsed="isSidebarCollapsed"
          @click="isSidebarCollapsedStorage = !isSidebarCollapsedStorage"
          class="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary)]/80 text-white hover:text-white font-medium">
          <template #icon>
            <span class="grid h-5 w-5 flex-shrink-0 place-items-center">
              <ArrowLeftToLine class="h-4 w-4 text-white duration-500 ease-out"
                :class="{ '[transform:rotateY(180deg)]': isSidebarCollapsedStorage }" />
            </span>
          </template>
        </SidebarLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import SidebarLink from '@/components/sidebar/SidebarLink.vue'
import { useStorage } from '@vueuse/core'
import {
  ArrowLeftToLine,
  BookOpen,
  CalendarCheck,
  MonitorSmartphone,
  Trophy,
  User,
  UserCheck,
  X,
  FileText,
} from 'lucide-vue-next'
import { computed, onMounted, onUnmounted, ref } from 'vue'

// Define emits
const emit = defineEmits(['close-mobile-sidebar'])

import { createResource } from 'frappe-ui'
import UserDropdown from './UserDropdown.vue'

const links = [
  // {
  // 	label: 'Dashboard',
  // 	to: '/',
  // 	icon: LayoutDashboard,
  // },
  {
    label: 'Hồ sơ cá nhân',
    to: '/profile',
    icon: User,
  },
  {
    label: 'Chương trình học',
    to: '/program',
    icon: MonitorSmartphone,
  },
  {
    label: 'Lịch học',
    to: '/schedule',
    icon: CalendarCheck,
  },
  // {
  //   label: 'Điểm Số',
  //   to: '/grades',
  //   icon: GraduationCap,
  // },
  // {
  //   label: 'Học Phí',
  //   to: '/fees',
  //   icon: Banknote,
  // },
  {
    label: 'Điểm Danh',
    to: '/attendance',
    icon: UserCheck,
  },
  {
    label: 'Bài tập về nhà',
    to: '/homework',
    icon: BookOpen,
  },
  {
    label: 'Bảng thành tích',
    to: '/achievements-ranking',
    icon: Trophy,
  },
  {
    label: 'Kết quả đánh giá',
    to: '/assessment-results',
    icon: FileText,
  },
  {
    label: 'Tài liệu học tập',
    to: '/learning',
    icon: BookOpen,
  },
  // {
  // 	// TODO: create School Diary Page with card like CRM and from ListView go to Resource Document of each Card
  // 	label: 'Notes',
  // 	to: '/notes',
  // 	icon: BookOpen,
  // },
  // {
  // 	label: 'Profile',
  // 	to: '/profile',
  // 	icon: User,
  // },
]

const isSidebarCollapsedStorage = useStorage('sidebar_is_collapsed', false)
const isMobile = ref(false)

// Computed property for sidebar collapsed state
const isSidebarCollapsed = computed(() => {
  // On mobile, always expanded
  if (isMobile.value) {
    return false
  }
  // On desktop, use storage value
  return isSidebarCollapsedStorage.value
})

// Check if mobile on mount and resize
const checkMobile = () => {
  isMobile.value = window.innerWidth < 1024 // lg breakpoint
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// create a resource which call the function get_school_abbr_logo in api file using createResource
const educationSettings = createResource({
  url: 'education.education.api.get_school_abbr_logo',
  auto: true,
})
</script>

<style scoped>
/* Mobile responsive width */
@media (max-width: 1023px) {
  .flex.h-full.flex-col {
    width: auto !important;
    min-width: 280px;
    max-width: 85vw;
  }
}
</style>