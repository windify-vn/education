<script setup>
import { ref, watch, nextTick } from 'vue'
import { Circle, CheckCircle, Eye, X } from 'lucide-vue-next'

const props = defineProps({
  topic: { type: Object, required: true },
  topicName: { type: String, required: true },
  index: { type: Number, required: true },
  expanded: { type: Boolean, default: false },
  dataKey: { type: String, default: '' },
  colors: { type: Object, default: () => ({ primary: '#000' }) },
})

const emit = defineEmits(['toggle'])

const rootEl = ref(null)

watch(
  () => props.expanded,
  async (isOpen) => {
    if (isOpen) {
      await nextTick()
      try {
        rootEl.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
        rootEl.value?.focus?.({ preventScroll: true })
      } catch (_) {}
    }
  }
)
</script>

<template>
  <div class="p-3 bg-white rounded-md border border-gray-200 transition-colors outline-none"
       ref="rootEl"
       :data-preview-key="dataKey"
       tabindex="-1"
       :style="{ borderColor: 'inherit' }"
       @mouseenter="$event.currentTarget.style.borderColor = colors.primary"
       @mouseleave="$event.currentTarget.style.borderColor = 'inherit'">
    <div class="flex items-center justify-between gap-3">
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <div class="text-xs font-medium text-gray-900 truncate">{{ topic.content }}</div>
        </div>
      </div>
      <button :style="{ color: colors.primary, borderColor: colors.primary }"
              class="text-2xs md:text-xs border rounded px-2 py-1 transition-colors flex items-center gap-1"
              @click="emit('toggle', index)">
        <Eye v-if="!expanded" class="size-3" />
        <X v-else class="size-3" />
        {{ expanded ? 'Đóng' : 'Xem' }}
      </button>
    </div>

    <div v-if="expanded" class="mt-2 p-3 rounded-md bg-orange-50 border border-orange-200 text-2xs md:text-sm text-gray-700">
      <slot />
    </div>
  </div>
</template>

<style scoped>
</style>


