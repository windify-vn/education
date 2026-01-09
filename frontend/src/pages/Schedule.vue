<template>
  <div class="w-full h-full">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-16">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Program Enrolled -->
    <div
      v-else-if="!hasProgram"
      class="flex flex-col items-center justify-center py-16 text-center"
    >
      <CalendarX class="w-16 h-16 text-slate-300 mb-4" />
      <h3 class="text-lg font-semibold text-gray-900 mb-2">Chưa có lịch học</h3>
      <p class="text-sm text-slate-500 max-w-sm">
        Bạn chưa được đăng ký vào chương trình học nào. Vui lòng liên hệ quản
        trị viên.
      </p>
    </div>

    <!-- Calendar -->
    <Calendar v-else :events="events" />
  </div>
</template>

<script setup>
import Calendar from '@/components/calendar/Calendar.vue'
import { call, Spinner } from 'frappe-ui'
import { ref, watch, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { studentStore } from '@/stores/student'
import { CalendarX } from 'lucide-vue-next'

const store = studentStore()
const { currentPrograms, studentGroups } = storeToRefs(store)
const events = ref([])
const loading = ref(false)

const hasProgram = computed(() => {
  return currentPrograms.value?.length > 0 && studentGroups.value?.length > 0
})

// Fetch schedule for ALL programs
async function fetchAllSchedules() {
  if (!currentPrograms.value?.length || !studentGroups.value?.length) {
    return
  }

  loading.value = true
  try {
    // Fetch schedule for each program
    const promises = currentPrograms.value.map((program) =>
      call('education.education.api.get_course_schedule_for_student', {
        program_name: program.program,
        student_groups: studentGroups.value,
      }),
    )

    const results = await Promise.all(promises)

    // Merge all schedules
    const allSchedules = []
    results.forEach((response) => {
      if (response) {
        response.forEach((classSchedule) => {
          allSchedules.push({
            title: classSchedule.title,
            with: classSchedule.instructor,
            name: classSchedule.name,
            room: classSchedule.room_name || classSchedule.room, // Use room_name if available
            date: classSchedule.schedule_date,
            from_time: classSchedule.from_time.split('.')[0],
            to_time: classSchedule.to_time.split('.')[0],
            color: classSchedule.class_schedule_color,
          })
        })
      }
    })

    events.value = allSchedules
  } catch (error) {
    console.error('Failed to fetch schedules:', error)
  } finally {
    loading.value = false
  }
}

// Watch for when student data is loaded
watch(
  [currentPrograms, studentGroups],
  ([programs, groups]) => {
    if (programs?.length > 0 && groups?.length > 0) {
      fetchAllSchedules()
    }
  },
  { immediate: true, deep: true },
)
</script>
