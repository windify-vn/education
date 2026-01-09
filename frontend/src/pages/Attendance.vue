<template>
  <div class="py-4 flex flex-col">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-16">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- No Student Groups -->
    <div
      v-else-if="!studentGroupsList.length"
      class="flex flex-col items-center justify-center py-16 text-center px-5"
    >
      <Users class="w-16 h-16 text-slate-300 mb-4" />
      <h3 class="text-lg font-semibold text-gray-900 mb-2">Chưa có lớp học</h3>
      <p class="text-sm text-slate-500 max-w-sm">
        Bạn chưa được thêm vào lớp học nào. Vui lòng liên hệ quản trị viên.
      </p>
    </div>

    <!-- Main Content -->
    <template v-else>
      <div class="px-3 md:px-5 flex flex-col sm:flex-row sm:items-center gap-2">
        <h2 class="font-semibold text-2xl truncate">
          {{ selectedProgram }}
        </h2>
        <Dropdown :options="dropdownOptions">
          <template #default="{ open }">
            <Button
              :label="selectedGroupLabel"
              class="truncate max-w-[200px] md:max-w-none"
            >
              <template #suffix>
                <FeatherIcon
                  :name="open ? 'chevron-up' : 'chevron-down'"
                  class="h-4 text-gray-600 flex-shrink-0"
                />
              </template>
            </Button>
          </template>
        </Dropdown>
      </div>
      <div class="h-full">
        <Calendar
          v-if="!attendanceResource.loading && attendanceResource.data"
          :events="attendanceResource.data"
        />
        <Calendar v-else :events="[]" />
      </div>
    </template>

    <Dialog
      v-model="isAttendancePage"
      :options="{
        size: '2xl',
        title: 'Đăng ký xin nghỉ',
      }"
    >
      <template #body-content>
        <NewLeave
          :newLeave="newLeave"
          :program="selectedProgram"
          :studentGroup="selectedGroupLabel"
        />
      </template>
      <template #actions="{ close }">
        <div class="flex flex-row-reverse gap-2">
          <Button
            :disabled="!newLeave.from_date || !newLeave.reason || isSubmitting"
            :loading="isSubmitting"
            variant="solid"
            label="Lưu"
            @click="submitLeave"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { leaveStore } from '@/stores/leave'
import { studentStore } from '@/stores/student'
import {
  Dialog,
  createResource,
  Dropdown,
  FeatherIcon,
  Spinner,
} from 'frappe-ui'
import { storeToRefs } from 'pinia'
import NewLeave from '@/components/attendance/NewLeave.vue'
import Calendar from '@/components/calendar/Calendar.vue'
import { createToast } from '@/utils'
import { Users } from 'lucide-vue-next'

const { getStudentInfo } = studentStore()
const studentInfo = getStudentInfo().value

const { isAttendancePage } = storeToRefs(leaveStore())

const loading = ref(true)
const studentGroupsList = ref([])
const selectedGroup = ref(null)
const isSubmitting = ref(false)

const selectedGroupLabel = computed(() => {
  return selectedGroup.value?.label || 'Chọn lớp học'
})

const selectedProgram = computed(() => {
  return selectedGroup.value?.program || ''
})

const dropdownOptions = computed(() => {
  return studentGroupsList.value.map((group) => ({
    label: group.label,
    onClick: () => selectGroup(group),
  }))
})

function selectGroup(group) {
  if (group.value === selectedGroup.value?.value) return
  selectedGroup.value = group
  loadAttendance()
}

function loadAttendance() {
  if (!selectedGroup.value?.value || !studentInfo?.name) return
  attendanceResource.update({
    params: {
      student_group: selectedGroup.value.value,
      student: studentInfo.name,
    },
  })
  attendanceResource.reload()
}

const studentGroupsResource = createResource({
  url: 'education.education.api.get_student_groups_for_attendance',
  params: {
    student: studentInfo?.name,
  },
  onSuccess: (data) => {
    studentGroupsList.value = data || []
    if (studentGroupsList.value.length > 0) {
      selectedGroup.value = studentGroupsList.value[0]
      loadAttendance()
    }
    loading.value = false
  },
  onError: (err) => {
    console.error('Error loading student groups:', err)
    loading.value = false
  },
})

const attendanceStatus = {
  Present: 'bg-green-100',
  Absent: 'bg-red-200',
  Leave: 'bg-orange-100',
}

const attendanceResource = createResource({
  url: 'education.education.api.get_student_attendance',
  params: {
    student_group: '',
    student: studentInfo?.name,
  },
  transform: (attendance) => {
    attendance = attendance.filter(
      (att, index, self) =>
        index === self.findIndex((t) => t.date === att.date),
    )

    return attendance.map((att) => ({
      name: att.name,
      title: att.status,
      background_color: attendanceStatus[att.status],
      date: att.date,
      status: att.status,
    }))
  },
  onError: (err) => {
    console.error('Error loading attendance:', err)
  },
})

const newLeave = reactive({
  student: studentInfo?.name,
  student_name: studentInfo?.student_name,
  from_date: '',
  to_date: '',
  reason: '',
  total_days: '',
})

function resetLeaveForm() {
  newLeave.from_date = ''
  newLeave.to_date = ''
  newLeave.reason = ''
  newLeave.total_days = ''
}

const applyLeave = createResource({
  url: 'education.education.api.apply_leave',
  onSuccess: () => {
    if (!isSubmitting.value) return // Guard against duplicate calls
    isSubmitting.value = false
    isAttendancePage.value = false
    attendanceResource.reload()
    createToast({
      title: 'Đăng ký nghỉ phép thành công',
      icon: 'check',
      iconClasses: 'text-green-600',
    })
    resetLeaveForm()
  },
  onError: (err) => {
    if (!isSubmitting.value) return // Guard against duplicate calls
    isSubmitting.value = false
    let errorMessage = 'Có lỗi xảy ra'

    // Try to parse _server_messages first (Frappe format)
    if (err._server_messages) {
      try {
        const serverMessages = JSON.parse(err._server_messages)
        if (serverMessages.length > 0) {
          const firstMessage = JSON.parse(serverMessages[0])
          errorMessage = firstMessage.message || errorMessage
        }
      } catch (e) {
        // Fallback to other error formats
      }
    }

    // Fallback to messages array or exception
    if (errorMessage === 'Có lỗi xảy ra') {
      errorMessage = err.messages?.[0] || err.exception || errorMessage
    }

    createToast({
      title: errorMessage,
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  },
})

function submitLeave() {
  // Prevent double submit
  if (isSubmitting.value || applyLeave.loading) return

  if (!selectedProgram.value) {
    createToast({
      title: 'Vui lòng chọn lớp học',
      icon: 'x',
      iconClasses: 'text-red-600',
    })
    return
  }

  isSubmitting.value = true
  applyLeave.submit({
    leave_data: { ...newLeave },
    program_name: selectedProgram.value,
    student_group: selectedGroup.value?.value, // Pass selected student group
  })
}

onMounted(() => {
  if (studentInfo?.name) {
    studentGroupsResource.submit()
  } else {
    loading.value = false
  }
})
</script>
