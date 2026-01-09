<template>
  <div>
    <div v-if="!isAuthRoute" class="flex h-screen w-screen">
      <!-- Desktop Sidebar -->
      <div class="hidden lg:block h-full border-r bg-gray-50">
        <Sidebar />
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 flex flex-col overflow-auto scroll-smooth">
        <Navbar @toggle-mobile-sidebar="toggleMobileSidebar" />
        <router-view
          class="flex-1 overflow-auto scroll-smooth bg-[url('/files/bg-banner.png')] bg-size-[100%] bg-center"
        />
      </div>

      <!-- Mobile Sidebar Overlay -->
      <Transition
        enter-active-class="transition-opacity duration-300"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-300"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="isMobileSidebarOpen"
          class="lg:hidden fixed inset-0 z-50 flex"
          @click="closeMobileSidebar"
        >
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black bg-opacity-50"></div>

          <!-- Sidebar -->
          <Transition
            enter-active-class="transition-transform duration-300 ease-out"
            enter-from-class="-translate-x-full"
            enter-to-class="translate-x-0"
            leave-active-class="transition-transform duration-300 ease-in"
            leave-from-class="translate-x-0"
            leave-to-class="-translate-x-full"
          >
            <div
              v-if="isMobileSidebarOpen"
              class="relative flex flex-col max-w-[85vw] bg-white shadow-xl"
              @click.stop
            >
              <Sidebar @close-mobile-sidebar="closeMobileSidebar" />
            </div>
          </Transition>
        </div>
      </Transition>
    </div>
    <div v-else class="h-screen w-screen">
      <router-view
        class="h-full w-full scroll-smooth bg-[url('/files/bg-banner.png')] bg-size-[100%] bg-center"
      />
    </div>
    <Toast />
  </div>
</template>

<script setup>
import Sidebar from './components/sidebar/Sidebar.vue'
import Navbar from './components/navbar/Navbar.vue'
import Toast from './components/common/Toast.vue'
import { RouterView, useRoute } from 'vue-router'
import { computed, ref, onMounted, onUnmounted, Transition, watch } from 'vue'
import { usersStore } from '@/stores/user'
import { sessionStore } from '@/stores/session'
import { studentStore } from '@/stores/student'

const route = useRoute()
const isAuthRoute = computed(() => route.path === '/login')

// Store instances
const { isLoggedIn } = sessionStore()
const { user } = usersStore()
const { student, studentInfo } = studentStore()

// Mobile sidebar state
const isMobileSidebarOpen = ref(false)

// Toggle mobile sidebar
const toggleMobileSidebar = () => {
  isMobileSidebarOpen.value = !isMobileSidebarOpen.value
}

// Close mobile sidebar
const closeMobileSidebar = () => {
  isMobileSidebarOpen.value = false
}

// Close sidebar when route changes (mobile)
const closeOnRouteChange = () => {
  if (isMobileSidebarOpen.value) {
    closeMobileSidebar()
  }
}

// Watch for route changes
const unwatchRoute = watch(route, () => {
  closeOnRouteChange()
})

// Handle escape key
const handleEscapeKey = (event) => {
  if (event.key === 'Escape' && isMobileSidebarOpen.value) {
    closeMobileSidebar()
  }
}

// Handle window resize
const handleResize = () => {
  if (window.innerWidth >= 1024) {
    // lg breakpoint
    closeMobileSidebar()
  }
}

// Kiểm tra student info khi component mount
const checkStudentInfo = async () => {
  if (isLoggedIn.value && !isAuthRoute.value) {
    if (user.data.length === 0) {
      await user.reload()
    }
    await student.reload()

    // Kiểm tra nếu có user info nhưng không có student info
    if (
      user.data.length > 0 &&
      (!studentInfo || Object.keys(studentInfo).length === 0)
    ) {
      window.location.href = '/app/education'
    }
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey)
  window.addEventListener('resize', handleResize)
  checkStudentInfo()
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey)
  window.removeEventListener('resize', handleResize)
  unwatchRoute()
})
</script>
