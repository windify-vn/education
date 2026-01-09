<template>
  <button
    class="group relative flex items-center w-full rounded-lg transition-all duration-300 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]/50 overflow-hidden"
    :class="[
      isActive
        ? 'bg-[var(--color-primary)] text-white shadow-sm'
        : 'hover:bg-[var(--color-primary)]/10 hover:text-[var(--color-primary)] text-gray-700',
      isCollapsed ? 'h-10 justify-center px-2' : 'h-11 px-3'
    ]" @click="handleClick">
    <!-- Icon -->
    <div class="flex items-center">
      <Tooltip :text="label" placement="right" :disabled="!isCollapsed">
        <slot name="icon">
          <span class="grid h-5 w-5 flex-shrink-0 place-items-center">
            <component :is="icon" class="h-4 w-4 transition-colors duration-300 ease-out" :class="[
              isActive
                ? 'text-white'
                : 'text-gray-600 group-hover:text-[var(--color-primary)]'
            ]" />
          </span>
        </slot>
      </Tooltip>

      <!-- Label -->
      <span class="flex-shrink-0 text-sm font-medium transition-all duration-300 ease-out" :class="[
        isCollapsed
          ? 'ml-0 w-0 overflow-hidden opacity-0'
          : 'ml-3 w-auto opacity-100'
      ]">
        {{ label }}
      </span>
    </div>
  </button>
</template>

<script setup>
import { Tooltip } from 'frappe-ui'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const props = defineProps({
  icon: {
    type: Function,
  },
  label: {
    type: String,
    default: '',
  },
  to: {
    type: String,
    default: '',
  },
  isCollapsed: {
    type: Boolean,
    default: false,
  },
})

function handleClick() {
  if (props.to) {
      router.push(props.to)
  } else {
    // Emit click event for custom actions (like toggle button)
    emit('click')
  }
}

const emit = defineEmits(['click'])

let isActive = computed(() => {
  return router.currentRoute.value.path === props.to
})
</script>