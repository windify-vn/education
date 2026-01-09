<template>
  <div
    class="col-span-1 overflow-hidden rounded-lg shadow-xl text-white p-4 flex flex-col md:flex-row gap-4 items-center md:items-start"
    style="
      background: linear-gradient(
        90deg,
        rgb(242, 90, 35) 0%,
        rgb(241, 146, 85) 100%
      );
    "
  >
    <!-- Avatar: smaller on mobile, larger on tablet/desktop -->
    <div
      class="size-28 sm:size-40 md:size-56 aspect-square rounded-lg overflow-hidden bg-gray-200 flex-shrink-0"
    >
      <img
        v-if="studentInfo?.image?.length > 0"
        :src="studentInfo?.image"
        class="size-28 sm:size-40 md:size-56 aspect-square object-cover bg-transparent"
      />
      <div
        v-else
        class="size-28 sm:size-40 md:size-56 aspect-square grid place-items-center text-[24px] font-semibold text-slate-500"
      >
        {{ firstInitial }}
      </div>
    </div>
    <!-- Info: centered on mobile, left-aligned on desktop -->
    <div class="min-w-0 text-center md:text-left">
      <div
        class="text-[22px] sm:text-[28px] md:text-[40px] font-extrabold truncate"
      >
        {{ studentInfo?.student_name }}
      </div>
      <div class="flex flex-col gap-1 items-center md:items-start">
        <span class="py-1 text-white/90 text-sm">{{ user?.data?.email }}</span>
        <p
          class="px-4 py-1 text-xl font-semibold rounded w-fit"
          style="background: linear-gradient(90deg, #224773 0%, #4086d9 100%)"
        >
          Học viên
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  studentInfo: { type: Object, default: () => ({}) },
  user: { type: Object, default: () => ({}) },
})

const firstInitial = computed(() => {
  const name =
    props.studentInfo?.student_name || props.user?.data?.student_name || ''
  return name.trim().charAt(0).toUpperCase()
})
</script>

<style scoped></style>
