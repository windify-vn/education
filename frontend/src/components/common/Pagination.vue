<template>
  <div v-if="totalPages > 1" class="flex justify-center pt-4">
    <div
      class="inline-flex items-center rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden"
    >
      <button
        @click="goToPrevious"
        :disabled="currentPage === 1"
        class="px-4 py-2.5 text-sm font-medium border-r border-gray-200 hover:bg-[#F25A23]/5 hover:text-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {{ previousLabel }}
      </button>
      <span class="px-5 py-2.5 text-sm font-medium bg-gray-50 tabular-nums">
        {{ currentPage }} / {{ totalPages }}
      </span>
      <button
        @click="goToNext"
        :disabled="currentPage >= totalPages"
        class="px-4 py-2.5 text-sm font-medium border-l border-gray-200 hover:bg-[#F25A23]/5 hover:text-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {{ nextLabel }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true,
    default: 1,
  },
  totalCount: {
    type: Number,
    required: true,
    default: 0,
  },
  pageSize: {
    type: Number,
    required: true,
    default: 10,
  },
  previousLabel: {
    type: String,
    default: 'Trước',
  },
  nextLabel: {
    type: String,
    default: 'Sau',
  },
})

const emit = defineEmits(['update:currentPage'])

const totalPages = computed(() => Math.ceil(props.totalCount / props.pageSize))

function goToPrevious() {
  if (props.currentPage > 1) {
    emit('update:currentPage', props.currentPage - 1)
  }
}

function goToNext() {
  if (props.currentPage < totalPages.value) {
    emit('update:currentPage', props.currentPage + 1)
  }
}
</script>
