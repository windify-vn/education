<template lang="">
  <header
    class="flex justify-between gap-3 items-center px-5 py-2.5 h-12 border-b"
  >
    <div class="flex gap-2 items-center">
      <!-- Mobile Hamburger Menu -->
      <button
        @click="$emit('toggle-mobile-sidebar')"
        class="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
      >
        <Menu class="h-5 w-5" />
      </button>

      <!-- Page Title -->
      <h3 class="font-medium text-lg text-gray-900">
        {{ currentRoute }}
      </h3>
    </div>

    <div class="flex flex-row gap-2 items-center">
      <Button
        v-if="currentRoute === 'Điểm Danh'"
        variant="solid"
        label="Đăng ký nghỉ"
        @click="setIsAttendancePage(true)"
        icon-left="plus"
      />
      <!-- Notification Bell -->
      <!-- <NotificationBell /> -->
    </div>
  </header>
</template>
<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { leaveStore } from '@/stores/leave'
import { Menu } from 'lucide-vue-next'
import NotificationBell from '@/components/common/NotificationBell.vue'

// Define emits
const emit = defineEmits(['toggle-mobile-sidebar'])

const router = useRouter()
const currentRoute = computed(() => router.currentRoute.value.name)

const { setIsAttendancePage } = leaveStore()
</script>
