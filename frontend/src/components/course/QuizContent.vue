<script setup>
defineProps({
  content: {
    type: Object,
    default: () => ({})
  }
})
</script>

<template>
  <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
    <div class="text-lg font-semibold text-green-800 mb-2">
      {{ content?.title || 'Bài kiểm tra' }}
    </div>
    <p class="text-green-700">Chuẩn bị cho bài kiểm tra này</p>
  </div>
</template>
