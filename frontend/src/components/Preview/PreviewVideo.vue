<script setup>
import { computed } from 'vue'
import { COLORS } from '@/constants/colors'

const props = defineProps({
  url: { type: String, default: '' },
})

function extractYouTubeId(rawUrl) {
  if (!rawUrl) return null
  try {
    const url = new URL(rawUrl)
    if (url.hostname.includes('youtu.be')) {
      return url.pathname.replace('/', '') || null
    }
    if (url.hostname.includes('youtube.com') || url.hostname.includes('youtu.be')) {
      if (url.pathname.startsWith('/watch')) {
        return url.searchParams.get('v')
      }
      if (url.pathname.startsWith('/embed/')) {
        return url.pathname.split('/embed/')[1]
      }
    }
  } catch (_) {
    return null
  }
  return null
}

function extractVimeoId(rawUrl) {
  if (!rawUrl) return null
  try {
    const url = new URL(rawUrl)
    if (url.hostname.includes('vimeo.com')) {
      // Patterns: vimeo.com/123456789 or player.vimeo.com/video/123456789
      const parts = url.pathname.split('/').filter(Boolean)
      const id = parts.pop()
      if (id && /^[0-9]+$/.test(id)) return id
    }
  } catch (_) {
    return null
  }
  return null
}

const embedUrl = computed(() => {
  const ytId = extractYouTubeId(props.url)
  if (ytId) return `https://www.youtube-nocookie.com/embed/${ytId}`

  const vmId = extractVimeoId(props.url)
  if (vmId) return `https://player.vimeo.com/video/${vmId}`

  if (props.url?.includes('/embed/')) return props.url
  return ''
})
</script>

<template>
  <div class="aspect-video w-full">
    <iframe v-if="embedUrl" :src="embedUrl" class="w-full h-full rounded"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen></iframe>
    <div v-else class="flex items-center justify-center w-full h-full text-sm text-gray-600 bg-gray-50 border border-gray-200 rounded">
      Không thể nhúng video này. <a v-if="url" :href="url" target="_blank" :style="{ color: COLORS.primary }" class="ml-1 underline">Mở video</a>
    </div>
  </div>
</template>

<style scoped>
</style>


