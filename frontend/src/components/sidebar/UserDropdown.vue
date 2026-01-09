<template class="z-10">
  <!-- Desktop: Use frappe-ui Dropdown -->
  <div class="hidden lg:block p-2 w-full">
    <Dropdown
      v-model:show="userMenuOpen"
      :options="userDropdownOptions"
      class="flex items-center justify-center w-full"
    >
      <template v-slot="{ open }">
        <button
          class="group flex h-12 items-center rounded-md border border-gray-200/60 bg-white/70 px-1 shadow-sm backdrop-blur transition duration-200 ease-in-out"
          :class="
            isCollapsed
              ? 'w-auto'
              : open
                ? 'ring-1 ring-[#FF6B35] w-[232px]'
                : 'hover:bg-white hover:shadow hover:ring-1 hover:ring-[#FF6B35] w-[232px]'
          "
          aria-label="User menu"
        >
          <div
            class="w-9 h-9 rounded-full flex items-center justify-center overflow-hidden bg-gray-100"
          >
            <Avatar
              v-if="educationSettings?.logo"
              :image="educationSettings?.logo"
              shape="circle"
              size="xl"
            />
            <Avatar
              v-else-if="user?.data?.user_image"
              :image="user.data.user_image"
              :label="user?.data?.full_name"
              shape="circle"
              size="xl"
            />
            <Avatar
              v-else
              :label="user?.data?.full_name || 'U'"
              shape="circle"
              size="xl"
            />
          </div>
          <div
            class="flex flex-1 min-w-0 flex-col text-left transition duration-200 ease-in-out"
            :class="
              isCollapsed
                ? 'opacity-0 ml-0 w-0 overflow-hidden'
                : 'opacity-100 ml-3 w-auto'
            "
          >
            <div
              class="truncate text-sm font-medium text-gray-900 leading-tight"
            >
              {{ educationSettings?.name || 'Education' }}
            </div>
            <div class="mt-0.5 truncate text-xs text-gray-600 leading-tight">
              <span
                v-if="user?.loading"
                class="inline-block h-3 w-24 animate-pulse rounded bg-gray-200"
              ></span>
              <span v-else>{{ user?.data?.full_name }}</span>
            </div>
          </div>

          <div
            class="transition-transform duration-200 ease-in-out"
            :class="
              isCollapsed
                ? 'opacity-0 ml-0 w-0 overflow-hidden'
                : open
                  ? 'rotate-180 ml-2'
                  : 'ml-2'
            "
          >
            <FeatherIcon
              name="chevron-down"
              class="h-4 w-4 text-gray-600 group-hover:text-gray-800"
              aria-hidden="true"
            />
          </div>
        </button>
      </template>
    </Dropdown>
  </div>

  <!-- Mobile: Custom dropdown with Teleport -->
  <div class="lg:hidden p-2 w-full">
    <button
      ref="mobileButtonRef"
      @click="toggleMobileMenu"
      class="group flex h-12 items-center rounded-md border border-gray-200/60 bg-white/70 px-1 shadow-sm backdrop-blur transition duration-200 ease-in-out w-full"
      :class="
        mobileMenuOpen
          ? 'ring-1 ring-[#FF6B35]'
          : 'hover:bg-white hover:shadow hover:ring-1 hover:ring-[#FF6B35]'
      "
      aria-label="User menu"
    >
      <div
        class="w-9 h-9 rounded-full flex items-center justify-center overflow-hidden bg-gray-100"
      >
        <Avatar
          v-if="educationSettings?.logo"
          :image="educationSettings?.logo"
          shape="circle"
          size="xl"
        />
        <Avatar
          v-else-if="user?.data?.user_image"
          :image="user.data.user_image"
          :label="user?.data?.full_name"
          shape="circle"
          size="xl"
        />
        <Avatar
          v-else
          :label="user?.data?.full_name || 'U'"
          shape="circle"
          size="xl"
        />
      </div>
      <div
        class="flex flex-1 min-w-0 flex-col text-left transition duration-200 ease-in-out opacity-100 ml-3 w-auto"
      >
        <div class="truncate text-sm font-medium text-gray-900 leading-tight">
          {{ educationSettings?.name || 'Education' }}
        </div>
        <div class="mt-0.5 truncate text-xs text-gray-600 leading-tight">
          <span
            v-if="user?.loading"
            class="inline-block h-3 w-24 animate-pulse rounded bg-gray-200"
          ></span>
          <span v-else>{{ user?.data?.full_name }}</span>
        </div>
      </div>
      <div
        class="transition-transform duration-200 ease-in-out ml-2"
        :class="mobileMenuOpen ? 'rotate-180' : ''"
      >
        <FeatherIcon
          name="chevron-down"
          class="h-4 w-4 text-gray-600 group-hover:text-gray-800"
          aria-hidden="true"
        />
      </div>
    </button>

    <!-- Mobile Menu - Teleported to body -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-100 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-75 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="mobileMenuOpen"
          class="fixed inset-0 z-[100]"
          @click="closeMobileMenu"
        >
          <div
            class="absolute bg-white rounded-lg shadow-lg border border-gray-200 py-1 min-w-[180px]"
            :style="mobileMenuStyle"
            @click.stop
          >
            <button
              v-for="option in userDropdownOptions"
              :key="option.label"
              @click="handleOptionClick(option)"
              class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <FeatherIcon :name="option.icon" class="h-4 w-4" />
              <span>{{ option.label }}</span>
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>

  <ProfileModal />
</template>

<script setup>
import { Dropdown, FeatherIcon, Avatar } from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/user'
import {
  provide,
  ref,
  onMounted,
  onUnmounted,
  nextTick,
  Teleport,
  Transition,
} from 'vue'
import ProfileModal from '@/components/profile/ProfileModal.vue'
import { useRouter } from 'vue-router'

const { user } = usersStore()
const { logout } = sessionStore()
const router = useRouter()
defineOptions({
  inheritAttrs: false,
})

const props = defineProps({
  isCollapsed: {
    type: Boolean,
    default: false,
  },
  educationSettings: {},
})

const showProfileDialog = ref(false)
const userMenuOpen = ref(false)
const mobileMenuOpen = ref(false)
const mobileButtonRef = ref(null)
const mobileMenuStyle = ref({})
provide('showProfileDialog', showProfileDialog)

const userDropdownOptions = [
  // Only show Test Doctype API menu for specific email
  ...(user.data?.email === 'hocvien1@gmail.com'
    ? [
        {
          icon: 'book-open-check',
          label: 'Test Doctype API',
          onClick: () => {
            console.log('user.data', user.data)
            router.push('/doctype-tester')
          },
        },
      ]
    : []),
  {
    icon: 'log-out',
    label: 'Đăng xuất',
    onClick: () => logout.submit(),
  },
]

const toggleMobileMenu = async () => {
  if (!mobileMenuOpen.value) {
    await nextTick()
    updateMenuPosition()
  }
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const handleOptionClick = (option) => {
  closeMobileMenu()
  if (option.onClick) {
    option.onClick()
  }
}

const updateMenuPosition = () => {
  if (mobileButtonRef.value) {
    const rect = mobileButtonRef.value.getBoundingClientRect()
    mobileMenuStyle.value = {
      top: `${rect.bottom + 4}px`,
      left: `${rect.left}px`,
    }
  }
}

// Close menu on escape key
const handleKeydown = (e) => {
  if (e.key === 'Escape' && mobileMenuOpen.value) {
    closeMobileMenu()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>
