<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-[9999] flex flex-col-reverse gap-2">
      <TransitionGroup
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-full"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-full"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg min-w-[280px] max-w-[400px]"
          :class="toastClasses[toast.type]"
        >
          <component
            :is="toastIcons[toast.type]"
            class="w-5 h-5 flex-shrink-0"
          />
          <span class="text-sm font-medium flex-1">{{ toast.message }}</span>
          <button
            @click="removeToast(toast.id)"
            class="p-1 rounded hover:bg-black/10 transition-colors"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { TransitionGroup, Teleport } from 'vue'
import { getToasts, removeToast } from '@/utils'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-vue-next'

const toasts = getToasts()

const toastClasses = {
  success: 'bg-green-50 text-green-800 border border-green-200',
  error: 'bg-red-50 text-red-800 border border-red-200',
  warning: 'bg-amber-50 text-amber-800 border border-amber-200',
  info: 'bg-blue-50 text-blue-800 border border-blue-200',
}

const toastIcons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
}
</script>
