<template>
  <div class="flex flex-col gap-5">
    <!-- Học sinh (readonly) -->
    <div>
      <label class="mb-2 block text-sm font-medium text-gray-700">
        Học sinh
      </label>
      <div
        class="flex items-center gap-3 px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-lg"
      >
        <div
          class="w-8 h-8 bg-[#F25A23]/10 rounded-full flex items-center justify-center"
        >
          <User class="w-4 h-4 text-[#F25A23]" />
        </div>
        <span class="text-gray-900 font-medium">
          {{ newLeave.student_name || newLeave.student }}
        </span>
      </div>
    </div>

    <!-- Program và Student Group (readonly) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="mb-2 block text-sm font-medium text-gray-700">
          Chương trình
        </label>
        <div
          class="flex items-center gap-2 px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-lg"
        >
          <BookOpen class="w-4 h-4 text-gray-400" />
          <span class="text-gray-700 text-sm">{{ program || '—' }}</span>
        </div>
      </div>
      <div>
        <label class="mb-2 block text-sm font-medium text-gray-700">
          Nhóm học
        </label>
        <div
          class="flex items-center gap-2 px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-lg"
        >
          <Users class="w-4 h-4 text-gray-400" />
          <span class="text-gray-700 text-sm">{{ studentGroup || '—' }}</span>
        </div>
      </div>
    </div>

    <!-- Ngày nghỉ -->
    <div>
      <label class="mb-2 block text-sm font-medium text-gray-700">
        Ngày nghỉ <span class="text-red-500">*</span>
      </label>
      <DatePicker
        v-model="leaveDate"
        placeholder="Chọn ngày nghỉ"
        :future-only="true"
        :error="dateError"
        @change="onDateChange"
      />
    </div>

    <!-- Lý do (đặt cuối) -->
    <div>
      <label class="mb-2 block text-sm font-medium text-gray-700">
        Lý do <span class="text-red-500">*</span>
      </label>
      <textarea
        v-model="newLeave.reason"
        placeholder="Nhập lý do xin nghỉ..."
        rows="3"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#F25A23]/20 focus:border-[#F25A23] transition-all duration-200 resize-none"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import dayjs from 'dayjs'
import DatePicker from '@/components/common/DatePicker.vue'
import { User, BookOpen, Users } from 'lucide-vue-next'

const props = defineProps({
  newLeave: {
    type: Object,
    required: true,
  },
  program: {
    type: String,
    default: '',
  },
  studentGroup: {
    type: String,
    default: '',
  },
})

const { newLeave } = props
const leaveDate = ref(newLeave.from_date || '')
const dateError = ref('')

function onDateChange(selectedDate) {
  leaveDate.value = selectedDate
  dateError.value = ''

  if (selectedDate) {
    const selected = dayjs(selectedDate)
    const today = dayjs().startOf('day')

    if (selected.isBefore(today)) {
      dateError.value = 'Ngày nghỉ phải từ hôm nay trở đi'
      newLeave.from_date = ''
      newLeave.to_date = ''
      newLeave.total_days = ''
      return
    }

    newLeave.from_date = selectedDate
    newLeave.to_date = selectedDate
    newLeave.total_days = 1
  } else {
    newLeave.from_date = ''
    newLeave.to_date = ''
    newLeave.total_days = ''
  }
}

watch(
  () => newLeave.from_date,
  (val) => {
    if (val !== leaveDate.value) {
      leaveDate.value = val
      dateError.value = ''
    }
  },
)
</script>
