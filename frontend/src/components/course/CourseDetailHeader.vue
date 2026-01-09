<script setup>
import { computed } from 'vue'
import { BookOpen, ArrowLeft } from 'lucide-vue-next'

const props = defineProps({
  courseDoc: { type: Object, default: () => ({}) },
  courseName: { type: String, default: '' },
  programName: { type: String, default: '' },
  siteUrl: { type: String, default: '' },
  gradients: { type: Object, default: () => ({ primary: '' }) },
  colors: { type: Object, default: () => ({ secondary: '' }) },
  showBackButton: { type: Boolean, default: false },
})

const emit = defineEmits(['back'])

const title = computed(() => props.courseDoc?.name || props.courseName)
const description = computed(() => props.courseDoc?.description || '')
const heroImage = computed(() => props.courseDoc?.hero_image)
</script>

<template>
  <div class="overflow-hidden rounded-lg shadow-xl bg-white">
    <div
      class="relative text-white p-3 md:p-6"
      :style="{ background: gradients.primary }"
    >
      <div
        class="flex flex-col md:flex-row items-start md:items-center justify-between md:justify-between gap-4"
      >
        <div class="flex items-center space-x-3">
          <!-- Back button -->
          <button
            v-if="showBackButton"
            @click="emit('back')"
            class="flex items-center space-x-2 text-white hover:text-gray-200 transition-colors"
          >
            <ArrowLeft class="size-4" />
            <span class="text-sm hidden sm:inline">Quay lại</span>
          </button>
          <div v-if="showBackButton" class="h-4 w-px bg-white/30"></div>
          <div class="p-2 bg-white/20 rounded-lg">
            <BookOpen class="md:size-6 size-4" />
          </div>
          <div>
            <h3 class="md:text-xl text-lg font-bold">{{ title }}</h3>
            <p class="md:text-sm text-xs text-white/90 mt-1">
              <span v-if="programName">{{ programName }}</span>
              <span v-else>Chi tiết Bài học</span>
            </p>
          </div>
        </div>
      </div>
    </div>
    <div class="p-3 md:p-6">
      <div class="flex lg:flex-row flex-col gap-4">
        <div
          v-if="heroImage"
          class="aspect-video md:h-48 h-36 rounded-md overflow-hidden shadow-md ring-2"
          :style="{ ringColor: colors.secondary }"
        >
          <img
            :src="`${siteUrl}${heroImage}`"
            alt="Course Image"
            class="w-full h-full object-cover"
          />
        </div>
        <div
          v-else
          class="aspect-video md:h-48 h-36 rounded-md overflow-hidden shadow-md ring-2"
          :style="{ ringColor: colors.secondary }"
        >
          <img
            src="https://www.placeholderimage.online/placeholder/420/310/ededed/e6e6e6?text=Course&font=Poppins.webp"
            alt="Course Image"
            class="w-full h-full object-cover"
          />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <p v-if="description" class="text-sm text-gray-600 text-justify">
            {{ description }}
          </p>
          <p v-else class="text-sm text-gray-600 text-justify">
            Không có mô tả cho bài học này
          </p>
          <slot name="actions"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
