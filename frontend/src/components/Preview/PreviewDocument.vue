<script setup>
import { computed } from 'vue'
import { COLORS } from '@/constants/colors'

const props = defineProps({
  url: { type: String, default: '' },
  title: { type: String, default: 'Tài liệu' }
})

const documentUrl = computed(() => {
  if (!props.url) return ''
  // If it's a relative path, make it absolute
  if (props.url.startsWith('/')) {
    return window.location.origin + props.url
  }
  return props.url
})

const isPdf = computed(() => {
  return props.url?.toLowerCase().includes('.pdf')
})

const fileName = computed(() => {
  if (!props.url) return props.title
  return props.url.split('/').pop() || props.title
})
</script>

<template>
  <div class="w-full">
    <div class="mb-2 text-xs font-semibold text-gray-900">{{ fileName }}</div>
    
    <div v-if="isPdf && documentUrl" class="w-full h-[calc(100vh-200px)] border border-gray-200 rounded-lg overflow-hidden">
      <iframe 
        :src="documentUrl" 
        class="w-full h-full"
        frameborder="0"
        allowfullscreen>
      </iframe>
    </div>
    
    <div v-else-if="documentUrl" class="p-4 text-center text-sm text-gray-600 bg-gray-50 border border-gray-200 rounded-lg">
      <p>Không thể xem trước loại tài liệu này.</p>
      <a :href="documentUrl" target="_blank" :style="{ color: COLORS.primary }" class="underline hover:no-underline">
        Mở tài liệu trong tab mới
      </a>
    </div>
    
    <div v-else class="p-4 text-center text-sm text-gray-600 bg-gray-50 border border-gray-200 rounded-lg">
      Không có tài liệu để hiển thị.
    </div>
  </div>
</template>

<style scoped>
</style>
