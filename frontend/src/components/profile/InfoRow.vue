<template>
  <div>
    <div class="flex justify-between gap-4 text-sm">
      <div class="flex gap-2">
        <slot name="icon" />
        <h3 class="font-semibold shrink-0">{{ label }}:</h3>
      </div>
      <span
        class="cursor-pointer hover:underline"
        :title="'Click để sao chép'"
        @click="copyToClipboard"
      >
        {{ value }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { createToast } from '@/utils'
const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    default: '',
  },
})

function copyToClipboard() {
  const text = props.value == null ? '' : String(props.value)
  console.debug('[InfoRow] copyToClipboard', { text })
  if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(onCopied).catch(() => {})
  } else {
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.left = '-9999px'
    document.body.appendChild(textarea)
    textarea.focus()
    textarea.select()
    try {
      document.execCommand('copy')
      onCopied()
    } catch (e) {}
    document.body.removeChild(textarea)
  }
}

function onCopied() {
  createToast({
    title: 'Đã sao chép',
    message: String(props.value ?? ''),
    icon: 'clipboard',
    iconClasses: 'text-[#224773]',
  })
}
</script>

<style scoped></style>

